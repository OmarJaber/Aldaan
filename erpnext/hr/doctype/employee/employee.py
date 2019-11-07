# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe

from frappe.utils import getdate, validate_email_add, today, add_years
from frappe.model.naming import set_name_by_naming_series
from frappe import throw, _, scrub
from frappe.permissions import add_user_permission, remove_user_permission, \
    set_user_permission_if_allowed, has_permission
from frappe.model.document import Document
from erpnext.utilities.transaction_base import delete_events
from frappe.utils.nestedset import NestedSet

class EmployeeUserDisabledError(frappe.ValidationError):
    pass

class Employee(NestedSet):
    nsm_parent_field = 'reports_to'

    def autoname(self):
        naming_method = frappe.db.get_value("HR Settings", None, "emp_created_by")
        if not naming_method:
            throw(_("Please setup Employee Naming System in Human Resource > HR Settings"))
        else:
            if naming_method == 'Naming Series':
                set_name_by_naming_series(self)
            elif naming_method == 'Employee Number':
                self.name = self.employee_number
            elif naming_method == 'Full Name':
                self.set_employee_name()
                self.name = self.employee_name

        self.employee = self.name

    def validate(self):
        from erpnext.controllers.status_updater import validate_status
        validate_status(self.status, ["Active", "Temporary Leave", "Left"])

        self.employee = self.name
        self.set_employee_name()
        self.set_employee_name_arabic()
        self.validate_date()
        self.validate_email()
        self.validate_status()
        self.validate_reports_to()
        self.validate_preferred_email()
        if self.job_applicant:
            self.validate_onboarding_process()

        if self.user_id:
            self.validate_for_enabled_user_id()
            self.validate_duplicate_user_id()
        else:
            existing_user_id = frappe.db.get_value("Employee", self.name, "user_id")
            if existing_user_id:
                remove_user_permission(
                    "Employee", self.name, existing_user_id)

        if self.advances_account_check:
            self.add_advances_account()
        if self.salary_expenses_account_check:
            self.add_salary_expebses_account()
        if self.accrued_vacation_account_check:
            self.add_accrued_vacation_account()
        if self.end_of_service_account_check:
            self.Add_end_of_service_account()


    def add_advances_account(self):
        prev='A'
        if self.company=='aldaan':
            prev='A'
        elif self.company=='Show Experts':
            prev='SE'
        elif self.company=='Primacasa':
            prev='P'

        emp_account_name_english = str(self.first_name+' '+self.last_name)
        emp_account_name_arabic = str(self.first_name_arabic+' '+self.last_name_arabic)

        accounts = frappe.db.sql("select account_name from `tabAccount` where parent_account='1271 - Employee Advances - سلف الموظفين - {0}' and account_name like '%{1}%' ".format(prev,emp_account_name_english))
        if not accounts:
            curr_account_number = 0
            account_number = frappe.db.sql("select account_number from `tabAccount` where parent_account='1271 - Employee Advances - سلف الموظفين - {0}' order by creation desc limit 1".format(prev)) 
            if account_number:
                curr_account_number= str(int(account_number[0][0][4:])+int(1))
            else:
                curr_account_number= '001'

            emp_account_name = "Employee Advances - {0} - سلف الموظفين - {1}".format(emp_account_name_english, emp_account_name_arabic)

            frappe.get_doc({
                "doctype": "Account",
                "account_name": str(emp_account_name),
                "account_number": '1271'+str(curr_account_number.zfill(3)),
                "parent_account": '1271 - Employee Advances - سلف الموظفين - {0}'.format(prev),
                "balance_must_be": 'Debit',
                "company": self.company,
                "is_group": 0
            }).save(ignore_permissions = True)
            
            acc_name = frappe.get_list("Account", filters={"account_name": str(emp_account_name) }, fields=["name"])
            self.advances_account = str(acc_name[0]['name'])
            frappe.msgprint("Advances Account for {0} was successfully made".format(emp_account_name_english))


    def add_salary_expebses_account(self):
        prev='A'
        if self.company=='aldaan':
            prev='A'
        elif self.company=='Show Experts':
            prev='SE'
        elif self.company=='Primacasa':
            prev='P'

        emp_account_name_english = str(self.first_name+' '+self.last_name)
        emp_account_name_arabic = str(self.first_name_arabic+' '+self.last_name_arabic)

        accounts = frappe.db.sql("select account_name from `tabAccount` where parent_account='2121 - Salary Expenses Payable - مصاريف رواتب مستحقة - {0}' and account_name like '%{1}%' ".format(prev,emp_account_name_english))
        if not accounts:
            curr_account_number = 0
            account_number = frappe.db.sql("select account_number from `tabAccount` where parent_account='2121 - Salary Expenses Payable - مصاريف رواتب مستحقة - {0}' order by creation desc limit 1".format(prev)) 
            if account_number:
                curr_account_number= str(int(account_number[0][0][4:])+int(1))
            else:
                curr_account_number= '001'

            emp_account_name = "Salary Expenses Payable {0} - مصاريف رواتب مستحقة {1}".format(emp_account_name_english, emp_account_name_arabic)

            frappe.get_doc({
                "doctype": "Account",
                "account_name": str(emp_account_name),
                "account_number": '2121'+str(curr_account_number.zfill(3)),
                "parent_account": '2121 - Salary Expenses Payable - مصاريف رواتب مستحقة - {0}'.format(prev),
                "company": self.company,
                # "balance_must_be": 'Debit',
                "is_group": 0
            }).save(ignore_permissions = True)
            
            acc_name = frappe.get_list("Account", filters={"account_name": str(emp_account_name) }, fields=["name"])
            self.salary_expenses_account = str(acc_name[0]['name'])
            frappe.msgprint("Salary Expenses Account for {0} was successfully made".format(emp_account_name_english))


    def add_accrued_vacation_account(self):
        prev='A'
        if self.company=='aldaan':
            prev='A'
        elif self.company=='Show Experts':
            prev='SE'
        elif self.company=='Primacasa':
            prev='P'

        emp_account_name_english = str(self.first_name+' '+self.last_name)
        emp_account_name_arabic = str(self.first_name_arabic+' '+self.last_name_arabic)

        accounts = frappe.db.sql("select account_name from `tabAccount` where parent_account='2122 - Accrued Vacation Expenses - مصاريف إجازات مستحقة - {0}' and account_name like '%{1}%' ".format(prev,emp_account_name_english))
        if not accounts:
            curr_account_number = 0
            account_number = frappe.db.sql("select account_number from `tabAccount` where parent_account='2122 - Accrued Vacation Expenses - مصاريف إجازات مستحقة - {0}' order by creation desc limit 1".format(prev)) 
            if account_number:
                curr_account_number= str(int(account_number[0][0][4:])+int(1))
            else:
                curr_account_number= '001'

            emp_account_name = "Accrued Vacation Expenses {0} مصاريف إجازات مستحقة {1}".format(emp_account_name_english, emp_account_name_arabic)

            frappe.get_doc({
                "doctype": "Account",
                "account_name": str(emp_account_name),
                "account_number": '2122'+str(curr_account_number.zfill(3)),
                "parent_account": '2122 - Accrued Vacation Expenses - مصاريف إجازات مستحقة - {0}'.format(prev),
                "balance_must_be": 'Credit',
                "company": self.company,
                "is_group": 0
            }).save(ignore_permissions = True)
            
            acc_name = frappe.get_list("Account", filters={"account_name": str(emp_account_name) }, fields=["name"])
            self.accrued_vacation_account = str(acc_name[0]['name'])
            frappe.msgprint("Accrued Vacation Account for {0} was successfully made".format(emp_account_name_english))


    def Add_end_of_service_account(self):
        prev='A'
        if self.company=='aldaan':
            prev='A'
        elif self.company=='Show Experts':
            prev='SE'
        elif self.company=='Primacasa':
            prev='P'

        emp_account_name_english = str(self.first_name+' '+self.last_name)
        emp_account_name_arabic = str(self.first_name_arabic+' '+self.last_name_arabic)

        accounts = frappe.db.sql("select account_name from `tabAccount` where parent_account='2131 - Reserve End of Service Bonus - مخصص مكافأة نهاية الخدمة - {0}' and account_name like '%{1}%' ".format(prev,emp_account_name_english))
        if not accounts:
            curr_account_number = 0
            account_number = frappe.db.sql("select account_number from `tabAccount` where parent_account='2131 - Reserve End of Service Bonus - مخصص مكافأة نهاية الخدمة - {0}' order by creation desc limit 1".format(prev)) 
            if account_number:
                curr_account_number= str(int(account_number[0][0][4:])+int(1))
            else:
                curr_account_number= '001'

            emp_account_name = "Reserve End of Service Bonus {0} - مخصص مكافأة نهاية الخدمة {1}".format(emp_account_name_english, emp_account_name_arabic)

            frappe.get_doc({
                "doctype": "Account",
                "account_name": str(emp_account_name),
                "account_number": '2131'+str(curr_account_number.zfill(3)),
                "parent_account": '2131 - Reserve End of Service Bonus - مخصص مكافأة نهاية الخدمة - {0}'.format(prev),
                "balance_must_be": 'Credit',
                "company": self.company,
                "is_group": 0
            }).save(ignore_permissions = True)
            
            acc_name = frappe.get_list("Account", filters={"account_name": str(emp_account_name) }, fields=["name"])
            self.end_of_service_account = str(acc_name[0]['name'])
            frappe.msgprint("End of Service Account for {0} was successfully made".format(emp_account_name_english))


    def set_employee_name(self):
        self.employee_name = ' '.join(filter(lambda x: x, [self.first_name, self.middle_name, self.last_name]))

    def set_employee_name_arabic(self):
        self.full_name_arabic = ' '.join(filter(lambda x: x, [self.first_name_arabic, self.middle_name_arabic, self.last_name_arabic]))

    def update_nsm_model(self):
        frappe.utils.nestedset.update_nsm(self)

    def on_update(self):
        self.update_nsm_model()
        if self.user_id:
            self.update_user()
            self.update_user_permissions()

    def update_user_permissions(self):
        if not self.create_user_permission: return
        if not has_permission('User Permission', ptype='write'): return

        add_user_permission("Employee", self.name, self.user_id)
        set_user_permission_if_allowed("Company", self.company, self.user_id)

    def update_user(self):
        # add employee role if missing
        user = frappe.get_doc("User", self.user_id)
        user.flags.ignore_permissions = True

        if "Employee" not in user.get("roles"):
            user.append_roles("Employee")

        # copy details like Fullname, DOB and Image to User
        if self.employee_name and not (user.first_name and user.last_name):
            employee_name = self.employee_name.split(" ")
            if len(employee_name) >= 3:
                user.last_name = " ".join(employee_name[2:])
                user.middle_name = employee_name[1]
            elif len(employee_name) == 2:
                user.last_name = employee_name[1]

            user.first_name = employee_name[0]

        if self.date_of_birth:
            user.birth_date = self.date_of_birth

        if self.gender:
            user.gender = self.gender

        if self.image:
            if not user.user_image:
                user.user_image = self.image
                try:
                    frappe.get_doc({
                        "doctype": "File",
                        "file_name": self.image,
                        "attached_to_doctype": "User",
                        "attached_to_name": self.user_id
                    }).insert()
                except frappe.DuplicateEntryError:
                    # already exists
                    pass

        user.save()

    def validate_date(self):
        if self.date_of_birth and getdate(self.date_of_birth) > getdate(today()):
            throw(_("Date of Birth cannot be greater than today."))

        if self.date_of_birth and self.date_of_joining and getdate(self.date_of_birth) >= getdate(self.date_of_joining):
            throw(_("Date of Joining must be greater than Date of Birth"))

        elif self.date_of_retirement and self.date_of_joining and (getdate(self.date_of_retirement) <= getdate(self.date_of_joining)):
            throw(_("Date Of Retirement must be greater than Date of Joining"))

        elif self.relieving_date and self.date_of_joining and (getdate(self.relieving_date) <= getdate(self.date_of_joining)):
            throw(_("Relieving Date must be greater than Date of Joining"))

        elif self.contract_end_date and self.date_of_joining and (getdate(self.contract_end_date) <= getdate(self.date_of_joining)):
            throw(_("Contract End Date must be greater than Date of Joining"))

    def validate_email(self):
        if self.company_email:
            validate_email_add(self.company_email, True)
        if self.personal_email:
            validate_email_add(self.personal_email, True)

    def validate_status(self):
        if self.status == 'Left' and not self.relieving_date:
            throw(_("Please enter relieving date."))

    def validate_for_enabled_user_id(self):
        if not self.status == 'Active':
            return
        enabled = frappe.db.get_value("User", self.user_id, "enabled")
        if enabled is None:
            frappe.throw(_("User {0} does not exist").format(self.user_id))
        if enabled == 0:
            frappe.throw(_("User {0} is disabled").format(self.user_id), EmployeeUserDisabledError)

    def validate_duplicate_user_id(self):
        employee = frappe.db.sql_list("""select name from `tabEmployee` where
            user_id=%s and status='Active' and name!=%s""", (self.user_id, self.name))
        if employee:
            throw(_("User {0} is already assigned to Employee {1}").format(
                self.user_id, employee[0]), frappe.DuplicateEntryError)

    def validate_reports_to(self):
        if self.reports_to == self.name:
            throw(_("Employee cannot report to himself."))

    def on_trash(self):
        self.update_nsm_model()
        delete_events(self.doctype, self.name)
        if frappe.db.exists("Employee Transfer", {'new_employee_id': self.name, 'docstatus': 1}):
            emp_transfer = frappe.get_doc("Employee Transfer", {'new_employee_id': self.name, 'docstatus': 1})
            emp_transfer.db_set("new_employee_id", '')

    def validate_preferred_email(self):
        if self.prefered_contact_email and not self.get(scrub(self.prefered_contact_email)):
            frappe.msgprint(_("Please enter " + self.prefered_contact_email))

    def validate_onboarding_process(self):
        employee_onboarding = frappe.get_all("Employee Onboarding",
            filters={"job_applicant": self.job_applicant, "docstatus": 1, "boarding_status": ("!=", "Completed")})
        if employee_onboarding:
            doc = frappe.get_doc("Employee Onboarding", employee_onboarding[0].name)
            doc.validate_employee_creation()
            doc.db_set("employee", self.name)

    def get_employee_entitlements(self):
        arr=[]
        try:
            for emp_entitlement in self.employee_entitlement:
                arr.append(emp_entitlement.entitlement_type)

            entitlements = frappe.get_list("Entitlement Type", fields='entitlement_name')
            for entitlement in entitlements:
                if entitlement['entitlement_name'] not in arr:
                    self.append('employee_entitlement', {"entitlement_type": entitlement['entitlement_name']})
        except:
            entitlement=frappe.db.sql("select name from `tabEntitlement Type`")
            for i in entitlement:
                self.append('employee_entitlement', {"entitlement_type": i[0]})
                

