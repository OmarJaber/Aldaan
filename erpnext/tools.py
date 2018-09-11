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


