# -*- coding: utf-8 -*-
# Copyright (c) 2017, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe, json
from frappe import msgprint, _
from frappe.model.document import Document
from erpnext.manufacturing.doctype.bom.bom import validate_bom_no
from frappe.utils import cstr, flt, cint, nowdate, add_days, comma_and, now_datetime
from erpnext.manufacturing.doctype.work_order.work_order import get_item_details
from six import string_types

class ProductionPlan(Document):
	def validate(self):
		self.calculate_total_planned_qty()
		self.set_status()

	def validate_data(self):
		for d in self.get('po_items'):
			if not d.bom_no:
				frappe.throw(_("Please select BOM for Item in Row {0}".format(d.idx)))
			else:
				validate_bom_no(d.item_code, d.bom_no)

			if not flt(d.planned_qty):
				frappe.throw(_("Please enter Planned Qty for Item {0} at row {1}").format(d.item_code, d.idx))

	def get_open_sales_orders(self):
		""" Pull sales orders  which are pending to deliver based on criteria selected"""
		open_so = get_sales_orders(self)

		if open_so:
			self.add_so_in_table(open_so)
		else:
			frappe.msgprint(_("Sales orders are not available for production"))

	def add_so_in_table(self, open_so):
		""" Add sales orders in the table"""
		self.set('sales_orders', [])

		for data in open_so:
			self.append('sales_orders', {
				'sales_order': data.name,
				'sales_order_date': data.transaction_date,
				'customer': data.customer,
				'grand_total': data.grand_total
			})

	def get_pending_material_requests(self):
		""" Pull Material Requests that are pending based on criteria selected"""
		mr_filter = item_filter = ""
		if self.from_date:
			mr_filter += " and mr.transaction_date >= %(from_date)s"
		if self.to_date:
			mr_filter += " and mr.transaction_date <= %(to_date)s"
		if self.warehouse:
			mr_filter += " and mr_item.warehouse = %(warehouse)s"

		if self.item_code:
			item_filter += " and mr_item.item_code = %(item)s"

		pending_mr = frappe.db.sql("""
			select distinct mr.name, mr.transaction_date
			from `tabMaterial Request` mr, `tabMaterial Request Item` mr_item
			where mr_item.parent = mr.name
				and mr.material_request_type = "Manufacture"
				and mr.docstatus = 1 and mr.company = %(company)s
				and mr_item.qty > ifnull(mr_item.ordered_qty,0) {0} {1}
				and (exists (select name from `tabBOM` bom where bom.item=mr_item.item_code
					and bom.is_active = 1))
			""".format(mr_filter, item_filter), {
				"from_date": self.from_date,
				"to_date": self.to_date,
				"warehouse": self.warehouse,
				"item": self.item_code,
				"company": self.company
			}, as_dict=1)

		self.add_mr_in_table(pending_mr)

	def add_mr_in_table(self, pending_mr):
		""" Add Material Requests in the table"""
		self.set('material_requests', [])

		for data in pending_mr:
			self.append('material_requests', {
				'material_request': data.name,
				'material_request_date': data.transaction_date
			})

	def get_items(self):
		if self.get_items_from == "Sales Order":
			self.get_so_items()
		elif self.get_items_from == "Material Request":
			self.get_mr_items()

	def get_so_items(self):
		so_list = [d.sales_order for d in self.sales_orders if d.sales_order]
		if not so_list:
			msgprint(_("Please enter Sales Orders in the above table"))
			return []

		item_condition = ""
		if self.item_code:
			item_condition = ' and so_item.item_code = "{0}"'.format(frappe.db.escape(self.item_code))

		items = frappe.db.sql("""select distinct parent, item_code, warehouse,
			(qty - work_order_qty) * conversion_factor as pending_qty, name
			from `tabSales Order Item` so_item
			where parent in (%s) and docstatus = 1 and qty > work_order_qty
			and exists (select name from `tabBOM` bom where bom.item=so_item.item_code
					and bom.is_active = 1) %s""" % \
			(", ".join(["%s"] * len(so_list)), item_condition), tuple(so_list), as_dict=1)

		if self.item_code:
			item_condition = ' and so_item.item_code = "{0}"'.format(frappe.db.escape(self.item_code))

		packed_items = frappe.db.sql("""select distinct pi.parent, pi.item_code, pi.warehouse as warehouse,
			(((so_item.qty - so_item.work_order_qty) * pi.qty) / so_item.qty)
				as pending_qty, pi.parent_item, so_item.name
			from `tabSales Order Item` so_item, `tabPacked Item` pi
			where so_item.parent = pi.parent and so_item.docstatus = 1
			and pi.parent_item = so_item.item_code
			and so_item.parent in (%s) and so_item.qty > so_item.work_order_qty
			and exists (select name from `tabBOM` bom where bom.item=pi.item_code
					and bom.is_active = 1) %s""" % \
			(", ".join(["%s"] * len(so_list)), item_condition), tuple(so_list), as_dict=1)

		self.add_items(items + packed_items)
		self.calculate_total_planned_qty()

	def get_mr_items(self):
		mr_list = [d.material_request for d in self.material_requests if d.material_request]
		if not mr_list:
			msgprint(_("Please enter Material Requests in the above table"))
			return []

		item_condition = ""
		if self.item_code:
			item_condition = " and mr_item.item_code ='{0}'".format(frappe.db.escape(self.item_code))

		items = frappe.db.sql("""select distinct parent, name, item_code, warehouse,
			(qty - ordered_qty) as pending_qty
			from `tabMaterial Request Item` mr_item
			where parent in (%s) and docstatus = 1 and qty > ordered_qty
			and exists (select name from `tabBOM` bom where bom.item=mr_item.item_code
				and bom.is_active = 1) %s""" % \
			(", ".join(["%s"] * len(mr_list)), item_condition), tuple(mr_list), as_dict=1)

		self.add_items(items)
		self.calculate_total_planned_qty()

	def add_items(self, items):
		self.set('po_items', [])
		for data in items:
			item_details = get_item_details(data.item_code)
			pi = self.append('po_items', {
				'include_exploded_items': 1,
				'warehouse': data.warehouse,
				'item_code': data.item_code,
				'description': item_details and item_details.description or '',
				'stock_uom': item_details and item_details.stock_uom or '',
				'bom_no': item_details and item_details.bom_no or '',
				'planned_qty': data.pending_qty,
				'pending_qty': data.pending_qty,
				'planned_start_date': now_datetime(),
				'product_bundle_item': data.parent_item
			})

			if self.get_items_from == "Sales Order":
				pi.sales_order = data.parent
				pi.sales_order_item = data.name

			elif self.get_items_from == "Material Request":
				pi.material_request = data.parent
				pi.material_request_item = data.name

	def calculate_total_planned_qty(self):
		self.total_planned_qty = 0
		for d in self.po_items:
			self.total_planned_qty += flt(d.planned_qty)

	def calculate_total_produced_qty(self):
		self.total_produced_qty = 0
		for d in self.po_items:
			self.total_produced_qty += flt(d.produced_qty)

		self.db_set("total_produced_qty", self.total_produced_qty, update_modified=False)

	def update_produced_qty(self, produced_qty, production_plan_item):
		for data in self.po_items:
			if data.name == production_plan_item:
				data.produced_qty = produced_qty
				data.db_update()

		self.calculate_total_produced_qty()
		self.set_status()
		self.db_set('status', self.status)

	def on_cancel(self):
		self.db_set('status', 'Cancelled')
		self.delete_draft_work_order()

	def delete_draft_work_order(self):
		for d in frappe.get_all('Work Order', fields = ["name"],
			filters = {'docstatus': 0, 'production_plan': ("=", self.name)}):
			frappe.delete_doc('Work Order', d.name)

	def set_status(self):
		self.status = {
			'0': 'Draft',
			'1': 'Submitted'
		}[cstr(self.docstatus or 0)]

		if self.total_produced_qty > 0:
			self.status = "In Process"
			if self.total_produced_qty == self.total_planned_qty:
				self.status = "Completed"

		if self.status != 'Completed':
			self.update_ordered_status()
			self.update_requested_status()

	def update_ordered_status(self):
		update_status = False
		for d in self.po_items:
			if d.planned_qty == d.ordered_qty:
				update_status = True

		if update_status and self.status != 'Completed':
			self.status = 'In Process'

	def update_requested_status(self):
		if not self.mr_items:
			return

		update_status = True
		for d in self.mr_items:
			if d.quantity != d.requested_qty:
				update_status = False

		if update_status:
			self.status = 'Material Requested'

	def get_production_items(self):
		item_dict = {}
		for d in self.po_items:
			item_details= {
				"production_item"		: d.item_code,
				"use_multi_level_bom"   : d.include_exploded_items,
				"sales_order"			: d.sales_order,
				"sales_order_item"		: d.sales_order_item,
				"material_request"		: d.material_request,
				"material_request_item"	: d.material_request_item,
				"bom_no"				: d.bom_no,
				"description"			: d.description,
				"stock_uom"				: d.stock_uom,
				"company"				: self.company,
				"fg_warehouse"			: d.warehouse,
				"production_plan"       : self.name,
				"production_plan_item"  : d.name,
				"product_bundle_item"	: d.product_bundle_item
			}

			item_details.update({
				"project": self.project or frappe.db.get_value("Sales Order", d.sales_order, "project")
			})

			if self.get_items_from == "Material Request":
				item_details.update({
					"qty": d.planned_qty
				})
				item_dict[(d.item_code, d.material_request_item, d.warehouse)] = item_details
			else:
				item_details.update({
					"qty":flt(item_dict.get((d.item_code, d.sales_order, d.warehouse),{})
						.get("qty")) + flt(d.planned_qty)
				})
				item_dict[(d.item_code, d.sales_order, d.warehouse)] = item_details

		return item_dict
		
	def get_items_for_material_requests(self):
		self.mr_items = []

		for data in self.po_items:
			bom_wise_item_details = {}
			if not data.planned_qty:
				frappe.throw(_("For row {0}: Enter planned qty").format(data.idx))

			if data.include_exploded_items and data.bom_no and self.include_subcontracted_items:
				for d in frappe.db.sql("""select bei.item_code, item.default_bom as bom,
						ifnull(sum(bei.stock_qty/ifnull(bom.quantity, 1)), 0) as qty, item.item_name,
						bei.description, bei.stock_uom, item.min_order_qty, bei.source_warehouse,
						item.default_material_request_type, item.min_order_qty, item_default.default_warehouse
					from
						`tabBOM Explosion Item` bei 
						JOIN `tabBOM` bom ON bom.name = bei.parent
						JOIN `tabItem` item ON item.name = bei.item_code
						LEFT JOIN `tabItem Default` item_default
							ON item_default.parent = item.name and item_default.company=%s
					where
						bei.docstatus < 2 
						and bom.name=%s and item.is_stock_item in (1, {0})
					group by bei.item_code, bei.stock_uom""".format(self.include_non_stock_items),
					(self.company, data.bom_no), as_dict=1):
						bom_wise_item_details.setdefault(d.item_code, d)
			else:
				bom_wise_item_details = self.get_subitems(data, bom_wise_item_details, data.bom_no, 1)

			for item, item_details in bom_wise_item_details.items():
				if item_details.qty > 0:
					self.add_item_in_material_request_items(item, item_details, data)

	def get_subitems(self, data, bom_wise_item_details, bom_no, parent_qty):
		items = frappe.db.sql("""
			SELECT
				bom_item.item_code, default_material_request_type, item.item_name,
				ifnull(%(parent_qty)s * sum(bom_item.stock_qty/ifnull(bom.quantity, 1)), 0) as qty,
				item.is_sub_contracted_item as is_sub_contracted, bom_item.source_warehouse,
				item.default_bom as default_bom, bom_item.description as description,
				bom_item.stock_uom as stock_uom, item.min_order_qty as min_order_qty,
				item_default.default_warehouse
			FROM
				`tabBOM Item` bom_item
				JOIN `tabBOM` bom ON bom.name = bom_item.parent
				JOIN tabItem item ON bom_item.item_code = item.name
				LEFT JOIN `tabItem Default` item_default
					ON item.name = item_default.parent and item_default.company = %(company)s
			where
				bom.name = %(bom)s
				and bom_item.docstatus < 2
				and item.is_stock_item in (1, {0})
			group by bom_item.item_code""".format(self.include_non_stock_items),{
				'bom': bom_no,
				'parent_qty': parent_qty,
				'company': self.company
			}, as_dict=1)

		for d in items:
			if not data.include_exploded_items or not d.default_bom:
				if d.item_code in bom_wise_item_details:
					bom_wise_item_details[d.item_code].qty = bom_wise_item_details[d.item_code].qty + d.qty
				else:
					bom_wise_item_details[d.item_code] = d

			if data.include_exploded_items and d.default_bom:
				if ((d.default_material_request_type in ["Manufacture", "Purchase"] and
					not d.is_sub_contracted) or (d.is_sub_contracted and self.include_subcontracted_items)):
					if d.qty > 0:
						self.get_subitems(data, bom_wise_item_details, d.default_bom, d.qty)

		return bom_wise_item_details

	def add_item_in_material_request_items(self, item, row, data):
		total_qty = row.qty * data.planned_qty
		projected_qty, actual_qty = get_bin_details(row)

		requested_qty = 0
		if self.ignore_existing_ordered_qty:
			requested_qty = total_qty
		else:
			requested_qty = total_qty - projected_qty

		if requested_qty > 0 and requested_qty < row.min_order_qty:
			requested_qty = row.min_order_qty

		if requested_qty > 0:
			self.append('mr_items', {
				'item_code': item,
				'item_name': row.item_name,
				'quantity': requested_qty,
				'warehouse': row.source_warehouse or row.default_warehouse,
				'actual_qty': actual_qty,
				'min_order_qty': row.min_order_qty,
				'sales_order': data.sales_order
			})

	def make_work_order(self):
		wo_list = []
		self.validate_data()
		items_data = self.get_production_items()

		for key, item in items_data.items():
			work_order = self.create_work_order(item)
			if work_order:
				wo_list.append(work_order)

		frappe.flags.mute_messages = False

		if wo_list:
			wo_list = ["""<a href="#Form/Work Order/%s" target="_blank">%s</a>""" % \
				(p, p) for p in wo_list]
			msgprint(_("{0} created").format(comma_and(wo_list)))
		else :
			msgprint(_("No Work Orders created"))

	def create_work_order(self, item):
		from erpnext.manufacturing.doctype.work_order.work_order import OverProductionError, get_default_warehouse
		warehouse = get_default_warehouse()
		wo = frappe.new_doc("Work Order")
		wo.update(item)
		wo.set_work_order_operations()

		if not wo.fg_warehouse:
			wo.fg_warehouse = warehouse.get('fg_warehouse')
		try:
			wo.insert()
			return wo.name
		except OverProductionError:
			pass

	def make_material_request(self):
		material_request_list = []

		item_details = self.get_itemwise_qty()
		for item_code, rows in item_details.items():
			item_doc = frappe.get_doc("Item", item_code)
			schedule_date = add_days(nowdate(), cint(item_doc.lead_time_days))

			material_request = frappe.new_doc("Material Request")
			material_request.update({
				"transaction_date": nowdate(),
				"status": "Draft",
				"company": self.company,
				"requested_by": frappe.session.user,
				"schedule_date": schedule_date,
				'material_request_type': item_doc.default_material_request_type
			})

			for idx in rows:
				child = self.mr_items[cint(idx)-1]
				material_request.append("items", {
					"item_code": item_code,
					"qty": child.quantity,
					"schedule_date": schedule_date,
					"warehouse": child.warehouse,
					"sales_order": child.sales_order,
					'production_plan': self.name,
					'material_request_plan_item': child.name,
					"project": frappe.db.get_value("Sales Order", child.sales_order, "project") \
						if child.sales_order else None
				})

			material_request.flags.ignore_permissions = 1
			material_request.run_method("set_missing_values")
			material_request.submit()
			material_request_list.append(material_request.name)
		
		frappe.flags.mute_messages = False

		if material_request_list:
			material_request_list = ["""<a href="#Form/Material Request/%s" target="_blank">%s</a>""" % \
				(p, p) for p in material_request_list]
			msgprint(_("{0} created").format(comma_and(material_request_list)))
		else :
			msgprint(_("No material request created"))

	def get_itemwise_qty(self):
		item_details = {}
		for data in self.get('mr_items'):
			if data.item_code in item_details:
				item_details[data.item_code].append(data.idx)
			else:
				item_details.setdefault(data.item_code, [data.idx])

		return item_details