def get_timeline_data(doctype, name):
    '''Return timeline for attendance'''
    return dict(frappe.db.sql('''select unix_timestamp(attendance_date), count(*)
        from `tabAttendance` where employee=%s
            and attendance_date > date_sub(curdate(), interval 1 year)
            and status in ('Present', 'Half Day')
            group by attendance_date''', name))

@frappe.whitelist()
def get_retirement_date(date_of_birth=None):
    ret = {}
    if date_of_birth:
        try:
            retirement_age = int(frappe.db.get_single_value("HR Settings", "retirement_age") or 60)
            dt = add_years(getdate(date_of_birth),retirement_age)
            ret = {'date_of_retirement': dt.strftime('%Y-%m-%d')}
        except ValueError:
            # invalid date
            ret = {}

    return ret

def validate_employee_role(doc, method):
    # called via User hook
    if "Employee" in [d.role for d in doc.get("roles")]:
        if not frappe.db.get_value("Employee", {"user_id": doc.name}):
            frappe.msgprint(_("Please set User ID field in an Employee record to set Employee Role"))
            doc.get("roles").remove(doc.get("roles", {"role": "Employee"})[0])

def update_user_permissions(doc, method):
    # called via User hook
    if "Employee" in [d.role for d in doc.get("roles")]:
        if not has_permission('User Permission', ptype='write'): return
        employee = frappe.get_doc("Employee", {"user_id": doc.name})
        employee.update_user_permissions()

