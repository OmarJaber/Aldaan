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





def add_primacasa_supplier():
    from frappe.utils.csvutils import read_csv_content
    from frappe.core.doctype.data_import.importer import upload
    with open("/home/frappe/frappe-bench/apps/erpnext/erpnext/primacasa_items.csv", "r") as infile:   
        rows = read_csv_content(infile.read())
        i = 0
        for index, row in enumerate(rows):
            if row[10]:

                if not frappe.db.exists("Supplier", {"supplier_name": row[10]}):

                    print(str(row[10][0:5])+' '+str(row[10][6:]))

                    frappe.get_doc({
                        "doctype":"Supplier",
                        "company": 'Primacasa',
                        "supplier_name": row[10],
                        "supplier_name_in_arabic": row[10][6:],
                        "tax_id": row[10][0:5],
                        "supplier_group": 'Raw Material',
                        "add_account": 1
                    }).insert(ignore_permissions=True)
                    
                    i+=1

        print('*************')
        print(i)
        print('*************')



def add_primacasa_uom_item():
    from frappe.utils.csvutils import read_csv_content
    from frappe.core.doctype.data_import.importer import upload
    with open("/home/frappe/frappe-bench/apps/erpnext/erpnext/primacasa_items.csv", "r") as infile:   
        rows = read_csv_content(infile.read())
        i = 0
        for index, row in enumerate(rows):
            if row[7]:
                if not frappe.db.exists("UOM", {"uom_name": row[7]}) :
                    print(row[7])
                    frappe.get_doc({
                        "doctype":"UOM",
                        "uom_name": row[7]
                    }).insert(ignore_permissions=True)
                    
                    i+=1

        print('*************')
        print(i)
        print('*************')



def add_primacasa_item_group():
    from frappe.utils.csvutils import read_csv_content
    from frappe.core.doctype.data_import.importer import upload
    with open("/home/frappe/frappe-bench/apps/erpnext/erpnext/primacasa_items.csv", "r") as infile:   
        rows = read_csv_content(infile.read())
        i = 0
        for index, row in enumerate(rows):
            if row[3]:
                if not frappe.db.exists("Item Group", {"item_group_name": row[3]}) :
                    print(row[3])
                    frappe.get_doc({
                        "doctype":"Item Group",
                        "company": 'Primacasa',
                        "is_group": 1,
                        "item_group_name": row[3],
                        "parent_item_group": 'All Item Groups'
                    }).insert(ignore_permissions=True)
                    
                    i+=1

        print('*************')
        print(i)
        print('*************')




def add_primacasa_sub_item_group():
    from frappe.utils.csvutils import read_csv_content
    from frappe.core.doctype.data_import.importer import upload
    with open("/home/frappe/frappe-bench/apps/erpnext/erpnext/primacasa_items.csv", "r") as infile:   
        rows = read_csv_content(infile.read())
        i = 0
        for index, row in enumerate(rows):
            if row[4]:
                if not frappe.db.exists("Item Group", {"item_group_name": row[4]}) :
                    print(row[4])
                    frappe.get_doc({
                        "doctype":"Item Group",
                        "company": 'Primacasa',
                        "is_group": 0,
                        "item_group_name": row[4],
                        "parent_item_group": row[3]
                    }).insert(ignore_permissions=True)
                    
                    i+=1

        print('*************')
        print(i)
        print('*************')



def add_primacasa_item_company():
    from frappe.utils.csvutils import read_csv_content
    from frappe.core.doctype.data_import.importer import upload
    with open("/home/frappe/frappe-bench/apps/erpnext/erpnext/primacasa_items.csv", "r") as infile:   
        rows = read_csv_content(infile.read())
        i = 0
        for index, row in enumerate(rows):
            if row[5]:
                if not frappe.db.exists("Item Company", {"item_company": row[5]}) :
                    print(row[5])
                    frappe.get_doc({
                        "doctype":"Item Company",
                        "item_company": row[5]
                    }).insert(ignore_permissions=True)
                    
                    i+=1

        print('*************')
        print(i)
        print('*************')


def add_primacasa_items():
    from frappe.utils.csvutils import read_csv_content
    from frappe.core.doctype.data_import.importer import upload
    with open("/home/frappe/frappe-bench/apps/erpnext/erpnext/primacasa_items.csv", "r") as infile:   
        rows = read_csv_content(infile.read())
        i = 0
        for index, row in enumerate(rows):

            if index:
                print(index)

                item = frappe.new_doc('Item')
                item.company = 'Primacasa'
                item.item_name = row[1]
                item.description = row[2]
                item.item_group = row[3]
                item.sub_item_group = row[4]
                item.item_company = row[5]
                item.standard_rate = row[6]
                item.valuation_rate = row[6]
                item.stock_uom = row[7]
                item.is_stock_item = 1
                item.item_code = row[11]

                if flt(row[8])>0 and flt(row[6])>0:
                    item.opening_stock = row[8]
                
                if cint(row[12])==1:
                    item.append('taxes', {
                        'tax_type': 'VAT 5% - P',
                        'tax_rate': 5
                    })

                if row[10]:
                    item.append('item_defaults', {
                        'company': 'Primacasa',
                        'default_warehouse': 'Stores - P',
                        'default_price_list': 'Standard Selling',
                        'default_supplier': row[10]
                    })

                    item.append('supplier_items', {
                        'supplier': row[10],
                        'supplier_part_no': str(row[10][0:5])
                    })

                item.save()

                i+=1


        print('*************')
        print(i)
        print('*************')




def update_items_company():
    i = 0
    errors = []
    items = frappe.db.sql_list("select name from `tabItem`")
    for item in items:

        print(i,' ----- ',item)
        doc = frappe.get_doc('Item', item )
        doc.company = 'aldaan'
        doc.save(ignore_permissions = True)
      
        i=i+1
    print(i)



def submit_purchase_invoice():
    i = 0
    errors = []
    purchase_invoices = frappe.db.sql_list("select name from `tabPurchase Invoice` where modified>'2019-08-01' and docstatus=0 ")
    for invoice in purchase_invoices:

        print(i,' ----- ',invoice)
        doc = frappe.get_doc('Purchase Invoice', invoice )
        doc.flags.ignore_validate = True

        # try:
        doc.submit()
        # except :
        #     errors.append(invoice)
        
        i=i+1


    

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

            
