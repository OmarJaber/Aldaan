# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals

import frappe, os, json

from frappe import _

default_lead_sources = ["Existing Customer", "Reference", "Advertisement",
	"Cold Calling", "Exhibition", "Supplier Reference", "Mass Mailing",
	"Customer's Vendor", "Campaign", "Walk In"]

default_sales_partner_type = ["Channel Partner", "Distributor", "Dealer", "Agent",
	"Retailer", "Implementation Partner", "Reseller"]

def install(country=None):
	records = [
		# domains
		{ 'doctype': 'Domain', 'domain': 'Distribution'},
		{ 'doctype': 'Domain', 'domain': 'Manufacturing'},
		{ 'doctype': 'Domain', 'domain': 'Retail'},
		{ 'doctype': 'Domain', 'domain': 'Services'},
		{ 'doctype': 'Domain', 'domain': 'Education'},
		{ 'doctype': 'Domain', 'domain': 'Healthcare'},
		{ 'doctype': 'Domain', 'domain': 'Agriculture'},
		{ 'doctype': 'Domain', 'domain': 'Non Profit'},

		# Setup Progress
		{'doctype': "Setup Progress", "actions": [
			{"action_name": "Add Company", "action_doctype": "Company", "min_doc_count": 1, "is_completed": 1,
				"domains": '[]' },
			{"action_name": "Set Sales Target", "action_doctype": "Company", "min_doc_count": 99,
				"action_document": frappe.defaults.get_defaults().get("company") or '',
				"action_field": "monthly_sales_target", "is_completed": 0,
				"domains": '["Manufacturing", "Services", "Retail", "Distribution"]' },
			{"action_name": "Add Customers", "action_doctype": "Customer", "min_doc_count": 1, "is_completed": 0,
				"domains": '["Manufacturing", "Services", "Retail", "Distribution"]' },
			{"action_name": "Add Suppliers", "action_doctype": "Supplier", "min_doc_count": 1, "is_completed": 0,
				"domains": '["Manufacturing", "Services", "Retail", "Distribution"]' },
			{"action_name": "Add Products", "action_doctype": "Item", "min_doc_count": 1, "is_completed": 0,
				"domains": '["Manufacturing", "Services", "Retail", "Distribution"]' },
			{"action_name": "Add Programs", "action_doctype": "Program", "min_doc_count": 1, "is_completed": 0,
				"domains": '["Education"]' },
			{"action_name": "Add Instructors", "action_doctype": "Instructor", "min_doc_count": 1, "is_completed": 0,
				"domains": '["Education"]' },
			{"action_name": "Add Courses", "action_doctype": "Course", "min_doc_count": 1, "is_completed": 0,
				"domains": '["Education"]' },
			{"action_name": "Add Rooms", "action_doctype": "Room", "min_doc_count": 1, "is_completed": 0,
				"domains": '["Education"]' },
			{"action_name": "Add Users", "action_doctype": "User", "min_doc_count": 4, "is_completed": 0,
				"domains": '[]' },
			{"action_name": "Add Letterhead", "action_doctype": "Letter Head", "min_doc_count": 1, "is_completed": 0,
				"domains": '[]' }
		]},

		# address template
		{'doctype':"Address Template", "country": country},

		# item group
		{'doctype': 'Item Group', 'item_group_name': _('All Item Groups'),
			'is_group': 1, 'parent_item_group': ''},
		{'doctype': 'Item Group', 'item_group_name': _('Products'),
			'is_group': 0, 'parent_item_group': _('All Item Groups'), "show_in_website": 1 },
		{'doctype': 'Item Group', 'item_group_name': _('Raw Material'),
			'is_group': 0, 'parent_item_group': _('All Item Groups') },
		{'doctype': 'Item Group', 'item_group_name': _('Services'),
			'is_group': 0, 'parent_item_group': _('All Item Groups') },
		{'doctype': 'Item Group', 'item_group_name': _('Sub Assemblies'),
			'is_group': 0, 'parent_item_group': _('All Item Groups') },
		{'doctype': 'Item Group', 'item_group_name': _('Consumable'),
			'is_group': 0, 'parent_item_group': _('All Item Groups') },

		# salary component
		{'doctype': 'Salary Component', 'salary_component': _('Income Tax'), 'description': _('Income Tax'), 'type': 'Deduction'},
		{'doctype': 'Salary Component', 'salary_component': _('Basic'), 'description': _('Basic'), 'type': 'Earning'},
		{'doctype': 'Salary Component', 'salary_component': _('Arrear'), 'description': _('Arrear'), 'type': 'Earning'},
		{'doctype': 'Salary Component', 'salary_component': _('Leave Encashment'), 'description': _('Leave Encashment'), 'type': 'Earning'},


		# expense claim type
		{'doctype': 'Expense Claim Type', 'name': _('Calls'), 'expense_type': _('Calls')},
		{'doctype': 'Expense Claim Type', 'name': _('Food'), 'expense_type': _('Food')},
		{'doctype': 'Expense Claim Type', 'name': _('Medical'), 'expense_type': _('Medical')},
		{'doctype': 'Expense Claim Type', 'name': _('Others'), 'expense_type': _('Others')},
		{'doctype': 'Expense Claim Type', 'name': _('Travel'), 'expense_type': _('Travel')},

		# leave type
		{'doctype': 'Leave Type', 'leave_type_name': _('Casual Leave'), 'name': _('Casual Leave'),
			'allow_encashment': 1, 'is_carry_forward': 1, 'max_continuous_days_allowed': '3', 'include_holiday': 1},
		{'doctype': 'Leave Type', 'leave_type_name': _('Compensatory Off'), 'name': _('Compensatory Off'),
			'allow_encashment': 0, 'is_carry_forward': 0, 'include_holiday': 1},
		{'doctype': 'Leave Type', 'leave_type_name': _('Sick Leave'), 'name': _('Sick Leave'),
			'allow_encashment': 0, 'is_carry_forward': 0, 'include_holiday': 1},
		{'doctype': 'Leave Type', 'leave_type_name': _('Privilege Leave'), 'name': _('Privilege Leave'),
			'allow_encashment': 0, 'is_carry_forward': 0, 'include_holiday': 1},
		{'doctype': 'Leave Type', 'leave_type_name': _('Leave Without Pay'), 'name': _('Leave Without Pay'),
			'allow_encashment': 0, 'is_carry_forward': 0, 'is_lwp':1, 'include_holiday': 1},

		# Employment Type
		{'doctype': 'Employment Type', 'employee_type_name': _('Full-time')},
		{'doctype': 'Employment Type', 'employee_type_name': _('Part-time')},
		{'doctype': 'Employment Type', 'employee_type_name': _('Probation')},
		{'doctype': 'Employment Type', 'employee_type_name': _('Contract')},
		{'doctype': 'Employment Type', 'employee_type_name': _('Commission')},
		{'doctype': 'Employment Type', 'employee_type_name': _('Piecework')},
		{'doctype': 'Employment Type', 'employee_type_name': _('Intern')},
		{'doctype': 'Employment Type', 'employee_type_name': _('Apprentice')},

		# Designation
		{'doctype': 'Designation', 'designation_name': _('CEO')},
		{'doctype': 'Designation', 'designation_name': _('Manager')},
		{'doctype': 'Designation', 'designation_name': _('Analyst')},
		{'doctype': 'Designation', 'designation_name': _('Engineer')},
		{'doctype': 'Designation', 'designation_name': _('Accountant')},
		{'doctype': 'Designation', 'designation_name': _('Secretary')},
		{'doctype': 'Designation', 'designation_name': _('Associate')},
		{'doctype': 'Designation', 'designation_name': _('Administrative Officer')},
		{'doctype': 'Designation', 'designation_name': _('Business Development Manager')},
		{'doctype': 'Designation', 'designation_name': _('HR Manager')},
		{'doctype': 'Designation', 'designation_name': _('Project Manager')},
		{'doctype': 'Designation', 'designation_name': _('Head of Marketing and Sales')},
		{'doctype': 'Designation', 'designation_name': _('Software Developer')},
		{'doctype': 'Designation', 'designation_name': _('Designer')},
		{'doctype': 'Designation', 'designation_name': _('Researcher')},

		# territory
		{'doctype': 'Territory', 'territory_name': _('All Territories'), 'is_group': 1, 'name': _('All Territories'), 'parent_territory': ''},

		# customer group
		{'doctype': 'Customer Group', 'customer_group_name': _('All Customer Groups'), 'is_group': 1, 	'name': _('All Customer Groups'), 'parent_customer_group': ''},
		{'doctype': 'Customer Group', 'customer_group_name': _('Individual'), 'is_group': 0, 'parent_customer_group': _('All Customer Groups')},
		{'doctype': 'Customer Group', 'customer_group_name': _('Commercial'), 'is_group': 0, 'parent_customer_group': _('All Customer Groups')},
		{'doctype': 'Customer Group', 'customer_group_name': _('Non Profit'), 'is_group': 0, 'parent_customer_group': _('All Customer Groups')},
		{'doctype': 'Customer Group', 'customer_group_name': _('Government'), 'is_group': 0, 'parent_customer_group': _('All Customer Groups')},

		# supplier group
		{'doctype': 'Supplier Group', 'supplier_group_name': _('All Supplier Groups'), 'is_group': 1, 'name': _('All Supplier Groups'), 'parent_supplier_group': ''},
		{'doctype': 'Supplier Group', 'supplier_group_name': _('Services'), 'is_group': 0, 'parent_supplier_group': _('All Supplier Groups')},
		{'doctype': 'Supplier Group', 'supplier_group_name': _('Local'), 'is_group': 0, 'parent_supplier_group': _('All Supplier Groups')},
		{'doctype': 'Supplier Group', 'supplier_group_name': _('Raw Material'), 'is_group': 0, 'parent_supplier_group': _('All Supplier Groups')},
		{'doctype': 'Supplier Group', 'supplier_group_name': _('Electrical'), 'is_group': 0, 'parent_supplier_group': _('All Supplier Groups')},
		{'doctype': 'Supplier Group', 'supplier_group_name': _('Hardware'), 'is_group': 0, 'parent_supplier_group': _('All Supplier Groups')},
		{'doctype': 'Supplier Group', 'supplier_group_name': _('Pharmaceutical'), 'is_group': 0, 'parent_supplier_group': _('All Supplier Groups')},
		{'doctype': 'Supplier Group', 'supplier_group_name': _('Distributor'), 'is_group': 0, 'parent_supplier_group': _('All Supplier Groups')},

		# Sales Person
		{'doctype': 'Sales Person', 'sales_person_name': _('Sales Team'), 'is_group': 1, "parent_sales_person": ""},

		# Mode of Payment
		{'doctype': 'Mode of Payment',
			'mode_of_payment': 'Check' if country=="United States" else _('Cheque'),
			'type': 'Bank'},
		{'doctype': 'Mode of Payment', 'mode_of_payment': _('Cash'),
			'type': 'Cash'},
		{'doctype': 'Mode of Payment', 'mode_of_payment': _('Credit Card'),
			'type': 'Bank'},
		{'doctype': 'Mode of Payment', 'mode_of_payment': _('Wire Transfer'),
			'type': 'Bank'},
		{'doctype': 'Mode of Payment', 'mode_of_payment': _('Bank Draft'),
			'type': 'Bank'},

		# Activity Type
		{'doctype': 'Activity Type', 'activity_type': _('Planning')},
		{'doctype': 'Activity Type', 'activity_type': _('Research')},
		{'doctype': 'Activity Type', 'activity_type': _('Proposal Writing')},
		{'doctype': 'Activity Type', 'activity_type': _('Execution')},
		{'doctype': 'Activity Type', 'activity_type': _('Communication')},

		{'doctype': "Item Attribute", "attribute_name": _("Size"), "item_attribute_values": [
			{"attribute_value": _("Extra Small"), "abbr": "XS"},
			{"attribute_value": _("Small"), "abbr": "S"},
			{"attribute_value": _("Medium"), "abbr": "M"},
			{"attribute_value": _("Large"), "abbr": "L"},
			{"attribute_value": _("Extra Large"), "abbr": "XL"}
		]},

		{'doctype': "Item Attribute", "attribute_name": _("Colour"), "item_attribute_values": [
			{"attribute_value": _("Red"), "abbr": "RED"},
			{"attribute_value": _("Green"), "abbr": "GRE"},
			{"attribute_value": _("Blue"), "abbr": "BLU"},
			{"attribute_value": _("Black"), "abbr": "BLA"},
			{"attribute_value": _("White"), "abbr": "WHI"}
		]},

		#Job Applicant Source
		{'doctype': 'Job Applicant Source', 'source_name': _('Website Listing')},
		{'doctype': 'Job Applicant Source', 'source_name': _('Walk In')},
		{'doctype': 'Job Applicant Source', 'source_name': _('Employee Referral')},
		{'doctype': 'Job Applicant Source', 'source_name': _('Campaign')},

		{'doctype': "Email Account", "email_id": "sales@example.com", "append_to": "Opportunity"},
		{'doctype': "Email Account", "email_id": "support@example.com", "append_to": "Issue"},
		{'doctype': "Email Account", "email_id": "jobs@example.com", "append_to": "Job Applicant"},

		{'doctype': "Party Type", "party_type": "Customer", "account_type": "Receivable"},
		{'doctype': "Party Type", "party_type": "Supplier", "account_type": "Payable"},
		{'doctype': "Party Type", "party_type": "Employee", "account_type": "Payable"},
		{'doctype': "Party Type", "party_type": "Member", "account_type": "Receivable"},
		{'doctype': "Party Type", "party_type": "Shareholder", "account_type": "Payable"},
		{'doctype': "Party Type", "party_type": "Student", "account_type": "Receivable"},

		{'doctype': "Opportunity Type", "name": "Hub"},
		{'doctype': "Opportunity Type", "name": _("Sales")},
		{'doctype': "Opportunity Type", "name": _("Support")},
		{'doctype': "Opportunity Type", "name": _("Maintenance")},

		{'doctype': "Project Type", "project_type": "Internal"},
		{'doctype': "Project Type", "project_type": "External"},
		{'doctype': "Project Type", "project_type": "Other"},

		{"doctype": "Offer Term", "offer_term": _("Date of Joining")},
		{"doctype": "Offer Term", "offer_term": _("Annual Salary")},
		{"doctype": "Offer Term", "offer_term": _("Probationary Period")},
		{"doctype": "Offer Term", "offer_term": _("Employee Benefits")},
		{"doctype": "Offer Term", "offer_term": _("Working Hours")},
		{"doctype": "Offer Term", "offer_term": _("Stock Options")},
		{"doctype": "Offer Term", "offer_term": _("Department")},
		{"doctype": "Offer Term", "offer_term": _("Job Description")},
		{"doctype": "Offer Term", "offer_term": _("Responsibilities")},
		{"doctype": "Offer Term", "offer_term": _("Leaves per Year")},
		{"doctype": "Offer Term", "offer_term": _("Notice Period")},
		{"doctype": "Offer Term", "offer_term": _("Incentives")},

		{'doctype': "Print Heading", 'print_heading': _("Credit Note")},
		{'doctype': "Print Heading", 'print_heading': _("Debit Note")},

		# Assessment Group
		{'doctype': 'Assessment Group', 'assessment_group_name': _('All Assessment Groups'),
			'is_group': 1, 'parent_assessment_group': ''},

		# Share Management
		{"doctype": "Share Type", "title": _("Equity")},
		{"doctype": "Share Type", "title": _("Preference")},
	]

	from erpnext.setup.setup_wizard.data.industry_type import get_industry_types
	records += [{"doctype":"Industry Type", "industry": d} for d in get_industry_types()]
	# records += [{"doctype":"Operation", "operation": d} for d in get_operations()]
	records += [{'doctype': 'Lead Source', 'source_name': _(d)} for d in default_lead_sources]

	records += [{'doctype': 'Sales Partner Type', 'sales_partner_type': _(d)} for d in default_sales_partner_type]

	base_path = frappe.get_app_path("erpnext", "hr", "doctype")
	response = frappe.read_file(os.path.join(base_path, "leave_application/leave_application_email_template.html"))

	records += [{'doctype': 'Email Template', 'name': _("Leave Approval Notification"), 'response': response,\
		'subject': _("Leave Approval Notification"), 'owner': frappe.session.user}]

	records += [{'doctype': 'Email Template', 'name': _("Leave Status Notification"), 'response': response,\
		'subject': _("Leave Status Notification"), 'owner': frappe.session.user}]

	# Records for the Supplier Scorecard
	from erpnext.buying.doctype.supplier_scorecard.supplier_scorecard import make_default_records
	make_default_records()

	make_fixture_records(records)

	# set default customer group and territory
	selling_settings = frappe.get_doc("Selling Settings")
	selling_settings.set_default_customer_group_and_territory()
	selling_settings.save()

	add_uom_data()

