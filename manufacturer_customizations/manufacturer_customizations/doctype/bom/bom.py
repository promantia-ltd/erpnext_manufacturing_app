from collections import deque
from operator import itemgetter
from typing import List

import frappe
from frappe import _
from frappe.utils import cint, cstr, flt
from erpnext.manufacturing.doctype.bom.bom import *
from erpnext.manufacturing.doctype.bom.bom import BOM

class CustomBOM(BOM):
    @frappe.whitelist()
    def get_bom_material_detail(self, args=None):
        """ Get raw material details like uom, desc and rate"""
        if not args:
            args = frappe.form_dict.get('args')

        if isinstance(args, str):
            import json
            args = json.loads(args)

        item = self.get_item_det(args['item_code'])

        args['bom_no'] = args['bom_no'] or item and cstr(item['default_bom']) or ''
        args['transfer_for_manufacture'] = (cstr(args.get('include_item_in_manufacturing', '')) or
            item and item.include_item_in_manufacturing or 0)
        args.update(item)

        rate = self.get_rm_rate(args)
        mfg_conversion_factor = frappe.db.get_value("UOM Conversion Detail",{'uom':item and args['manufacturing_uom'],'parent':item and args['item_code']},'conversion_factor') or 1
        mfg_stock_qty = (args.get("qty") or args.get("stock_qty") or 1) * mfg_conversion_factor
        ret_item = {
                'item_name'	: item and args['item_name'] or '',
                'description'  : item and args['description'] or '',
                'image'		: item and args['image'] or '',
                'stock_uom'	: item and args['stock_uom'] or '',
                'uom'			: item and args['manufacturing_uom'] or item and args['stock_uom'] or '',
                'conversion_factor': mfg_conversion_factor,
                'bom_no'		: args['bom_no'],
                'rate'			: flt(rate) * (flt(mfg_conversion_factor) or 1),
                'qty'			: args.get("qty") or args.get("stock_qty") or 1,
                'stock_qty'	: mfg_stock_qty,
                'base_rate'	: flt(rate) * (flt(mfg_conversion_factor) or 1),
                'include_item_in_manufacturing': cint(args.get('transfer_for_manufacture')),
                'sourced_by_supplier'		: args.get('sourced_by_supplier', 0)
        }

        return ret_item
