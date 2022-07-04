frappe.ui.form.on('Job Card', {
	onload: function(frm) {
		if(frm.doc.status!="Completed"){
			if(frm.doc.work_order && frm.doc.production_item && frm.doc.operation){
				frappe.call({
					method: "manufacturer_customizations.manufacturer_customizations.doctype.job_card.job_card.update_qty_to_manufacture",
					args:{
						"work_order":frm.doc.work_order,
						"production_item":frm.doc.production_item,
						"operation":frm.doc.operation,
						"for_quantity":frm.doc.for_quantity,
						"name":frm.doc.name
					},
					callback: function (r) {
						if(r.message!=0){
							for(var i=0;i<frm.doc.time_logs.length;i++){
								var child=frm.doc.time_logs[i]
								if(child.completed_qty!=frm.doc.for_quantity && i==0){
									frappe.call({
										method: "manufacturer_customizations.manufacturer_customizations.doctype.job_card.job_card.set_completed_qty",
										args:{
											'name':child.name,
											'qty':r.message,
											'work_order':frm.doc.work_order,
											'production_item':frm.doc.production_item
										},
										callback: function (r) {
											frm.reload_doc()
										}
									})
								}
							}
						}
						if(r.message==0){
							for(var i=0;i<frm.doc.time_logs.length;i++){
								var child=frm.doc.time_logs[i]
								if(child.completed_qty!=frm.doc.for_quantity){
									frappe.call({
										method: "manufacturer_customizations.manufacturer_customizations.doctype.job_card.job_card.set_completed_qty",
										args:{
											'name':child.name,
											'qty':frm.doc.for_quantity,
											'work_order':frm.doc.work_order,
											'production_item':frm.doc.production_item
										},
										callback: function (r) {
											frm.reload_doc()
										}
									})
								}
							}
						}
					}
				});
			}
		}
	}
});

frappe.ui.form.on('Job Card Time Log', {
    accepted_qty: function(frm, cdt, cdn){
		calculate_rejected_excess_qty(frm, cdt, cdn);
	}
});

function calculate_rejected_excess_qty(frm, cdt, cdn){
	var row = locals[cdt][cdn];
	var rejected_qty = row.launch_qty - row.accepted_qty;
	var excess_qty=0;
	var shortfall_qty=0;
	if(row.accepted_qty>row.order_qty){
		excess_qty = row.accepted_qty - row.order_qty
	}
	else if(row.accepted_qty<=row.order_qty){
		excess_qty=0
	}
	if(row.accepted_qty<row.order_qty){
		shortfall_qty=row.order_qty-row.accepted_qty
	}
	else if(row.accepted_qty>=row.order_qty){
		shortfall_qty=0
	}
	frappe.model.set_value(cdt,cdn,'rejected_qty', rejected_qty);
	frappe.model.set_value(cdt,cdn,'excess_qty', excess_qty);
	frappe.model.set_value(cdt,cdn,'shortfall_qty', shortfall_qty);
}
