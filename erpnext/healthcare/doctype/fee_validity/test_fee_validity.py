# -*- coding: utf-8 -*-
# Copyright (c) 2015, ESS LLP and Contributors
# See license.txt
from __future__ import unicode_literals

import frappe
import unittest
from erpnext.healthcare.doctype.patient_appointment.patient_appointment import invoice_appointment
from frappe.utils.make_random import get_random
from frappe.utils import nowdate, add_days
# test_records = frappe.get_test_records('Fee Validity')

class TestFeeValidity(unittest.TestCase):
	def test_fee_validity(self):
		patient = get_random("Patient")
		practitioner = get_random("Healthcare Practitioner")
		department = get_random("Medical Department")

		if not patient:
			patient = frappe.new_doc("Patient")
			patient.patient_name = "Test Patient"
			patient.sex = "Male"
			patient.save(ignore_permissions=True)
			patient = patient.name

		if not department:
			medical_department = frappe.new_doc("Medical Department")
			medical_department.department = "Test Medical Department"
			medical_department.save(ignore_permissions=True)
			department = medical_department.name

		if not practitioner:
			practitioner = frappe.new_doc("Healthcare Practitioner")
			practitioner.first_name = "Amit Jain"
			practitioner.department = department
			practitioner.save(ignore_permissions=True)
			practitioner = practitioner.name



		frappe.db.set_value("Healthcare Settings", None, "max_visit", 2)
		frappe.db.set_value("Healthcare Settings", None, "valid_days", 7)

		appointment = create_appointment(patient, practitioner, nowdate(), department)
		invoice = frappe.db.get_value("Patient Appointment", appointment.name, "sales_invoice")
		self.assertEqual(invoice, None)
		invoice_appointment(appointment)
		appointment = create_appointment(patient, practitioner, add_days(nowdate(), 4), department)
		invoice = frappe.db.get_value("Patient Appointment", appointment.name, "sales_invoice")
		self.assertTrue(invoice)
		appointment = create_appointment(patient, practitioner, add_days(nowdate(), 5), department)
		invoice = frappe.db.get_value("Patient Appointment", appointment.name, "sales_invoice")
		self.assertEqual(invoice, None)
		appointment = create_appointment(patient, practitioner, add_days(nowdate(), 10), department)
		invoice = frappe.db.get_value("Patient Appointment", appointment.name, "sales_invoice")
		self.assertEqual(invoice, None)

def create_appointment(patient, practitioner, appointment_date, department):
	appointment = frappe.new_doc("Patient Appointment")
	appointment.patient = patient
	appointment.practitioner = practitioner
	appointment.department = department
	appointment.appointment_date = appointment_date
	appointment.company = "_Test Company"
	appointment.save(ignore_permissions=True)
	return appointment
