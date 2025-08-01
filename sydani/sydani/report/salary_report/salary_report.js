
// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.query_reports["Salary Report"] = {
	"filters": [
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company"),
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
			fieldname: "payroll_period",
			label: __("Payroll Period"),
			fieldtype: "Link",
			options: "Payroll Period",
			reqd: 0,
			get_data: function () {
				return frappe.db.get_list('Payroll Period', {
					fields: ['name'],
					order_by: 'creation desc',
					limit: 1
				}).then((result) => {
					if (result.length) {
						return result[0].name;
					}
					return null;
				});
			}
		},
		{
			fieldname: "reportss",
			label: __("Report"),
			fieldtype: "Select",
			options: [
				{ "value": "Summary", "label": __("Summary") },
				{ "value": "Detailed", "label": __("Detailed") },
				{ "value": "Pension", "label": __("Pension") },
				{ "value": "Pay As You Earn", "label": __("Pay As You Earn") },
				{ "value": "National Housing Fund", "label": __("National Housing Fund") }
			],
			default: "Summary",
			reqd: 1
		},
		{
			fieldname: "department",
			label: __("Department"),
			fieldtype: "Link",
			options: "Department",
			reqd: 0
		},
		{
			fieldname: "employee",
			label: __("Employee"),
			fieldtype: "Link",
			options: "Employee",
			reqd: 0
		},
		{
			fieldname: "designation",
			label: __("Designation"),
			fieldtype: "Link",
			options: "Designation",
			reqd: 0
		},
	],

	"formatter": function (value, row, column, data, default_formatter) {
		// Retain the original formatted value
		let formatted_value = default_formatter(value, row, column, data);

		// Color formatting for standard columns
		if (column.fieldname == "gross_pay") {
			formatted_value = `<span style='color:green'>${formatted_value}</span>`;
		} else if (column.fieldname == "net_pay") {
			formatted_value = `<span style='color:blue'>${formatted_value}</span>`;
		} else if (column.fieldname == "total_deduction") {
			formatted_value = `<span style='color:red'>${formatted_value}</span>`;
		}

		// Dynamic color formatting for Salary Components
		if (data && data.salary_components && data.salary_components[column.fieldname]) {
			let component = data.salary_components[column.fieldname];
			if (component.type === "Earning" && component.do_not_include_in_total == 0) {
				formatted_value = `<span style='color:green'>${formatted_value}</span>`;
			} else if (component.type === "Deduction") {
				formatted_value = `<span style='color:red'>${formatted_value}</span>`;
			}
		}

		return formatted_value;
	},

	onload: function (report) {
		// Fetch the most recently created Payroll Period and set it as the default
		frappe.db.get_list('Payroll Period', {
			fields: ['name'],
			order_by: 'creation desc',
			limit: 1
		}).then((result) => {
			if (result.length) {
				const payroll_period_filter = report.get_filter('payroll_period');
				// payroll_period_filter.set_input(result[0].name);
				report.set_filter_value('payroll_period', result[0].name);

			}
		});

		// Set the default currency based on the selected company's default currency
		const company = frappe.query_report.get_filter_value('company');
		if (company) {
			frappe.db.get_value('Company', company, 'default_currency')
				.then(r => {
					const default_currency = r.message.default_currency;
					if (default_currency) {
						frappe.query_report.set_filter_value('currency', default_currency);
					}
				});
		}
	}
};
