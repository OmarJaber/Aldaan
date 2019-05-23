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



def add_show_expert_accounts():
    from frappe.utils.csvutils import read_csv_content
    from frappe.core.doctype.data_import.importer import upload
    with open("/home/frappe/frappe-bench/apps/erpnext/erpnext/show_expert_account_tree.csv", "r") as infile:   
        rows = read_csv_content(infile.read())
        i = 0
        for index, row in enumerate(rows):
            parent = str(row[1])+' - '+str(row[0])+' - '+str(row[2])+' - S'
            account_name = str(row[3])+' - '+str(row[5])
            print(parent)
            if row[7]==1:
                frappe.get_doc({
                  "doctype":"Account",
                  "account_name": account_name,
                  "account_number": row[4],
                  "is_group": row[7],
                  "root_type": row[6]
                }).insert(ignore_permissions=True)
            else:
                frappe.get_doc({
                  "doctype":"Account",
                  "account_name": account_name,
                  "account_number": row[4],
                  "is_group": row[7]
                }).insert(ignore_permissions=True)
            
            i+=1

        print('*************')
        print(i)
        print('*************')




def tst_api():
    from bidi.algorithm import get_display

    import arabic_reshaper

    from bidi.algorithm import get_display

    from num2words import num2words

    print(num2words(1606,lang='ar'))
    print(arabic_reshaper.reshape(num2words(1606,lang='ar')))
    print(get_display(arabic_reshaper.reshape(num2words(1606,lang='ar'))))


def add_entitlment():
    employees=frappe.db.sql("select name from `tabEmployee`")
    for emp in employees:
        print(emp[0])
        entitlement=frappe.db.sql("select name from `tabEntitlement Type`")
        for i in entitlement:
            doc = frappe.get_doc('Employee', emp[0] )
            doc.append('employee_entitlement', {"entitlement_type": i[0]})
            doc.flags.ignore_mandatory = True
            doc.save(ignore_permissions = True)





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

            
