app_name = "myhealth"
app_title = "Myhealth"
app_publisher = "Karen"
app_description = "Health"
app_email = "karenkagai4@gmail.com"
app_license = "mit"

override_whitelisted_methods = {
    # Appointment API
    "myhealth.myhealth.api.appointment_api.create_appointment": "myhealth.myhealth.api.appointment_api.create_appointment",
    "myhealth.myhealth.api.appointment_api.get_appointments": "myhealth.myhealth.api.appointment_api.get_appointments",
    "myhealth.myhealth.api.appointment_api.update_appointment": "myhealth.myhealth.api.appointment_api.update_appointment",
}

override_whitelisted_methods = {
    # Patient API
    "myhealth.api.patient_api.create_patient": "myhealth.myhealth.api.patient_api.create_patient",
    "myhealth.api.patient_api.get_patient": "myhealth.myhealth.api.patient_api.get_patient",
    "myhealth.api.patient_api.update_patient": "myhealth.myhealth.api.patient_api.update_patient",
    "myhealth.api.patient_api.delete_patient": "myhealth.myhealth.api.patient_api.delete_patient",
    "myhealth.api.patient_api.list_patients": "myhealth.myhealth.api.patient_api.list_patients",
}

doc_events = {}
override_whitelisted_methods = {
    "myhealth.myhealth.api.appointment_api.get_appointment_summary": 
        "myhealth.myhealth.api.appointment_api.get_appointment_summary"
}

override_whitelisted_methods.update({
    "myhealth.myhealth.api.doctor_api.create_doctor": "myhealth.myhealth.api.doctor_api.create_doctor",
    "myhealth.myhealth.api.doctor_api.get_doctors": "myhealth.myhealth.api.doctor_api.get_doctors",
    "myhealth.myhealth.api.doctor_api.update_doctor": "myhealth.myhealth.api.doctor_api.update_doctor",
    "myhealth.myhealth.api.doctor_api.deactivate_doctor": "myhealth.myhealth.api.doctor_api.deactivate_doctor"
})


# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "myhealth",
# 		"logo": "/assets/myhealth/logo.png",
# 		"title": "Myhealth",
# 		"route": "/myhealth",
# 		"has_permission": "myhealth.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/myhealth/css/myhealth.css"
# app_include_js = "/assets/myhealth/js/myhealth.js"

# include js, css files in header of web template
# web_include_css = "/assets/myhealth/css/myhealth.css"
# web_include_js = "/assets/myhealth/js/myhealth.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "myhealth/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "myhealth/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# automatically load and sync documents of this doctype from downstream apps
# importable_doctypes = [doctype_1]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "myhealth.utils.jinja_methods",
# 	"filters": "myhealth.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "myhealth.install.before_install"
# after_install = "myhealth.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "myhealth.uninstall.before_uninstall"
# after_uninstall = "myhealth.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "myhealth.utils.before_app_install"
# after_app_install = "myhealth.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "myhealth.utils.before_app_uninstall"
# after_app_uninstall = "myhealth.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "myhealth.notifications.get_notification_config"

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

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"myhealth.tasks.all"
# 	],
# 	"daily": [
# 		"myhealth.tasks.daily"
# 	],
# 	"hourly": [
# 		"myhealth.tasks.hourly"
# 	],
# 	"weekly": [
# 		"myhealth.tasks.weekly"
# 	],
# 	"monthly": [
# 		"myhealth.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "myhealth.install.before_tests"

# Extend DocType Class
# ------------------------------
#
# Specify custom mixins to extend the standard doctype controller.
# extend_doctype_class = {
# 	"Task": "myhealth.custom.task.CustomTaskMixin"
# }

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "myhealth.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "myhealth.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["myhealth.utils.before_request"]
# after_request = ["myhealth.utils.after_request"]

# Job Events
# ----------
# before_job = ["myhealth.utils.before_job"]
# after_job = ["myhealth.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"myhealth.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