def get_sales_orders(self):
	so_filter = item_filter = ""
	if self.from_date:
		so_filter += " and so.transaction_date >= %(from_date)s"
	if self.to_date:
		so_filter += " and so.transaction_date <= %(to_date)s"
	if self.customer:
		so_filter += " and so.customer = %(customer)s"
	if self.project:
		so_filter += " and so.project = %(project)s"

	if self.item_code:
		item_filter += " and so_item.item_code = %(item)s"

	open_so = frappe.db.sql("""
		select distinct so.name, so.transaction_date, so.customer, so.base_grand_total
		from `tabSales Order` so, `tabSales Order Item` so_item
		where so_item.parent = so.name
			and so.docstatus = 1 and so.status not in ("Stopped", "Closed")
			and so.company = %(company)s
			and so_item.qty > so_item.work_order_qty {0} {1}
			and (exists (select name from `tabBOM` bom where bom.item=so_item.item_code
					and bom.is_active = 1)
				or exists (select name from `tabPacked Item` pi
					where pi.parent = so.name and pi.parent_item = so_item.item_code
						and exists (select name from `tabBOM` bom where bom.item=pi.item_code
							and bom.is_active = 1)))
		""".format(so_filter, item_filter), {
			"from_date": self.from_date,
			"to_date": self.to_date,
			"customer": self.customer,
			"project": self.project,
			"item": self.item_code,
			"company": self.company
		}, as_dict=1)

	return open_so

@frappe.whitelist()
def get_bin_details(row):
	if isinstance(row, string_types):
		row = frappe._dict(json.loads(row))

	conditions = ""
	warehouse = row.source_warehouse or row.default_warehouse or row.warehouse
	if warehouse:
		conditions = " and warehouse='{0}'".format(frappe.db.escape(warehouse))

	item_projected_qty = frappe.db.sql(""" select ifnull(sum(projected_qty),0) as projected_qty,
		ifnull(sum(actual_qty),0) as actual_qty from `tabBin` 
		where item_code = %(item_code)s {conditions}
	""".format(conditions=conditions), { "item_code": row.item_code }, as_list=1)

	return item_projected_qty and item_projected_qty[0] or (0,0)
