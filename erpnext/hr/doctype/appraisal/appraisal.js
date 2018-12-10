// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

cur_frm.add_fetch('employee', 'company', 'company');
cur_frm.add_fetch('employee', 'employee_name', 'employee_name');

cur_frm.cscript.onload = function(doc,cdt,cdn){
	if(!doc.status)
		set_multiple(cdt,cdn,{status:'Draft'});
	if(doc.amended_from && doc.__islocal) {
		doc.status = "Draft";
	}
}

cur_frm.cscript.onload_post_render = function(doc,cdt,cdn){
	if(doc.__islocal && doc.employee==frappe.defaults.get_user_default("Employee")) {
		cur_frm.set_value("employee", "");
		cur_frm.set_value("employee_name", "")
	}
}

cur_frm.cscript.refresh = function(doc,cdt,cdn){

}

cur_frm.cscript.kra_template = function(doc, dt, dn) {
	doc.goals = [];
	erpnext.utils.map_current_doc({
		method: "erpnext.hr.doctype.appraisal.appraisal.fetch_appraisal_template",
		source_name: cur_frm.doc.kra_template,
		frm: cur_frm
	});
}

cur_frm.cscript.calculate_total_score = function(doc,cdt,cdn){
	//return get_server_fields('calculate_total','','',doc,cdt,cdn,1);
	var val = doc.goals || [];
	var total =0;
	for(var i = 0; i<val.length; i++){
		total = flt(total)+flt(val[i].score_earned)
	}
	doc.total_score = flt(total)
	refresh_field('total_score')
}

cur_frm.cscript.score = function(doc,cdt,cdn){
	var d = locals[cdt][cdn];
	if (d.score){
		if (flt(d.score) > 5) {
			frappe.msgprint(__("Score must be less than or equal to 5"));
			d.score = 0;
			refresh_field('score', d.name, 'goals');
		}
		var total = flt(d.per_weightage*d.score)/100;
		d.score_earned = total.toPrecision(2);
		refresh_field('score_earned', d.name, 'goals');
	}
	else{
		d.score_earned = 0;
		refresh_field('score_earned', d.name, 'goals');
	}
	cur_frm.cscript.calculate_total(doc,cdt,cdn);
}

cur_frm.cscript.calculate_total = function(doc,cdt,cdn){
	var val = doc.goals || [];
	var total =0;
	for(var i = 0; i<val.length; i++){
		total = flt(total)+flt(val[i].score_earned);
	}
	doc.total_score = flt(total);
	refresh_field('total_score');
}

cur_frm.fields_dict.employee.get_query = function(doc,cdt,cdn) {
	return{	query: "erpnext.controllers.queries.employee_query" }
}




