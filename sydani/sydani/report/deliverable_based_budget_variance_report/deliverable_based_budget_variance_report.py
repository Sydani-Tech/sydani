# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

import datetime
import frappe
from frappe import _
from frappe.utils import flt, formatdate
from six import iteritems

from erpnext.controllers.trends import get_period_date_ranges, get_period_month_ranges

def execute(filters=None):
    if not filters:
        filters = {}

    columns = get_columns(filters)
    if filters.get("budget_against_filter"):
        dimensions = filters.get("budget_against_filter")
    else:
        dimensions = get_cost_centers(filters)

    period_month_ranges = get_period_month_ranges(filters["period"], filters["from_fiscal_year"])
    cam_map = get_dimension_account_month_map(filters)

    data = []
    for dimension in dimensions:
        dimension_items = cam_map.get(dimension)
        if dimension_items:
            data = get_final_data(dimension, dimension_items, filters, period_month_ranges, data, 0)
        else:
            DCC_allocation = frappe.db.sql('''SELECT parent, sum(percentage_allocation) as percentage_allocation
                FROM `tabDistributed Cost Center`
                WHERE cost_center IN %(dimension)s
                AND parent NOT IN %(dimension)s
                GROUP BY parent''', {'dimension': [dimension]})
            if DCC_allocation:
                filters['budget_against_filter'] = [DCC_allocation[0][0]]
                ddc_cam_map = get_dimension_account_month_map(filters)
                dimension_items = ddc_cam_map.get(DCC_allocation[0][0])
                if dimension_items:
                    data = get_final_data(dimension, dimension_items, filters, period_month_ranges, data, DCC_allocation[0][1])

    # chart = get_chart_data(filters, columns, data)
    chart = get_chart_data_by_deliverable(filters, columns, data)
    return columns, data, None, chart

# def execute(filters=None):
#     if not filters:
#         filters = {}

#     columns = get_columns(filters)

#     if filters.get("budget_against_filter"):
#         dimensions = filters.get("budget_against_filter")
#     else:
#         dimensions = get_cost_centers(filters)

#     period_month_ranges = get_period_month_ranges(filters["period"], filters["from_fiscal_year"])
#     cam_map = get_dimension_account_month_map(filters)

#     data = []
#     for dimension in dimensions:
#         dimension_items = cam_map.get(dimension)
#         if dimension_items:
#             data = get_final_data(dimension, dimension_items, filters, period_month_ranges, data, 0)
#         else:
#             DCC_allocation = frappe.db.sql('''SELECT parent, sum(percentage_allocation) as percentage_allocation
#                 FROM `tabDistributed Cost Center`
#                 WHERE cost_center IN %(dimension)s
#                 AND parent NOT IN %(dimension)s
#                 GROUP BY parent''', {'dimension': [dimension]})
#             if DCC_allocation:
#                 filters['budget_against_filter'] = [DCC_allocation[0][0]]
#                 ddc_cam_map = get_dimension_account_month_map(filters)
#                 dimension_items = ddc_cam_map.get(DCC_allocation[0][0])
#                 if dimension_items:
#                     data = get_final_data(dimension, dimension_items, filters, period_month_ranges, data, DCC_allocation[0][1])

#     chart = get_chart_data(filters, columns, data)
#     return columns, data, None, chart


def get_final_data(dimension, dimension_items, filters, period_month_ranges, data, DCC_allocation):
	for account, deliverables in iteritems(dimension_items):
		for deliverable, monthwise_data in iteritems(deliverables):
			row = [dimension, deliverable, account]
			totals = [0, 0, 0]
			for year in get_fiscal_years(filters):
				last_total = 0
				for relevant_months in period_month_ranges:
					period_data = [0, 0, 0]
					for month in relevant_months:
						if monthwise_data.get(year[0]):
							month_data = monthwise_data.get(year[0]).get(month, {})
							for i, fieldname in enumerate(["target", "actual", "variance"]):
								value = flt(month_data.get(fieldname))
								period_data[i] += value
								totals[i] += value

					period_data[0] += last_total

					if DCC_allocation:
						period_data[0] = period_data[0] * (DCC_allocation / 100)
						period_data[1] = period_data[1] * (DCC_allocation / 100)

					if filters.get("show_cumulative"):
						last_total = period_data[0] - period_data[1]

					period_data[2] = period_data[0] - period_data[1]
					row += period_data
			totals[2] = totals[0] - totals[1]
			if filters["period"] != "Yearly":
				row += totals
			data.append(row)

	return data