def send_birthday_reminders():
    """Send Employee birthday reminders if no 'Stop Birthday Reminders' is not set."""
    if int(frappe.db.get_single_value("HR Settings", "stop_birthday_reminders") or 0):
        return

    from frappe.utils.user import get_enabled_system_users
    users = None

    birthdays = get_employees_who_are_born_today()

    if birthdays:
        if not users:
            users = [u.email_id or u.name for u in get_enabled_system_users()]

        for e in birthdays:
            frappe.sendmail(recipients=filter(lambda u: u not in (e.company_email, e.personal_email, e.user_id), users),
                subject=_("Birthday Reminder for {0}").format(e.employee_name),
                message=_("""Today is {0}'s birthday!""").format(e.employee_name),
                reply_to=e.company_email or e.personal_email or e.user_id)

def get_employees_who_are_born_today():
    """Get Employee properties whose birthday is today."""
    return frappe.db.sql("""select name, personal_email, company_email, user_id, employee_name
        from tabEmployee where day(date_of_birth) = day(%(date)s)
        and month(date_of_birth) = month(%(date)s)
        and status = 'Active'""", {"date": today()}, as_dict=True)

def get_holiday_list_for_employee(employee, raise_exception=True):
    if employee:
        holiday_list, company = frappe.db.get_value("Employee", employee, ["holiday_list", "company"])
    else:
        holiday_list=''
        company=frappe.db.get_value("Global Defaults", None, "default_company")

    if not holiday_list:
        holiday_list = frappe.db.get_value("Company", company, "default_holiday_list")

    if not holiday_list and raise_exception:
        frappe.throw(_('Please set a default Holiday List for Employee {0} or Company {1}').format(employee, company))

    return holiday_list

