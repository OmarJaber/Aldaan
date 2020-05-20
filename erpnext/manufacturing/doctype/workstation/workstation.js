// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.ui.form.on("Workstation", {
	validate: function(frm) {
		var total = 0;
	    $.each(frm.doc.workstation_additions || [], function (i, d) {
	        total += flt(d.workstation_additions_cost);
	    });
	    frm.set_value("hour_rate", total);
	},
	onload: function(frm) {
		if(frm.is_new())
		{
			frappe.call({
				type:"GET",
				method:"erpnext.manufacturing.doctype.workstation.workstation.get_default_holiday_list",
				callback: function(r) {
					if(!r.exe && r.message){
						cur_frm.set_value("holiday_list", r.message);
					}
				}
			})
		}
	},
	get_operations: function(frm) {
		frappe.call({
            method: "get_workstation_additions",
            doc: cur_frm.doc,
            callback: function(r) { 
            	frm.refresh_field("workstation_additions");
            }
        });
	}
})


frappe.ui.form.on("Workstation Additions", "workstation_additions_cost", function (frm, cdt, cdn) {
    var total = 0;
    $.each(frm.doc.workstation_additions || [], function (i, d) {
        total += flt(d.workstation_additions_cost);
    });
    frm.set_value("hour_rate", total);
});
