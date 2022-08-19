# from tkinter.filedialog import asksaveasfile
# from erpnext.erpnext.stock.doctype.quality_inspection.quality_inspection import quality_inspection_query
import frappe
import json
import pandas as pd
import numpy as np
import calendar
from erpnext.manufacturing.doctype.work_order.work_order import *
from erpnext.manufacturing.doctype.work_order.work_order import WorkOrder
import datetime

@frappe.whitelist()
def get_accepted_qty(doc):
    doc = json.loads(doc)
    record = frappe.get_doc("Job Card", {'work_order': doc.get('name'), 'operation': doc['operations'][-1]['operation'], 'docstatus': 1}, ['*']).as_dict()
    qty = record.time_logs[-1].accepted_qty - doc.get('produced_qty')
    if qty > 0:
        return qty
    else:
        frappe.throw("Accepted Quantity exhausted to create Stock Entry")
        quantity_tested=doc.final_qty
        frappe.db.set_value("Quality Inspection",doc.name,'quality_tested',quantity_tested)

class CustomWorkOrder(WorkOrder):
    def validate_work_order_against_so(self):
        # already ordered qty
        ordered_qty_against_so = frappe.db.sql("""select sum(produced_qty) from `tabWork Order`
            where production_item = %s and sales_order = %s and docstatus < 2 and name != %s""",
            (self.production_item, self.sales_order, self.name))[0][0]

        total_qty = flt(ordered_qty_against_so) + flt(self.qty)

        # get qty from Sales Order Item table
        so_item_qty = frappe.db.sql("""select sum(stock_qty) from `tabSales Order Item`
            where parent = %s and item_code = %s""",
            (self.sales_order, self.production_item))[0][0]
        # get qty from Packing Item table
        dnpi_qty = frappe.db.sql("""select sum(qty) from `tabPacked Item`
            where parent = %s and parenttype = 'Sales Order' and item_code = %s""",
            (self.sales_order, self.production_item))[0][0]
        # total qty in SO
        so_qty = flt(so_item_qty) + flt(dnpi_qty)

        allowance_percentage = flt(frappe.db.get_single_value("Manufacturing Settings",
            "overproduction_percentage_for_sales_order"))

        # if total_qty > so_qty + (allowance_percentage/100 * so_qty):
        #     frappe.throw(_("Cannot produce more Item {0} than Sales Order quantity {1}")
        #         .format(self.production_item, so_qty), OverProductionError)
                


@frappe.whitelist()
def make_stock_entry(work_order_id, purpose, qty=None):
    work_order = frappe.get_doc("Work Order", work_order_id)
    print("workordernumber",work_order.operations)
    job_card = frappe.get_doc("Job Card", {'work_order': work_order_id, 'operation': work_order.operations[-1].operation, 'docstatus': 1}, ['*']).as_dict()
    if job_card.time_logs[-1].accepted_qty < (work_order.get('produced_qty') + flt(qty)):
        frappe.throw("Cannot create stock entry as it exceeds Accepted Quantity")
    if not frappe.db.get_value("Warehouse", work_order.wip_warehouse, "is_group"):
        wip_warehouse = work_order.wip_warehouse
    else:
        wip_warehouse = None

    stock_entry = frappe.new_doc("Stock Entry")
    stock_entry.purpose = purpose
    stock_entry.work_order = work_order_id
    stock_entry.company = work_order.company
    stock_entry.from_bom = 1
    stock_entry.bom_no = work_order.bom_no
    stock_entry.use_multi_level_bom = work_order.use_multi_level_bom
    stock_entry.fg_completed_qty = qty or (flt(work_order.qty) - flt(work_order.produced_qty))
    if work_order.bom_no:
        stock_entry.inspection_required = frappe.db.get_value('BOM',
                                                              work_order.bom_no, 'inspection_required')

    if purpose == "Material Transfer for Manufacture":
        stock_entry.to_warehouse = wip_warehouse
        stock_entry.project = work_order.project
    else:
        stock_entry.from_warehouse = wip_warehouse
        stock_entry.to_warehouse = work_order.fg_warehouse
        stock_entry.project = work_order.project

    stock_entry.set_stock_entry_type()
    stock_entry.get_items()
    stock_entry.set_serial_no_batch_for_finished_good()
    return stock_entry.as_dict()

def update_sales_order_qty(doc, method):
    if(doc.sales_order and not doc.sales_order_qty):
        doc.sales_order_qty=doc.qty

@frappe.whitelist()
def update_name(doc_name):
    layer = frappe.db.get_value('Work Order',{'name':doc_name},'layer')
    out = []
    name = doc_name.strip('WO-')
    name = layer+name
    for row in frappe.db.get_list('Work Order Item',{'parenttype':'Work Order','parent':doc_name},'name'):
        frappe.db.set_value('Work Order Item', row.name,{'parent':name})
    for row_operation in frappe.db.get_list('Work Order Operation',{'parenttype':'Work Order','parent':doc_name},'name'):
        frappe.db.set_value('Work Order Operation', row_operation.name,{'parent':name})
    frappe.db.set_value('Work Order', doc_name,{ 'name': name,'updated_series':1})
    out.append(name)
    return out

@frappe.whitelist()
def update_naming_series_current_value(series,current_value):
    frappe.db.sql("update `tabSeries` set current = %s where name =%s",(int(current_value), series))
    return 'Success'