# def get_final_data(dimension, dimension_items, filters, period_month_ranges, data, DCC_allocation):
#     for account, monthwise_data in dimension_items.items():
#         deliverable = ""
#         row = [dimension, deliverable, account]
#         totals = [0, 0, 0, 0]  # Updated to include a total for Percentage Spend

#         for year in get_fiscal_years(filters):
#             last_total = 0
#             for relevant_months in period_month_ranges:
#                 period_data = [0, 0, 0, 0]  # Updated to include Percentage Spend
#                 for month in relevant_months:
#                     if monthwise_data.get(year[0]):
#                         month_data = monthwise_data.get(year[0]).get(month, {})
#                         for i, fieldname in enumerate(["target", "actual", "variance"]):
#                             value = flt(month_data.get(fieldname))
#                             period_data[i] += value
#                             totals[i] += value
#                         if month_data.get("deliverable"):
#                             deliverable = month_data.get("deliverable")

#                 period_data[0] += last_total

#                 if DCC_allocation:
#                     period_data[0] = period_data[0] * (DCC_allocation / 100)
#                     period_data[1] = period_data[1] * (DCC_allocation / 100)

#                 if filters.get("show_cumulative"):
#                     last_total = period_data[0] - period_data[1]

#                 period_data[2] = period_data[0] - period_data[1]
                
#                 # Calculate Percentage Spend
#                 if period_data[0] > 0:
#                     period_data[3] = (period_data[1] / period_data[0]) * 100
#                 else:
#                     period_data[3] = 0
                
#                 row += period_data

#         totals[2] = totals[0] - totals[1]
#         if totals[0] > 0:
#             totals[3] = (totals[1] / totals[0]) * 100
#         else:
#             totals[3] = 0

#         if filters["period"] != "Yearly":
#             row += totals

#         row[1] = deliverable  # Set deliverable in the row
#         data.append(row)

#     return data


# def get_columns(filters):
#     columns = [
#         {
#             'label': _(filters.get("budget_against")),
#             'fieldtype': 'Link',
#             'fieldname': 'budget_against',
#             'options': filters.get('budget_against'),
#             'width': 150
#         },
#         {
#             'label': _('Deliverable'),
#             'fieldname': 'deliverable',
#             'fieldtype': 'Data',
#             'width': 150
#         },
#         {
#             'label': _('Account'),
#             'fieldname': 'account',
#             'fieldtype': 'Link',
#             'options': 'Account',
#             'width': 150
#         }
#     ]

#     group_months = False if filters["period"] == "Monthly" else True

#     fiscal_year = get_fiscal_years(filters)

#     for year in fiscal_year:
#         for from_date, to_date in get_period_date_ranges(filters["period"], year[0]):
#             if filters["period"] == "Yearly":
#                 labels = [
#                     _("Budget") + " " + str(year[0]),
#                     _("Actual") + " " + str(year[0]),
#                     _("Variance") + " " + str(year[0]),
#                     _("Percentage Spend") + " " + str(year[0])
#                 ]
#                 for label in labels:
#                     columns.append({
#                         'label': label,
#                         'fieldtype': 'Float',
#                         'fieldname': frappe.scrub(label),
#                         'width': 150
#                     })
#             else:
#                 for label in [
#                     _("Budget") + " (%s)" + " " + str(year[0]),
#                     _("Actual") + " (%s)" + " " + str(year[0]),
#                     _("Variance") + " (%s)" + " " + str(year[0]),
#                     _("Percentage Spend") + " (%s)" + " " + str(year[0])
#                 ]:
#                     if group_months:
#                         label = label % (
#                             formatdate(from_date, format_string="MMM")
#                             + "-"
#                             + formatdate(to_date, format_string="MMM")
#                         )
#                     else:
#                         label = label % formatdate(from_date, format_string="MMM")

#                     columns.append({
#                         'label': label,
#                         'fieldtype': 'Float',
#                         'fieldname': frappe.scrub(label),
#                         'width': 150
#                     })

#     if filters["period"] != "Yearly":
#         for label in [_("Total Budget"), _("Total Actual"), _("Total Variance"), _("Total Percentage Spend")]:
#             columns.append({
#                 'label': label,
#                 'fieldtype': 'Float',
#                 'fieldname': frappe.scrub(label),
#                 'width': 150
#             })

#     return columns



