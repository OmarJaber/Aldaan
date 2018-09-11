# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
import frappe.defaults
from frappe import msgprint, _
from frappe.model.naming import set_name_by_naming_series
from frappe.contacts.address_and_contact import load_address_and_contact, delete_contact_and_address
from erpnext.utilities.transaction_base import TransactionBase
from erpnext.accounts.party import validate_party_accounts, get_dashboard_info, get_timeline_data # keep this


class Supplier(TransactionBase):
	def get_feed(self):
		return self.supplier_name

	def onload(self):
		"""Load address and contacts in `__onload`"""
		load_address_and_contact(self)
		self.load_dashboard_info()

	def before_save(self):
		if not self.on_hold:
			self.hold_type = ''
			self.release_date = ''
		elif self.on_hold and not self.hold_type:
			self.hold_type = 'All'

	def load_dashboard_info(self):
		info = get_dashboard_info(self.doctype, self.name)
		self.set_onload('dashboard_info', info)

	def autoname(self):
		supp_master_name = frappe.defaults.get_global_default('supp_master_name')
		if supp_master_name == 'Supplier Name':
			self.name = self.supplier_name
		else:
			set_name_by_naming_series(self)

	def on_update(self):
		if not self.naming_series:
			self.naming_series = ''

	def validate(self):
		# validation for Naming Series mandatory field...
		if frappe.defaults.get_global_default('supp_master_name') == 'Naming Series':
			if not self.naming_series:
				msgprint(_("Series is mandatory"), raise_exception=1)

		validate_party_accounts(self)
		if self.add_account:
			self.add_supplier_account()


	def add_supplier_account(self):
        supplier_account_name_english = str(self.supplier_name)
        supplier_account_name_arabic = str(self.supplier_name_in_arabic)

        accounts = frappe.db.sql("select account_name from `tabAccount` where parent_account='21111 - Suppliers - الموردين - A' and account_name like '%{0}%' ".format(supplier_account_name_english))
        if not accounts:
            curr_account_number = 0
            account_number = frappe.db.sql("select account_number from `tabAccount` where parent_account='21111 - Suppliers - الموردين - A' order by creation desc limit 1") 
            if account_number:
                curr_account_number= str(int(account_number[0][0][5:])+int(1))
            else:
                curr_account_number= '001'

            supplier_account_name = "{0} - {1}".format(supplier_account_name_english, supplier_account_name_arabic)

            frappe.get_doc({
                "doctype": "Account",
                "account_name": str(supplier_account_name),
                "account_number": '21111'+str(curr_account_number.zfill(3)),
                "parent_account": '21111 - Suppliers - الموردين - A',
                # "balance_must_be": 'Debit',
                "is_group": 0
            }).save(ignore_permissions = True)
            
            acc_name = frappe.get_list("Account", filters={"account_name": str(supplier_account_name) }, fields=["name"])
            self.advances_account = str(acc_name[0]['name'])
            frappe.msgprint("Supplier Account for {0} was successfully made".format(supplier_account_name_english))


	def on_trash(self):
		delete_contact_and_address('Supplier', self.name)

	def after_rename(self, olddn, newdn, merge=False):
		if frappe.defaults.get_global_default('supp_master_name') == 'Supplier Name':
			frappe.db.set(self, "supplier_name", newdn)
