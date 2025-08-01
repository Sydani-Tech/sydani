// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Workplan Leadership Board"] = {
	"filters": [
		{
			"fieldname": "employee",
			"label": __("Employee"),
			"fieldtype": "Link",
			"options": "Employee",
			// "default": frappe.defaults.get_user_default("Company")
		},
		{
			"fieldname": "company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			// "default": frappe.defaults.get_user_default("Company")
		},
		{
			"fieldname": "present_cadre",
			"label": __("Present Cadre"),
			"fieldtype": "Link",
			"options": "Designation",
			// "default": frappe.defaults.get_user_default("Company")
		},
		{
			"fieldname": "department",
			"label": __("Department"),
			"fieldtype": "Link",
			"options": "Department",
			// "default": frappe.defaults.get_user_default("Company")
		},
		{
			"fieldname": "date_range",
			"label": __("Date Range"),
			"fieldtype": "Select",
			// "options": ["Last Week\nLast 1 Month\n Last 3 Months\nLast 6 Months\nLast 1 Year\nAll Time Record"],
			"options": [
				"Last Week",
				"Last 1 Month",
				"Last 3 Months",
				"Last 6 Months",
				"Last 1 Year",
				"All Time Record"
			],
			"default": "Last 1 Month" // Set the default filter option here
		},
		{
			"fieldname": "start_date2",
			"label": __("Start Date"),
			"fieldtype": "Date",
			// "options": "Department",
			// "default": frappe.defaults.get_user_default("Company")
		},
		{
			"fieldname": "end_date2",
			"label": __("End Date"),
			"fieldtype": "Date",
			// "options": "Department",
			// "default": frappe.defaults.get_user_default("Company")
		}

	]

};