def get_columns(filters):
	columns = [
		{
			'label': _(filters.get("budget_against")),
			'fieldtype': 'Link',
			'fieldname': 'budget_against',
			'options': filters.get('budget_against'),
			'width': 150
		},
		# {
		# 	'label': _('Account'),
		# 	'fieldname': 'Account',
		# 	'fieldtype': 'Link',
		# 	'options': 'Account',
		# 	'width': 200
		# },
		# {
		# 	'label': _('Deliverable'),
		# 	'fieldname': 'Deliverable',
		# 	'fieldtype': 'Data',
		# 	'width': 250
		# }
		{
			'label': _('Deliverable'),
			'fieldname': 'Account',
			'fieldtype': 'Link',
			'options': 'Account',
			'width': 250
		},
		{
			'label': _('Account'),
			'fieldname': 'Deliverable',
			'fieldtype': 'Data',
			'width': 200
		}
	]

	group_months = False if filters["period"] == "Monthly" else True

	fiscal_year = get_fiscal_years(filters)

	for year in fiscal_year:
		for from_date, to_date in get_period_date_ranges(filters["period"], year[0]):
			if filters["period"] == "Yearly":
				labels = [
					_("Budget") + " " + str(year[0]),
					_("Actual") + " " + str(year[0]),
					_("Variance") + " " + str(year[0])
				]
				for label in labels:
					columns.append({
						'label': label,
						'fieldtype': 'Float',
						'fieldname': frappe.scrub(label),
						'width': 150
					})
			else:
				for label in [
					_("Budget") + " (%s)" + " " + str(year[0]),
					_("Actual") + " (%s)" + " " + str(year[0]),
					_("Variance") + " (%s)" + " " + str(year[0])
				]:
					if group_months:
						label = label % (
							formatdate(from_date, format_string="MMM")
							+ "-"
							+ formatdate(to_date, format_string="MMM")
						)
					else:
						label = label % formatdate(from_date, format_string="MMM")

					columns.append({
						'label': label,
						'fieldtype': 'Float',
						'fieldname': frappe.scrub(label),
						'width': 150
					})

	if filters["period"] != "Yearly":
		for label in [_("Total Budget"), _("Total Actual"), _("Total Variance")]:
			columns.append({
				'label': label,
				'fieldtype': 'Float',
				'fieldname': frappe.scrub(label),
				'width': 150
			})

	return columns

def get_cost_centers(filters):
	order_by = ""
	if filters.get("budget_against") == "Cost Center":
		order_by = "order by lft"

	if filters.get("budget_against") in ["Cost Center", "Project"]:
		return frappe.db.sql_list(
			"""
				select
					name
				from
					`tab{tab}`
				where
					company = %s
				{order_by}
			""".format(tab=filters.get("budget_against"), order_by=order_by),
			filters.get("company"))
	else:
		return frappe.db.sql_list(
			"""
				select
					name
				from
					`tab{tab}`
			""".format(tab=filters.get("budget_against")))  # nosec

# Get dimension & target details
def get_dimension_target_details(filters):
	budget_against = frappe.scrub(filters.get("budget_against"))
	cond = ""
	if filters.get("budget_against_filter"):
		cond += """ and b.{budget_against} in (%s)""".format(
			budget_against=budget_against) % ", ".join(["%s"] * len(filters.get("budget_against_filter")))

	return frappe.db.sql(
		"""
			select
				b.{budget_against} as budget_against,
				b.monthly_distribution,
				ba.account,
				ba.budget_amount,
				ba.deliverable,
				b.fiscal_year
			from
				`tabBudget` b,
				`tabDeliverable Based Budget` ba
			where
				b.name = ba.parent
				and b.docstatus = 1
				and b.fiscal_year between %s and %s
				and b.budget_against = %s
				and b.company = %s
				{cond}
			order by
				b.fiscal_year
		""".format(
			budget_against=budget_against,
			cond=cond,
		),
		tuple(
			[
				filters.from_fiscal_year,
				filters.to_fiscal_year,
				filters.budget_against,
				filters.company,
			]
			+ (filters.get("budget_against_filter") or [])
		), as_dict=True)

# Get target distribution details of accounts of cost center
def get_target_distribution_details(filters):
	target_details = {}
	for d in frappe.db.sql(
		"""
			select
				md.name,
				mdp.month,
				mdp.percentage_allocation
			from
				`tabMonthly Distribution Percentage` mdp,
				`tabMonthly Distribution` md
			where
				mdp.parent = md.name
				and md.fiscal_year between %s and %s
			order by
				md.fiscal_year
		""",
		(filters.from_fiscal_year, filters.to_fiscal_year), as_dict=1):
		target_details.setdefault(d.name, {}).setdefault(
			d.month, flt(d.percentage_allocation)
		)

	return target_details

