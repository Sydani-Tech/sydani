// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

// frappe.query_reports["Employee FTE"] = {
// 	"filters": [
// 		{
//             fieldname: "employee",
//             label: __("Employee"),
//             fieldtype: "Link",
//             options: "Employee",
//             reqd: 0,
//         },
//         {
//             fieldname: "employee_status",
//             label: __("Employee Status"),
//             fieldtype: "Select",
//             options: [
//                 { "value": "All", "label": __("All") },
//                 { "value": "Active", "label": __("Active") },
//             ],
//             default: "Active",
//             reqd: 1
//         },
// 		{
//             fieldname: "project",
//             label: __("Project"),
//             fieldtype: "Link",
//             options: "Project",
//             reqd: 0,
//         },
//         {
//             fieldname: "project_status",
//             label: __("Project Status"),
//             fieldtype: "Select",
//             options: [

// 				{ "value": "Ongoing", "label": __("Ongoing") },
// 				{ "value": "All", "label": __("All") },
//             ],
//             default: "Ongoing",
//             reqd: 1
//         },
//         {
//             fieldname: "company",
//             label: __("Company"),
//             fieldtype: "Link",
//             options: "Company",
//             // default: frappe.defaults.get_user_default("Company"),
//             reqd: 0,
// 		},

//     ],
//     };


frappe.query_reports["Employee FTE"] = {
	"filters": [
		{
			fieldname: "employee",
			label: __("Employee"),
			fieldtype: "Link",
			options: "Employee",
			reqd: 0,
		},
		{
			fieldname: "employee_status",
			label: __("Employee Status"),
			fieldtype: "Select",
			options: [
				{ "value": "All", "label": __("All") },
				{ "value": "Active", "label": __("Active") },
			],
			default: "Active",
			reqd: 1
		},
		{
			fieldname: "project",
			label: __("Project"),
			fieldtype: "Link",
			options: "Project",
			reqd: 0,
		},
		{
			fieldname: "project_status",
			label: __("Project Status"),
			fieldtype: "Select",
			options: [
				{ "value": "Ongoing", "label": __("Ongoing") },
				{ "value": "All", "label": __("All") },
			],
			default: "Ongoing",
			reqd: 1
		},
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			reqd: 0,
		}
	],

	"formatter": function (value, row, column, data, default_formatter) {
		// Retain the original formatted value
		let formatted_value = default_formatter(value, row, column, data);

		// Apply conditional formatting for the total_fte column
		if (column.fieldname === "total_fte") {
			if (value >= 0 && value <= 69) {
				formatted_value = `<span style='color: #00cc00;'>${formatted_value}</span>`;
			} else if (value >= 70 && value <= 80) {
				formatted_value = `<span style='color: #99ff66;'>${formatted_value}</span>`;
			} else if (value >= 81 && value <= 100) {
				formatted_value = `<span style='color: #ffcc66;'>${formatted_value}</span>`;
			} else if (value > 100) {
				formatted_value = `<span style='color: #ff1a1a;'>${formatted_value}</span>`;
			} else {
				formatted_value = `<span style='color: #8B0000;'>${formatted_value}</span>`;
			}
		}

		return formatted_value;
	},

	// onload: function(report) {
	//     // Custom logic on report load (if needed)
	// }
};
