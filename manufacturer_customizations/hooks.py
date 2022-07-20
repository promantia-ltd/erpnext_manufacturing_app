from . import __version__ as app_version

app_name = "manufacturer_customizations"
app_title = "manufacturer_customizations"
app_publisher = "manufacturer_customizations"
app_description = "manufacturer_customizations"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "abc@gmail.com"
app_license = "MIT"


# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/pcprocess_customizations/css/pcprocess_customizations.css"
# app_include_js = "/assets/pcprocess_customizations/js/pcprocess_customizations.js"

# include js, css files in header of web template
# web_include_css = "/assets/pcprocess_customizations/css/pcprocess_customizations.css"
# web_include_js = "/assets/pcprocess_customizations/js/pcprocess_customizations.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "pcprocess_customizations/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
doctype_list_js = {
    "Job Card": "manufacturer_customizations/doctype/job_card/job_card_list.js"
}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}
doctype_js = {
    "Job Card":"manufacturer_customizations/doctype/job_card/job_card.js",
    "Work Order":"manufacturer_customizations/doctype/work_order/work_order.js"
}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "pcprocess_customizations.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes
fixtures = ["Workflow State", 
            {
                "dt": 'Client Script',
                "filters": [
                    ["name", "in",
                    [
                        "Work Order-Form",
                        "Quality Inspection-Form",
                        "Job Card-Form",
                        "BOM-Form"

                    ]
                    ]

                ]
            },
            {
                "dt": 'DocType',
                "filters": [
                    ["name", "in",
                     [
                             "Spares Item"
                     ]
                     ]
                ]
            },
            {
                "dt": 'Custom Field',
                "filters": [
                    ["name", "in",
                     [
                        "Job Card Time Log-shortfall_qty",
                        "Job Card Time Log-accepted_qty",
                        "BOM Item-column_break_10",
                        "BOM Item-tg",
                        "BOM Item-make",
                        "BOM Item-section_break_7",
                        "Work Order-workflow_state",
                        "Job Card Time Log-rejected_qty",
                        "Job Card Time Log-excess_qty",
                        "Job Card Time Log-order_qty",
                        "Job Card Time Log-launch_qty",
                        "Sales Order-lead_date_and_time",
                        "Work Order Item-length",
                        "Work Order Item-breadth",
                        "Work Order Item-product",
                        "Work Order-batch_code",
                        "BOM-mpc_dpc_no",
                        "Work Order-layer",
                        "Work Order-week_number",
                        "Work Order-year",
                        "Work Order-updated_series",
                        "Item-manufacturing_uom",
                        "Work Order Item-quality_inspection",
			"Work Order-final_qty",
			"Work Order-final_accepted_qty",
			"Quality Inspection-quantity_tested",
			"Quality Inspection-quantity_passed"
                     ]
                     ]
                ]
            },
            {
                "dt": 'Property Setter',
                "filters": [
                    ["name", "in",
                     [
                         "Job Card Time Log-employee-in_list_view",
                         "Work Order-skip_transfer-default",
                         "Work Order-source_warehouse-default",
                         "Work Order-sales_order-reqd",
                         "Work Order-naming_series-default",
			 "Quality Inspection-reference_type-options"
                     ]
                     ]
                ]
            },
            
            ]
override_doctype_class = {
    "Work Order": "manufacturer_customizations.manufacturer_customizations.doctype.work_order.work_order.CustomWorkOrder",
    "BOM": "manufacturer_customizations.manufacturer_customizations.doctype.bom.bom.CustomBOM",
}

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
   # "Quotation": {
    #    "on_submit": ["pcprocess_customizations.schedulers.send_notification_for_quotation"]
    #},
    # "Work Order": {
    #     "before_insert": ["manufacturer_customizations.manufacturer_customizations.doctype.work_order.work_order.set_naming_series"],
    # },
    #"Lead":{
     #   "validate":["pcprocess_customizations.schedulers.send_notification_for_lead"]
    #},
    "Job Card": {
        "on_submit": ['manufacturer_customizations.manufacturer_customizations.doctype.job_card.job_card.validate']
    },
    "Quality Inspection": {
	"on_submit": ['manufacturer_customizations.manufacturer_customizations.doctype.quality_inspection.quality_inspection.on_submit']
    }
    # 	"*": {
    # 		"on_update": "method",
    # 		"on_cancel": "method",
    # 		"on_trash": "method"
    #	}
}

# Scheduled Tasks
# ---------------
# scheduler_events = {
   # "cron": {
      #      "00 9 * * *": [
       #         "pcprocess_customizations.schedulers.send_quotation_followup_mails",
        #        "pcprocess_customizations.schedulers.send_purchase_order_first_notification",
         #       "pcprocess_customizations.schedulers.send_purchase_order_final_notification"
          #  ]
#        },

    # "daily": [
#         "manufacturer_customizations.schedulers.send_notification_for_shelf_life_in_days_items",
#         "manufacturer_customizations.schedulers.send_notification_for_asset_maintenance",
#         "manufacturer_customizations.schedulers.send_docket_and_courier_details_of_DN"
#     ],
#     "weekly": [
# 		"manufacturer_customizations.schedulers.send_notification_for_SI",
#     ]
# }
# scheduler_events = {
# 	"all": [
# 		"pcprocess_customizations.tasks.all"
# 	],
# 	"daily": [
# 		"pcprocess_customizations.tasks.daily"
# 	],
# 	"hourly": [
# 		"pcprocess_customizations.tasks.hourly"
# 	],
# 	"weekly": [
# 		"pcprocess_customizations.tasks.weekly"
# 	]
# 	"monthly": [
# 		"pcprocess_customizations.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "pcprocess_customizations.install.before_tests"

# Overriding Methods
# ------------------------------
#     

#override_whitelisted_methods = {
    #"erpnext.crm.doctype.lead.lead.make_opportunity":"manufacturer_customizations.manufacturer_customizations.doctype.lead.lead.make_opportunity",
 #   "erpnext.manufacturing.doctype.work_order.work_order.make_stock_entry": "manufacturer_customizations.manufacturer_customizations.doctype.work_order.work_order.make_stock_entry",
  #  }


# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps

override_doctype_dashboards = {
	"Job Card": "manufacturer_customizations.manufacturer_customizations.doctype.job_card.job_card_dashboard.get_data"
}

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]


# User Data Protection
# --------------------

user_data_fields = [
    {
        "doctype": "{doctype_1}",
        "filter_by": "{filter_by}",
        "redact_fields": ["{field_1}", "{field_2}"],
        "partial": 1,
    },
    {
        "doctype": "{doctype_2}",
        "filter_by": "{filter_by}",
        "partial": 1,
    },
    {
        "doctype": "{doctype_3}",
        "strict": False,
    },
    {
        "doctype": "{doctype_4}"
    }
]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"pcprocess_customizations.auth.validate"
# ]
