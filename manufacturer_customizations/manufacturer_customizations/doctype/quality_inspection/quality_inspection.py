import frappe
from frappe import _

def on_submit(doc,method=None):
    if not doc.quantity_passed:
        frappe.throw('Please enter the Quantity Passed')
        
    accepted_qty = int(doc.quantity_passed)
    if doc.quantity_passed and doc.quantity_tested:
            if int(doc.quantity_passed) > int(doc.quantity_tested):
                frappe.throw("Quantity Passed cannot be greater than Quantity Tested")
    
    if doc.reference_type=="Job Card":
        frappe.db.set_value("Work Order",doc.reference_name,'final_qty',accepted_qty)
        
    excess_qty=0
    shortfall_qty=0
    if doc.reference_type=="Job Card" and doc.reference_name:
        record=frappe.get_doc(doc.reference_type,doc.reference_name)
        if record.time_logs:
            for each in record.time_logs:
                each.accepted_qty=int(accepted_qty)
                each.rejected_qty=int(each.launch_qty) - int(each.accepted_qty)
                if(int(each.accepted_qty)>int(each.order_qty)):
                    excess_qty = int(each.accepted_qty) - int(each.order_qty)
                elif(int(each.accepted_qty)<=int(each.order_qty)):
                    excess_qty=0
                if(int(each.accepted_qty)<int(each.order_qty)):
                    shortfall_qty=int(each.order_qty)-int(each.accepted_qty)
                elif(int(each.accepted_qty)>=int(each.order_qty)):
                    shortfall_qty=0
                each.excess_qty=excess_qty
                each.shortfall_qty=shortfall_qty
        record.submit()