def get_actual_details(name, filters):
	budget_against = frappe.scrub(filters.get("budget_against"))
	cond = ""

	if filters.get("budget_against") == "Cost Center":
		cc_lft, cc_rgt = frappe.db.get_value("Cost Center", name, ["lft", "rgt"])
		cond = """
				and lft >= "{lft}"
				and rgt <= "{rgt}"
			""".format(lft=cc_lft, rgt=cc_rgt)

	ac_details = frappe.db.sql(
		"""
			select
				gl.account,
				gl.debit,
				gl.credit,
				gl.fiscal_year,
				MONTHNAME(gl.posting_date) as month_name,
				b.{budget_against} as budget_against,
				case when gl.voucher_type = 'Purchase Invoice' then pii.deliverable else '' end as deliverable
			from
				`tabGL Entry` gl
				left join `tabPurchase Invoice` pi on pi.name = gl.voucher_no and gl.voucher_type = 'Purchase Invoice'
				left join `tabPurchase Invoice Item` pii on pii.parent = pi.name
				,`tabDeliverable Based Budget` ba,
				`tabBudget` b
			where
				b.name = ba.parent
				and b.docstatus = 1
				and ba.account = gl.account
				and b.{budget_against} = gl.{budget_against}
				and gl.fiscal_year between %s and %s
				and b.{budget_against} = %s
				and exists(
					select
						name
					from
						`tab{tab}`
					where
						name = gl.{budget_against}
						{cond}
				)
				group by
					gl.name
				order by gl.fiscal_year
		""".format(tab=filters.budget_against, budget_against=budget_against, cond=cond),
		(filters.from_fiscal_year, filters.to_fiscal_year, name), as_dict=1)

	cc_actual_details = {}
	for d in ac_details:
		deliverable = d.deliverable or 'Not Specified'
		cc_actual_details.setdefault(d.account, {}).setdefault(deliverable, []).append(d)

	return cc_actual_details


def get_dimension_account_month_map(filters):
	dimension_target_details = get_dimension_target_details(filters)
	tdd = get_target_distribution_details(filters)

	cam_map = {}

	for ccd in dimension_target_details:
		actual_details = get_actual_details(ccd.budget_against, filters)

		for month_id in range(1, 13):
			month = datetime.date(2013, month_id, 1).strftime("%B")
			cam_map.setdefault(ccd.budget_against, {}).setdefault(
				ccd.account, {}
			).setdefault(ccd.deliverable, {}).setdefault(
				ccd.fiscal_year, {}
			).setdefault(
				month, frappe._dict({"target": 0.0, "actual": 0.0})
			)

			tav_dict = cam_map[ccd.budget_against][ccd.account][ccd.deliverable][ccd.fiscal_year][month]
			month_percentage = (
				tdd.get(ccd.monthly_distribution, {}).get(month, 0)
				if ccd.monthly_distribution
				else 100.0 / 12
			)

			tav_dict.target = flt(ccd.budget_amount) * month_percentage / 100

			for ad in actual_details.get(ccd.account, {}).get(ccd.deliverable, []):
				if ad.month_name == month and ad.fiscal_year == ccd.fiscal_year:
					tav_dict.actual += flt(ad.debit) - flt(ad.credit)

	return cam_map

def get_fiscal_years(filters):
	fiscal_year = frappe.db.sql(
		"""
			select
				name
			from
				`tabFiscal Year`
			where
				name between %(from_fiscal_year)s and %(to_fiscal_year)s
		""",
		{
			"from_fiscal_year": filters["from_fiscal_year"],
			"to_fiscal_year": filters["to_fiscal_year"]
		})

	return fiscal_year