def is_holiday(employee, date=None):
    '''Returns True if given Employee has an holiday on the given date
    :param employee: Employee `name`
    :param date: Date to check. Will check for today if None'''

    holiday_list = get_holiday_list_for_employee(employee)
    if not date:
        date = today()

    if holiday_list:
        return frappe.get_all('Holiday List', dict(name=holiday_list, holiday_date=date)) and True or False

@frappe.whitelist()
def deactivate_sales_person(status = None, employee = None):
    if status == "Left":
        sales_person = frappe.db.get_value("Sales Person", {"Employee": employee})
        if sales_person:
            frappe.db.set_value("Sales Person", sales_person, "enabled", 0)

@frappe.whitelist()
def create_user(employee, user = None, email=None):
    emp = frappe.get_doc("Employee", employee)

    employee_name = emp.employee_name.split(" ")
    middle_name = last_name = ""

    if len(employee_name) >= 3:
        last_name = " ".join(employee_name[2:])
        middle_name = employee_name[1]
    elif len(employee_name) == 2:
        last_name = employee_name[1]

    first_name = employee_name[0]

    if email:
        emp.prefered_email = email

    user = frappe.new_doc("User")
    user.update({
        "name": emp.employee_name,
        "email": emp.prefered_email,
        "enabled": 1,
        "first_name": first_name,
        "middle_name": middle_name,
        "last_name": last_name,
        "gender": emp.gender,
        "birth_date": emp.date_of_birth,
        "phone": emp.cell_number,
        "bio": emp.bio
    })
    user.insert()
    return user.name

