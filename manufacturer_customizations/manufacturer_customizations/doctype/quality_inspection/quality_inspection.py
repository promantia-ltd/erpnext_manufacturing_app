import frappe
from frappe import _
def on_submit(doc,method):
    accepted_qty = doc.quantity_passed
    frappe.db.set_value("Job Card Time Log",{'parent':doc.reference_name}, 'accepted_qty',accepted_qty)
    frappe.db.set_value("Work Order",doc.reference_name,'final_accepted_qty',accepted_qty)
    if doc.quantity_tested < doc.quantity_passed:
        frappe.throw("Quantity Passed cannot be greater than Quantity Tested")