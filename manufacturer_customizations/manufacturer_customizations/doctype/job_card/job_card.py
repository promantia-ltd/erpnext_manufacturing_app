import frappe
import json
from erpnext.manufacturing.doctype.job_card import job_card_dashboard
from frappe import _

def get_job_cards(raw_jobs):
    job_names = [j['name'] for j in raw_jobs]    
    query = """SELECT jc.name, jc.work_order, jc.company, jc.for_quantity, 
                jc.operation, wo.sales_order, so.total_qty 
                from `tabJob Card` jc
                LEFT JOIN `tabWork Order` wo on jc.work_order = wo.name
                LEFT JOIN `tabSales Order` so on wo.sales_order = so.name"""
    if len(job_names) == 1:
        query += f" WHERE jc.name = '{job_names[0]}'"
    else:
        query += f" WHERE jc.name in {tuple(job_names)}"

    jobs = frappe.db.sql(query, as_dict=1)
    job_cards = {}
    for job in jobs:
        name = job.pop('name')
        job_cards.setdefault(name, job)
    return job_cards

def validate_records(job_cards):
    values = job_cards.values()
    company, operation = '', ''

    for val in values:
        if company == '':
            company = val.company
        else:
            if company != val.company:
                frappe.throw("Please select Job Cards with same Company")
        
        if operation == '':
            operation = val.operation
        else:
            if operation != val.operation:
                frappe.throw("Please select Job Cards with same Operation")
    return company


def insert_job_details(job_cards):
    if len(job_cards) != 0:
        completed_job = frappe.get_doc(
            {
                "doctype": "Completed Jobs"
            }
        )
        for key, value in job_cards.items():
            so_rec=frappe.db.get_value('Work Order',value.work_order,'sales_order')

            order_qty=frappe.db.get_value('Sales Order Item',{'parent':so_rec,'item_code':frappe.db.get_value('Job Card',key,'production_item')},'qty')
            excess_qty=0
            shortfall_qty=0
            if value.for_quantity>order_qty:
                excess_qty = value.for_quantity - order_qty
            elif value.for_quantity<=order_qty:
                excess_qty=0
            if value.for_quantity<order_qty:
                shortfall_qty=order_qty-value.for_quantity
            elif value.for_quantity>=order_qty:
                shortfall_qty=0

            completed_job.append('job_logs', {
                "operation": value.operation or '',
                "work_order": value.work_order or '',
                "job_card": key,
                "order_qty": order_qty,
                "launch_qty": frappe.db.get_value('Work Order',value.work_order,'qty'),
                "accepted_qty": value.for_quantity,
                "excess_qty":excess_qty,
                "shortfall_qty":shortfall_qty,
                "completed_qty":value.for_quantity
            })
    return completed_job

def insert_raw_materials_and_scrap_items(completed_jobs, job_cards):
    required_fields = ['item_code', 'source_warehouse', 'uom', 'stock_uom', 'required_qty', 'allow_alternative_item']
    query = 'SELECT * FROM `tabJob Card Item`'
    keys = job_cards.keys()
    if len(keys) == 1:
        query += f""" WHERE parent = '{keys[0]}'"""
    else:
        query += f""" WHERE parent in {tuple(keys)}"""
    
    data = frappe.db.sql(query, as_dict=1)
    if len(data) != 0:
        raw_materials = {}
        for d in data:
            for key, value in d.items():
                if key in required_fields:
                    raw_materials[key] = value
            completed_jobs.append('items', raw_materials)
            raw_materials = {}


    required_scrap_fields = ['item_code', 'item_name', 'stock_qty', 'stock_uom']
    scrap_quary = """SELECT * FROM `tabJob Card Scrap Item`"""
    if len(keys) == 1:
        query += f""" WHERE parent = '{keys[0]}'"""
    else:
        query += f""" WHERE parent in {tuple(keys)}"""

    scrap_data = frappe.db.sql(scrap_quary, as_dict=1)
    if len(scrap_data) != 0:
        scrap_materials = {}
        for sd in scrap_data:
            for key, value in sd.items():
                if key in required_scrap_fields:
                    scrap_materials[key] = value
            completed_jobs.append('scrap_items', scrap_materials)
            scrap_materials = {}

    return completed_jobs

