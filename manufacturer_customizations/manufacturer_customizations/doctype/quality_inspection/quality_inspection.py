import frappe
from frappe import _

def on_submit(doc,method=None):
    accepted_qty = doc.quantity_passed
    frappe.db.set_value("Job Card Time Log",{'parent':doc.reference_name}, 'accepted_qty',accepted_qty)
    frappe.db.set_value("Work Order",doc.reference_name,'final_qty',accepted_qty)
    if doc.quantity_passed and doc.quantity_tested:
        if int(doc.quantity_passed) > int(doc.quantity_tested):
            frappe.throw("Quantity Passed cannot be greater than Quantity Tested")

    if doc.reference_type=="Job Card" and doc.reference_name:
        record=frappe.get_doc(doc.reference_type,doc.reference_name)
        record.submit()
