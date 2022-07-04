import frappe
from frappe import _
def on_submit(doc,method):
    accepted_qty = doc.quantity_passed
    # accepted_qty= frappe.db.get_value("quantity_passed","accepted_qty")
    print(accepted_qty, doc.reference_name)
    frappe.db.set_value("Job Card Time Log",{'parent':doc.reference_name}, 'accepted_qty',accepted_qty)