def add_uom_data():
	# add UOMs
	uoms = json.loads(open(frappe.get_app_path("erpnext", "setup", "setup_wizard", "data", "uom_data.json")).read())
	for d in uoms:
		if not frappe.db.exists('UOM', _(d.get("uom_name"))):
			uom_doc = frappe.get_doc({
				"doctype": "UOM",
				"uom_name": _(d.get("uom_name")),
				"name": _(d.get("uom_name")),
				"must_be_whole_number": d.get("must_be_whole_number")
			}).insert(ignore_permissions=True)

	# bootstrap uom conversion factors
	uom_conversions = json.loads(open(frappe.get_app_path("erpnext", "setup", "setup_wizard", "data", "uom_conversion_data.json")).read())
	for d in uom_conversions:
		if not frappe.db.exists("UOM Category", _(d.get("category"))):
			frappe.get_doc({
				"doctype": "UOM Category",
				"category_name": _(d.get("category"))
			}).insert(ignore_permissions=True)

		uom_conversion = frappe.get_doc({
			"doctype": "UOM Conversion Factor",
			"category": _(d.get("category")),
			"from_uom": _(d.get("from_uom")),
			"to_uom": _(d.get("to_uom")),
			"value": d.get("value")
		}).insert(ignore_permissions=True)

