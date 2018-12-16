// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

cur_frm.add_fetch('employee', 'company', 'company');
cur_frm.add_fetch('employee', 'employee_name', 'employee_name');

cur_frm.cscript.onload = function(doc, cdt, cdn) {
	if(doc.__islocal) cur_frm.set_value("attendance_date", frappe.datetime.get_today());
}

cur_frm.fields_dict.employee.get_query = function(doc,cdt,cdn) {
	return{
		query: "erpnext.controllers.queries.employee_query"
	}	
}


frappe.ui.form.on("Attendance", {
	finished_on: function(frm) {
		var total = frm.doc.finished_on - frm.doc.start_on;
		var start = moment(frm.doc.start_on, "HH:mm");
		var end = moment(frm.doc.finished_on, "HH:mm");
		var minutes = end.diff(start, 'minutes');
		var hours = Math.trunc(minutes/60);
		var m1 = minutes%60;
		var total_t = (	hours-1) + ":" + m1;
		var total_time = total_t;
		refresh_field('total_time');
		frm.set_value('over_time_hours', hours-1)
		frm.set_value('over_time_minutes', m1)
		frm.set_value('actual_working_hours', total_time)
	},
	start_on: function(frm) {
		var total = frm.doc.finished_on - frm.doc.start_on;
		var start = moment(frm.doc.start_on, "HH:mm");
		var end = moment(frm.doc.finished_on, "HH:mm");
		var minutes = end.diff(start, 'minutes');
		var hours = Math.trunc(minutes/60);
		var m1 = minutes%60;
		var total_t = (hours-1) + ":" + m1;
		var total_time = total_t;
		refresh_field('total_time');
		frm.set_value('over_time_hours', hours-1)
		frm.set_value('over_time_minutes', m1)
		frm.set_value('actual_working_hours', total_time)
	},
	finished_on_work: function(frm) {
		var total = frm.doc.finished_on_work - frm.doc.start_on_work;
		var start = moment(frm.doc.start_on_work, "HH:mm");
		var end = moment(frm.doc.finished_on_work, "HH:mm");
		var minutes = end.diff(start, 'minutes');
		var hours = Math.trunc(minutes/60);
		var m1 = minutes%60;
		var total_t = (	hours-1) + ":" + m1;
		var total_time = total_t;
		refresh_field('total_time');
		frm.set_value('over_time_hours_work', hours-1)
		frm.set_value('over_time_minutes_work', m1)
		frm.set_value('actual_working_hours_work', total_time)
	},
	start_on_work: function(frm) {
		var total = frm.doc.finished_on_work - frm.doc.start_on_work;
		var start = moment(frm.doc.start_on_work, "HH:mm");
		var end = moment(frm.doc.finished_on_work, "HH:mm");
		var minutes = end.diff(start, 'minutes');
		var hours = Math.trunc(minutes/60);
		var m1 = minutes%60;
		var total_t = (hours-1) + ":" + m1;
		var total_time = total_t;
		refresh_field('total_time');
		frm.set_value('over_time_hours_work', hours-1)
		frm.set_value('over_time_minutes_work', m1)
		frm.set_value('actual_working_hours_work', total_time)
	}

});


frappe.ui.form.on("Attendance", "on_submit", function(frm, cdt, cdn) {
    var total = frm.doc.finished_on - frm.doc.start_on;
	var start = moment(frm.doc.start_on, "HH:mm");
	var end = moment(frm.doc.finished_on, "HH:mm");
	var minutes = end.diff(start, 'minutes');
	var hours = Math.trunc(minutes/60);
	var m1 = minutes%60;
	var total_t = (hours-1) + ":" + m1;
	var total_time = total_t;
	refresh_field('total_time');
	frm.set_value('over_time_hours', hours-1)
	frm.set_value('over_time_minutes', m1)
	frm.set_value('actual_working_hours', total_time)
})




frappe.ui.form.on("Attendance", "on_submit", function(frm, cdt, cdn) {
    var total = frm.doc.finished_on_work - frm.doc.start_on_work;
	var start = moment(frm.doc.start_on_work, "HH:mm");
	var end = moment(frm.doc.finished_on_work, "HH:mm");
	var minutes = end.diff(start, 'minutes');
	var hours = Math.trunc(minutes/60);
	var m1 = minutes%60;
	var total_t = (hours-1) + ":" + m1;
	var total_time = total_t;
	refresh_field('total_time');
	frm.set_value('over_time_hours_work', hours-1)
	frm.set_value('over_time_minutes_work', m1)
	frm.set_value('actual_working_hours_work', total_time)
})

