import frappe
from frappe import _
def on_submit(doc,method):
    accepted_qty = doc.quantity_passed
    
    # accepted_qty= frappe.db.get_value("quantity_passed","accepted_qty")
    # # print(accepted_qty, doc.reference_name)
    frappe.db.set_value("Job Card Time Log",{'parent':doc.reference_name}, 'accepted_qty',accepted_qty)
    frappe.db.set_value("Work Order",doc.reference_name,'final_accepted_qty',accepted_qty)
    
    # # frappe.db.set_value("Job Card",doc.reference_name, 'serial_no',accepted_qty)
    if doc.quantity_tested < doc.quantity_passed:
        frappe.throw("Quantity Passed cannot be greater than Quantity Tested")
        
        # frappe.db.set_value("Quality Inspection",{'parent':doc.name},'rejected_qty',od)