def get_employee_emails(employee_list):
    '''Returns list of employee emails either based on user_id or company_email'''
    employee_emails = []
    for employee in employee_list:
        if not employee:
            continue
        user, email = frappe.db.get_value('Employee', employee, ['user_id', 'company_email'])
        if user or email:
            employee_emails.append(user or email)

    return employee_emails

@frappe.whitelist()
def get_children(doctype, parent=None, company=None, is_root=False, is_tree=False):
    filters = [['company', '=', company]]
    fields = ['name as value', 'employee_name as title']

    if is_root:
        parent = ''
    if parent and company and parent!=company:
        filters.append(['reports_to', '=', parent])
    else:
        filters.append(['reports_to', '=', ''])

    employees = frappe.get_list(doctype, fields=fields,
        filters=filters, order_by='name')

    for employee in employees:
        is_expandable = frappe.get_all(doctype, filters=[
            ['reports_to', '=', employee.get('value')]
        ])
        employee.expandable = 1 if is_expandable else 0

    return employees


def on_doctype_update():
    frappe.db.add_index("Employee", ["lft", "rgt"])

def has_user_permission_for_employee(user_name, employee_name):
    return frappe.db.exists({
        'doctype': 'User Permission',
        'user': user_name,
        'allow': 'Employee',
        'for_value': employee_name
    })