def make_fixture_records(records):
	from frappe.modules import scrub
	for r in records:
		doc = frappe.new_doc(r.get("doctype"))
		doc.update(r)

		# ignore mandatory for root
		parent_link_field = ("parent_" + scrub(doc.doctype))
		if doc.meta.get_field(parent_link_field) and not doc.get(parent_link_field):
			doc.flags.ignore_mandatory = True

		try:
			doc.insert(ignore_permissions=True)
		except frappe.DuplicateEntryError as e:
			# pass DuplicateEntryError and continue
			if e.args and e.args[0]==doc.doctype and e.args[1]==doc.name:
				# make sure DuplicateEntryError is for the exact same doc and not a related doc
				pass
			else:
				raise

def install_post_company_fixtures(company=None):
	records = [
		# Department
		{'doctype': 'Department', 'department_name': _('All Departments'), 'is_group': 1, 'parent_department': ''},
		{'doctype': 'Department', 'department_name': _('Accounts'), 'parent_department': _('All Departments'), 'company': company},
		{'doctype': 'Department', 'department_name': _('Marketing'), 'parent_department': _('All Departments'), 'company': company},
		{'doctype': 'Department', 'department_name': _('Sales'), 'parent_department': _('All Departments'), 'company': company},
		{'doctype': 'Department', 'department_name': _('Purchase'), 'parent_department': _('All Departments'), 'company': company},
		{'doctype': 'Department', 'department_name': _('Operations'), 'parent_department': _('All Departments'), 'company': company},
		{'doctype': 'Department', 'department_name': _('Production'), 'parent_department': _('All Departments'), 'company': company},
		{'doctype': 'Department', 'department_name': _('Dispatch'), 'parent_department': _('All Departments'), 'company': company},
		{'doctype': 'Department', 'department_name': _('Customer Service'), 'parent_department': _('All Departments'), 'company': company},
		{'doctype': 'Department', 'department_name': _('Human Resources'), 'parent_department': _('All Departments'), 'company': company},
		{'doctype': 'Department', 'department_name': _('Management'), 'parent_department': _('All Departments'), 'company': company},
		{'doctype': 'Department', 'department_name': _('Quality Management'), 'parent_department': _('All Departments'), 'company': company},
		{'doctype': 'Department', 'department_name': _('Research & Development'), 'parent_department': _('All Departments'), 'company': company},
		{'doctype': 'Department', 'department_name': _('Legal'), 'parent_department': _('All Departments'), 'company': company},
	]

	make_fixture_records(records)
