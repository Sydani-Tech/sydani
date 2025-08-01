frappe.query_reports["Project Timesheet"] = {
	"filters": [
		// {
		//     "fieldname": "employee",
		//     "label": __("Employee"),
		//     "fieldtype": "Link",
		//     "options": "Employee"
		// },
		{
			"fieldname": "project",
			"label": __("Project"),
			"fieldtype": "Link",
			"options": "Project",
			"reqd": 1,
			"default": "Operations (Tech)"
		},
		{
			"fieldname": "start_date",
			"label": __("Start Date"),
			"fieldtype": "Date",
			"reqd": 1,
			"default": getStartDate()
		},
		{
			"fieldname": "end_date",
			"label": __("End Date"),
			"fieldtype": "Date",
			"reqd": 1,
			"default": getEndDate()
		}
	],
	"formatter": function (value, row, column, data, default_formatter) {
		if (column.fieldname === "hourly_rate" || column.fieldname === "billing_amount") {
			return formatCurrency(value, data.currency);
		} else {
			return default_formatter(value, row, column, data);
		}
	}
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

function formatCurrency(value, currency) {
	// Assuming currency is a valid currency code (e.g., USD, EUR)
	var formattedValue = new Intl.NumberFormat('en', { style: 'currency', currency: currency }).format(value);
	return formattedValue;
}
