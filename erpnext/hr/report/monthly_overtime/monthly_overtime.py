# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
	columns, data = get_columns(filters), get_data(filters)
	return columns, data


def get_columns(filters):
	return [
		_("Name") + ":Link/Employee:150",
		_("Employee Name") + "::150",
		_("Over Time") + "::150"
		]


def get_conditions(filters):
	conditions = ""

	if filters.get("employee"): conditions += " and employee= '{0}' ".format(filters.get("employee"))

	return conditions


def get_data(filters):
	data=[]
	conditions = get_conditions(filters)
	li_list=frappe.db.sql("""select name, employee_name from `tabEmployee`
		where docstatus = 0 {0} """.format(conditions),as_dict=1)

	for emp in li_list:
		i = 1
		days_num = 0
		total_hours = 0
		total_minutes = 0
		attendace_count = frappe.db.sql("select count(name) from `tabAttendance` where employee='{0}' and attendance_date between '{1}' and '{2}' ".format(emp.name,filters.get("from_date"),filters.get("to_date")))
		if attendace_count[0][0]>0:
			days_num = attendace_count[0][0]
		else:
			days_num = 0

		working_hours = frappe.db.sql("select sum(over_time_hours)-8*{0},sum(over_time_minutes) from `tabAttendance` where employee='{1}' and attendance_date between '{2}' and '{3}' ".format(attendace_count[0][0],emp.name,filters.get("from_date"),filters.get("to_date")))
		if working_hours:
			total_hours = working_hours[0][0]
			total_minutes = working_hours[0][1]
		while i==1:
			if working_hours[0][1]>=60:
				total_hours = total_hours+1
				total_minutes = total_minutes-60
			i=0

		if total_minutes>=30:
			total_hours = total_hours+1

		row = [
		emp.name,
		emp.employee_name,
		total_hours if total_hours else 0
		]
		data.append(row)

	return data