frappe.ui.form.on('Appraisal', {
    refresh: function(frm,cdt,cdn){

    	frm.add_custom_button(__("Test"), function () {



			function convert(timestamp) {
				var date = new Date(timestamp);
				return [date.getFullYear(),("0" + (date.getMonth()+1)).slice(-2),("0" + date.getDate()).slice(-2),].join('-');
			}


			function listDate(startDate,endDate){
				var listDate = [];
				var dateMove = new Date(startDate);
				var strDate = startDate;

				while (strDate < endDate){
				  var strDate = dateMove.toISOString().slice(0,10);
				  listDate.push(strDate);
				  dateMove.setDate(dateMove.getDate()+1);
				};
				return listDate
			}




			var arr=[]

			var end_date = new Date(cur_frm.doc.end_date);
			var makeDate = new Date(cur_frm.doc.end_date);

			


			// previous_month1 = makeDate.setMonth(makeDate.getMonth() - 1);
			// console.log(previous_month1)

			console.log(listDate(convert('2018-10-01'),convert('2018-11-01')))
			console.log(listDate(convert('2018-11-01'),convert('2018-12-01')))

			// frappe.db.get_value('Attendance', {
	  //   		'employee': cur_frm.doc.employee,
	  //   		'docstatus': 1,
	  //   		'attendance_date': ["in", listDate(convert(previous_month1),convert(end_date)) ]
	  //   	}, 'sum(actual_working_hours)', function(r) {
			// 	if(r['sum(actual_working_hours)']){
			// 		arr.push(r['sum(actual_working_hours)'])
			// 	}else{
			// 		arr.push(0)
			// 	}
			// });



			// previous_month2 = makeDate.setMonth(makeDate.getMonth() - 1);
			// frappe.db.get_value('Attendance', {
	  //   		'employee': cur_frm.doc.employee,
	  //   		'docstatus': 1,
	  //   		'attendance_date': ["in", listDate(convert(previous_month2),convert(previous_month1)) ]
	  //   	}, 'sum(actual_working_hours)', function(r) {
			// 	if(r['sum(actual_working_hours)']){
			// 		arr.push(r['sum(actual_working_hours)'])
			// 	}else{
			// 		arr.push(0)
			// 	}
			// });

			


			// previous_month3 = makeDate.setMonth(makeDate.getMonth() - 1);
			// frappe.db.get_value('Attendance', {
	  //   		'employee': cur_frm.doc.employee,
	  //   		'docstatus': 1,
	  //   		'attendance_date': ["in", listDate(convert(previous_month3),convert(previous_month2)) ]
	  //   	}, 'sum(actual_working_hours)', function(r) {
			// 	if(r['sum(actual_working_hours)']){
			// 		arr.push(r['sum(actual_working_hours)'])
			// 	}else{
			// 		arr.push(0)
			// 	}
			// });



			// previous_month4 = makeDate.setMonth(makeDate.getMonth() - 1);
			// frappe.db.get_value('Attendance', {
	  //   		'employee': cur_frm.doc.employee,
	  //   		'docstatus': 1,
	  //   		'attendance_date': ["in", listDate(convert(previous_month4),convert(previous_month3)) ]
	  //   	}, 'sum(actual_working_hours)', function(r) {
			// 	if(r['sum(actual_working_hours)']){
			// 		arr.push(r['sum(actual_working_hours)'])
			// 	}else{
			// 		arr.push(0)
			// 	}
			// });



			// previous_month5 = makeDate.setMonth(makeDate.getMonth() - 1);
			// frappe.db.get_value('Attendance', {
	  //   		'employee': cur_frm.doc.employee,
	  //   		'docstatus': 1,
	  //   		'attendance_date': ["in", listDate(convert(previous_month5),convert(previous_month4)) ]
	  //   	}, 'sum(actual_working_hours)', function(r) {
			// 	if(r['sum(actual_working_hours)']){
			// 		arr.push(r['sum(actual_working_hours)'])
			// 	}else{
			// 		arr.push(0)
			// 	}
			// });



			// previous_month6 = makeDate.setMonth(makeDate.getMonth() - 1);
			// frappe.db.get_value('Attendance', {
	  //   		'employee': cur_frm.doc.employee,
	  //   		'docstatus': 1,
	  //   		'attendance_date': ["in", listDate(convert(previous_month6),convert(previous_month5)) ]
	  //   	}, 'sum(actual_working_hours)', function(r) {
			// 	if(r['sum(actual_working_hours)']){
			// 		arr.push(r['sum(actual_working_hours)'])
			// 	}else{
			// 		arr.push(0)
			// 	}
			// });



			// previous_month7 = makeDate.setMonth(makeDate.getMonth() - 1);
			// frappe.db.get_value('Attendance', {
	  //   		'employee': cur_frm.doc.employee,
	  //   		'docstatus': 1,
	  //   		'attendance_date': ["in", listDate(convert(previous_month7),convert(previous_month6)) ]
	  //   	}, 'sum(actual_working_hours)', function(r) {
			// 	if(r['sum(actual_working_hours)']){
			// 		arr.push(r['sum(actual_working_hours)'])
			// 	}else{
			// 		arr.push(0)
			// 	}
			// });



			// previous_month8 = makeDate.setMonth(makeDate.getMonth() - 1);
			// frappe.db.get_value('Attendance', {
	  //   		'employee': cur_frm.doc.employee,
	  //   		'docstatus': 1,
	  //   		'attendance_date': ["in", listDate(convert(previous_month8),convert(previous_month7)) ]
	  //   	}, 'sum(actual_working_hours)', function(r) {
			// 	if(r['sum(actual_working_hours)']){
			// 		arr.push(r['sum(actual_working_hours)'])
			// 	}else{
			// 		arr.push(0)
			// 	}
			// });



			// previous_month9 = makeDate.setMonth(makeDate.getMonth() - 1);
			// frappe.db.get_value('Attendance', {
	  //   		'employee': cur_frm.doc.employee,
	  //   		'docstatus': 1,
	  //   		'attendance_date': ["in", listDate(convert(previous_month9),convert(previous_month8)) ]
	  //   	}, 'sum(actual_working_hours)', function(r) {
			// 	if(r['sum(actual_working_hours)']){
			// 		arr.push(r['sum(actual_working_hours)'])
			// 	}else{
			// 		arr.push(0)
			// 	}
			// });




			// tt=frappe.db.get_value('Attendance', {
	  //   		'docstatus': 1,
	  //   		'attendance_date': ["in", listDate(convert(previous_month9),convert(end_date)) ]
	  //   	}, 'sum(actual_working_hours)', function(r) {
			// 	if(r['sum(actual_working_hours)']){
			// 		arr.push(r['sum(actual_working_hours)'])
			// 	}else{
			// 		arr.push(0)
			// 	}
			// });



        });



    }



});
