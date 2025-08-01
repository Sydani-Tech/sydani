// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Request Status Report"] = {
	"filters": [

	]
};

frappe.query_reports["Request Status Report"] = {
	"filters": [
		{
			fieldname: "request_type",
			label: __("Request Type"),
			fieldtype: "Select",
			options: [
				{ "value": "All", "label": __("All") },
				{ "value": "Expense Claim", "label": __("Expense Claim") },
				{ "value": "Employee Travel Request", "label": __("Employee Travel Request") },
				{ "value": "Procurement Request", "label": __("Procurement Request") },
				{ "value": "Procurement Evaluation Sheet", "label": __("Procurement Evaluation Sheet") },
				{ "value": "Capacity Building Fund Request", "label": __("Capacity Building Fund Request") },
			],
			default: "All",
			reqd: 1
		},
		// {
		// 	fieldname: "responsible_party",
		// 	label: __("Responsible Party"),
		// 	fieldtype: "Select",
		// 	options: [
		// 		{ "value": "All", "label": __("All") },
		// 		{ "value": "Admin", "label": __("Admin") },
		// 		{ "value": "Audit", "label": __("Audit") },
		// 		{ "value": "Finance", "label": __("Finance") },
		// 		{ "value": "Procurement", "label": __("Procurement") },
		// 		{ "value": "Manager", "label": __("Manager") },
		// 		{ "value": "Managing Partner", "label": __("Managing Partner") },
		// 	],
		// 	default: "All",
		// 	reqd: 1
		// },
		{
			fieldname: "project",
			label: __("Project"),
			fieldtype: "Link",
			options: "Project",
			reqd: 0
		},
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			// default: frappe.defaults.get_user_default("Company"),
			default: "",
			reqd: 0,
		},
		{
			fieldname: "fiscal_year",
			label: __("Fiscal Year"),
			fieldtype: "Link",
			options: "Fiscal Year",
			default: frappe.sys_defaults.fiscal_year,
			reqd: 0
		},

		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			// default: frappe.datetime.get_today(),
			reqd: 0
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			// default: frappe.datetime.get_today(),
			reqd: 0
		},
		// {
		// 	"fieldname": "max_percentage_paid",
		// 	"label": "Max Percentage Paid",
		// 	"fieldtype": "Float",
		// 	"default": 94
		// }

	],
	"formatter": function (value, row, column, data, default_formatter) {
		// Retain the original formatted value
		let formatted_value = default_formatter(value, row, column, data);

		// Apply conditional formatting for the percentage_paid and percentage_raised columns
		if (column.fieldname === "percentage_paid" || column.fieldname === "percentage_raised") {
			if (value >= 94) {
				formatted_value = `<span style='color: #00cc00;'>${formatted_value}</span>`; // Green
			} else if (value >= 80 && value < 94) {
				formatted_value = `<span style='color: #99ff66;'>${formatted_value}</span>`; // Light green
			} else if (value >= 50 && value < 80) {
				formatted_value = `<span style='color: #ffcc66;'>${formatted_value}</span>`; // Orange
			} else {
				formatted_value = `<span style='color: #8B0000;'>${formatted_value}</span>`; // Dark red
			}
		}

		// Apply number formatting with commas for total-related columns
		if ((column.fieldname === "total") || (column.fieldname === "total_paid") || (column.fieldname === "total_raised")) {
			let numericValue = parseFloat(value);
			if (!isNaN(numericValue)) {
				formatted_value = numericValue.toLocaleString("en-US", {
					minimumFractionDigits: 2,
					maximumFractionDigits: 2
				});
			}
		}

		return formatted_value;
	},
	// "onload": function (report) {
	// 	report.page.add_inner_button("Apply Filter", function () {
	// 		let max_percentage_paid = frappe.query_report.get_filter_value("max_percentage_paid");

	// 		if (max_percentage_paid !== undefined && max_percentage_paid !== null) {
	// 			frappe.query_report.data = frappe.query_report.data.filter(row => {
	// 				return row.percentage_paid < max_percentage_paid;
	// 			});
	// 			frappe.query_report.refresh();
	// 		}
	// 	});
	// },
};
