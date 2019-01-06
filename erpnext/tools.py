# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import frappe, os , math
from frappe.model.document import Document
from frappe.utils import get_site_base_path
from frappe.utils.data import flt, nowdate, getdate, cint
from frappe.utils.csvutils import read_csv_content_from_uploaded_file
from frappe.utils.password import update_password as _update_password
from frappe.utils import cint, cstr, flt, nowdate, comma_and, date_diff, getdate
import datetime
from datetime import date
from dateutil.relativedelta import relativedelta


def save_attendance():
    length=frappe.db.sql("select count(name) from `tabAttendance` where name='ATT-00001'")
    emp=frappe.db.sql("select name from `tabAttendance` where name='ATT-00001'")

    for i in range(length[0][0]):
        doc = frappe.get_doc('Attendance', emp[i][0] )
        doc.save()
        print(i)






def add_items():
    from frappe.utils.csvutils import read_csv_content
    from frappe.core.doctype.data_import.importer import upload
    with open("/home/frappe/frappe-bench/apps/erpnext/erpnext/items.csv", "r") as infile:   
        rows = read_csv_content(infile.read())
        for index, row in enumerate(rows):
            print(index)
            if row[5]:
                frappe.get_doc({
                        "doctype":"Item",
                        "item_code": row[0],
                        "item_name": row[1],
                        "is_stock_item": 1,
                        "hub_warehouse": row[2],
                        "item_defaults": [
                                  {
                                    "doctype": "Item Default",
                                    "company": "aldaan",
                                    "default_warehouse": row[2],
                                    "income_account": "411 - gross sales - إجمالي المبيعات - A"
                                  }
                                ],
                        "item_group": row[3],
                        "stock_uom": row[4],
                        "sales_uom": row[4],
                        "uoms": [
                                  {
                                    "doctype": "UOM Conversion Detail",
                                    "uom": row[5],
                                    "conversion_factor": 1
                                  }
                                ],
                        "common_code": row[6],
                        "common_name": row[7],
                        "valuation_rate": row[8]
                    }).insert(ignore_permissions=True)
            else:
                frappe.get_doc({
                        "doctype":"Item",
                        "item_code": row[0],
                        "item_name": row[1],
                        "is_stock_item": 1,
                        "hub_warehouse": row[2],
                        "item_defaults": [
                                  {
                                    "doctype": "Item Default",
                                    "company": "aldaan",
                                    "default_warehouse": row[2],
                                    "income_account": "411 - gross sales - إجمالي المبيعات - A"
                                  }
                                ],
                        "item_group": row[3],
                        "stock_uom": row[4],
                        "sales_uom": row[4],
                        "common_code": row[6],
                        "common_name": row[7],
                        "valuation_rate": row[8]
                    }).insert(ignore_permissions=True)


            if row[8]:
                frappe.get_doc({
                        "doctype":"Item Price",
                        "item_code": row[0],
                        "price_list": "Standard Buying",
                        "price_list_rate": row[8]
                    }).insert(ignore_permissions=True)

            