@frappe.whitelist()
def make_quality_inspection(doc):
    doc = json.loads(doc)
    qi = frappe.get_doc({
        'doctype': 'Quality Inspection',
        "inspection_type": "In Process",
        "reference_type": "Job Card",
        "reference_name": doc.get('name'),
        "item_code": doc.get('production_item'),
        "item_name": doc.get('item_name'),
        "item_serial_no": doc.get('serial_no'),
        "batch_no": doc.get('batch_no'),
        "quality_inspection_template": doc.get('quality_inspection_template'),
        "inspected_by": frappe.session.user,
        'sample_size': doc.get('for_quantity')
    })
    if len(doc.get('time_logs')) != 0:
        time_logs = doc.get('time_logs')
        qi.update({
            'quantity_tested': time_logs[0].get('completed_qty'),
            'quantity_passed': time_logs[0].get('accepted_qty'),
            'excess_qty': time_logs[0].get('excess_qty'),
            'rejected_qty': time_logs[0].get('rejected_qty'),
            'order_qty': time_logs[0].get('order_qty'),
            'shortfall_qty':time_logs[0].get('shortfall_qty'),
            'launch_qty': time_logs[0].get('launch_qty'),
        })
    resp = qi.insert()
    if resp:
        frappe.msgprint(f'Quality Inspection Created Successfully.')
        return resp.name
    else:
        frappe.msgprint(f'Quality Inspection creation failed.')
        return None

@frappe.whitelist()
def create_completed_jobs(raw_jobs):
    raw_jobs = json.loads(raw_jobs)
    job_cards = get_job_cards(raw_jobs)
    company = validate_records(job_cards)
    qty_updated_job_cards=fetch_previous_operation_acc_qty(job_cards)
    completed_job = insert_job_details(qty_updated_job_cards)
    #completed_job = insert_raw_materials_and_scrap_items(completed_job, job_cards)
    completed_job.company = company
    
    resp = completed_job.insert(ignore_mandatory=True)
    if resp:
        return f'Completed Jobs Created Successfully <a href= "completed-jobs/{resp.name}">{resp.name}</a>.'
    else:
        return f"Failed to created Completed Jobs"

def fetch_previous_operation_acc_qty(job_cards):
    for key, value in job_cards.items():
        if value.work_order:
            wo_rec=frappe.get_doc('Work Order',value.work_order)
            if wo_rec.operations:
                previous_operation_acc_qty=0
                for idx, oper in enumerate(wo_rec.operations):
                    if value.operation==oper.operation:
                        if idx!=0:
                            job_card_rec=frappe.get_doc('Job Card',{'work_order':value.work_order,'operation':wo_rec.operations[idx-1].operation})
                            if job_card_rec.time_logs:
                                for time_log in job_card_rec.time_logs:
                                    previous_operation_acc_qty=time_log.accepted_qty
                            value.for_quantity=previous_operation_acc_qty
                            value.total_qty=previous_operation_acc_qty
                            frappe.db.set_value('Job Card',key,'for_quantity',previous_operation_acc_qty)
    return job_cards

@frappe.whitelist()
def update_qty_to_manufacture(work_order,production_item,operation,for_quantity,name):
    wo_rec=frappe.get_doc('Work Order',work_order)
    if wo_rec.operations:
        previous_operation_acc_qty=0
        for idx, oper in enumerate(wo_rec.operations):
            if operation==oper.operation:
                if idx!=0:
                    job_card_rec=frappe.get_doc('Job Card',{'work_order':work_order,'operation':wo_rec.operations[idx-1].operation})
                    if job_card_rec.time_logs:
                        for idx, time_log in enumerate(job_card_rec.time_logs):
                            if idx==0:
                                previous_operation_acc_qty=time_log.accepted_qty
                                if float(for_quantity)!=previous_operation_acc_qty:
                                    frappe.db.set_value('Job Card',name,'for_quantity',previous_operation_acc_qty)
                                    # frappe.db.set_value('Work Order',name,'final_qty',previous_operation_acc_qty)
    return previous_operation_acc_qty

@frappe.whitelist()
def set_completed_qty(name,qty,work_order,production_item):
    so_rec=frappe.db.get_value('Work Order',work_order,'sales_order')
    frappe.db.set_value('Job Card Time Log',name,'completed_qty',qty)
    frappe.db.set_value('Job Card Time Log',name,'launch_qty',frappe.db.get_value('Work Order',work_order,'qty'))
    if so_rec:
        frappe.db.set_value('Job Card Time Log',name,'order_qty',frappe.db.get_value('Sales Order Item',{'parent':so_rec,'item_code':production_item},'qty'))


@frappe.whitelist()
def validate(self, method):
    if len(self.time_logs) == 0:
        frappe.throw("Please insert Time Logs before submitting the record")
    
    for row in self.time_logs:
        if row.accepted_qty < 0:
            frappe.throw("Accepted Quantity cannot less than 0")
        
        if row.accepted_qty > row.completed_qty:
            frappe.throw("Accepted Quantity cannot be greater than Completed Quantity")

    if self.work_order:
        wo=frappe.get_doc('Work Order',self.work_order)
        operation_name=wo.operations[-1].operation
        if self.operation==operation_name:
            job_card_qty=self.time_logs[0].accepted_qty
            frappe.db.set_value("Work Order",self.work_order,'final_qty',job_card_qty)