def get_chart_data(filters, columns, data):

    if not data:
        return None

    labels = []

    fiscal_year = get_fiscal_years(filters)
    group_months = False if filters["period"] == "Monthly" else True

    for year in fiscal_year:
        for from_date, to_date in get_period_date_ranges(filters["period"], year[0]):
            if filters['period'] == 'Yearly':
                labels.append(year[0])
            else:
                if group_months:
                    label = formatdate(from_date, format_string="MMM") + "-" \
                            + formatdate(to_date, format_string="MMM")
                    labels.append(label)
                else:
                    label = formatdate(from_date, format_string="MMM")
                    labels.append(label)

    # frappe.msgprint(_("Generated Labels: {0}").format(labels))  # Debugging message

    no_of_columns = len(labels)

    budget_values, actual_values = [0] * no_of_columns, [0] * no_of_columns

    for d in data:
        values = d[3:]  # Adjust index to account for new 'Deliverable' column
        index = 0

        for i in range(no_of_columns):
            budget_values[i] += values[index]
            actual_values[i] += values[index + 1]
            index += 3  # Assuming budget, actual, variance structure in each set of data

    # frappe.msgprint(_("Budget Values: {0}").format(budget_values))  # Debugging message
    # frappe.msgprint(_("Actual Values: {0}").format(actual_values))  # Debugging message

    return {
        'data': {
            'labels': labels,
            'datasets': [
                {'name': 'Budget', 'chartType': 'bar', 'values': budget_values},
                {'name': 'Actual Expense', 'chartType': 'bar', 'values': actual_values}
            ]
        },
        'type': 'bar'
    }


# def get_chart_data_by_deliverable(filters, columns, data):
# 	if not data:
# 		return None

# 	labels = []

# 	fiscal_year = get_fiscal_years(filters)
# 	group_months = False if filters["period"] == "Monthly" else True

# 	for year in fiscal_year:
# 		for from_date, to_date in get_period_date_ranges(filters["period"], year[0]):
# 			if filters['period'] == 'Yearly':
# 				labels.append(year[0])
# 			else:
# 				if group_months:
# 					label = formatdate(from_date, format_string="MMM") + "-" \
# 						+ formatdate(to_date, format_string="MMM")
# 					labels.append(label)
# 				else:
# 					label = formatdate(from_date, format_string="MMM")
# 					labels.append(label)

# 	no_of_columns = len(labels)

# 	deliverable_budget_values, deliverable_actual_values = {}, {}
# 	for d in data:
# 		deliverable = d[2]
# 		values = d[3:]
# 		index = 0

# 		for i in range(no_of_columns):
# 			deliverable_budget_values.setdefault(deliverable, [0] * no_of_columns)[i] += values[index]
# 			deliverable_actual_values.setdefault(deliverable, [0] * no_of_columns)[i] += values[index + 1]
# 			index += 3

# 	datasets = []
# 	for deliverable, budget_values in deliverable_budget_values.items():
# 		datasets.append({'name': f'Budget ({deliverable})', 'chartType': 'bar', 'values': budget_values})

# 	for deliverable, actual_values in deliverable_actual_values.items():
# 		datasets.append({'name': f'Actual Expense ({deliverable})', 'chartType': 'bar', 'values': actual_values})

# 	return {
# 		'data': {
# 			'labels': labels,
# 			'datasets': datasets
# 		},
# 		'type': 'bar'
# 	}


def get_chart_data_by_deliverable(filters, columns, data):
    if not data:
        return None

    deliverable_labels = list(set(row[1] for row in data if row[1]))
    deliverable_labels.sort()
    
    fiscal_year = get_fiscal_years(filters)
    group_months = False if filters["period"] == "Monthly" else True

    labels = []
    for year in fiscal_year:
        for from_date, to_date in get_period_date_ranges(filters["period"], year[0]):
            if filters['period'] == 'Yearly':
                labels.append(year[0])
            else:
                if group_months:
                    label = formatdate(from_date, format_string="MMM") + "-" + formatdate(to_date, format_string="MMM")
                    labels.append(label)
                else:
                    label = formatdate(from_date, format_string="MMM")
                    labels.append(label)

    no_of_columns = len(labels)
    deliverable_budget_values = {label: [0] * no_of_columns for label in deliverable_labels}
    deliverable_actual_values = {label: [0] * no_of_columns for label in deliverable_labels}

    for d in data:
        deliverable = d[1]
        values = d[3:]  # Skip the dimension and account columns
        index = 0

        for i in range(no_of_columns):
            deliverable_budget_values[deliverable][i] += values[index]
            deliverable_actual_values[deliverable][i] += values[index + 1]
            index += 3

    datasets = []
    for deliverable in deliverable_labels:
        datasets.append({'name': f'Budget ({deliverable})', 'chartType': 'bar', 'values': deliverable_budget_values[deliverable]})
        datasets.append({'name': f'Actual Expense ({deliverable})', 'chartType': 'bar', 'values': deliverable_actual_values[deliverable]})

    return {
        'data': {
            'labels': labels,
            'datasets': datasets
        },
        'type': 'bar'
    }
