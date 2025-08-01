
// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */


frappe.query_reports["Employee Timesheet Report"] = {
	"filters": [
		{
			fieldname: "employee",
			label: __("Employee"),
			fieldtype: "Link",
			options: "Employee",
			reqd: 0,
		},
		{
			fieldname: "project",
			label: __("Project"),
			fieldtype: "Link",
			options: "Project",
			reqd: 0,
		},
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			reqd: 1,
			default: "Sydani Initiative for International Development"
		},
		{
			fieldname: "start_date",
			label: __("Start Date"),
			fieldtype: "Date",
			reqd: 1,
			"default": getStartDate()
		},
		{
			fieldname: "end_date",
			label: __("End Date"),
			fieldtype: "Date",
			reqd: 1,
			"default": getEndDate()
		},
		{
			fieldname: "report_type",
			label: __("Report Type"),
			fieldtype: "Select",
			options: [
				{ "value": "Hours", "label": __("Hours") },
				{ "value": "Percentabe", "label": __("Percentage") }
			],
			default: "Hours",
			reqd: 1
		},
		{
			fieldname: "leavenholiday",
			label: __("Include Leaves & Holidays"),
			fieldtype: "Check",
			// options: [
			// 	{ "value": "Hours", "label": __("Hours") },
			// 	{ "value": "Percentabe", "label": __("Percentage") }
			// ],
			default: 1,

		},
	],



};

function getStartDate() {
	var today = new Date();
	var year = today.getFullYear();
	var month = today.getMonth();

	// If current month is January, then set the previous month as December of the previous year
	if (month === 0) {
		year -= 1;
		month = 11; // December
	} else {
		month -= 1;
	}

	// Set the date to 21st of the previous month
	var startDate = new Date(year, month, 21);

	// Convert to string format "yyyy-mm-dd"
	var formattedStartDate = frappe.datetime.obj_to_str(startDate);

	return formattedStartDate;
}

function getEndDate() {
	var today = new Date();
	var year = today.getFullYear();
	var month = today.getMonth();

	// Set the date to 20th of the current month
	var endDate = new Date(year, month, 20);

	// Convert to string format "yyyy-mm-dd"
	var formattedEndDate = frappe.datetime.obj_to_str(endDate);

	return formattedEndDate;
}
