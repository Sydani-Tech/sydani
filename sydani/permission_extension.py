# import frappe


# @frappe.whitelist()
# def check_user_permission(doctype, docname, ptype="read"):
#     user = frappe.session.user
#     has_perm = frappe.permissions.has_permission(
#         doctype=doctype, ptype=ptype, doc=frappe.get_doc(doctype, docname), user=user
#     )
#     return has_perm


# import frappe
# from frappe.core.doctype.user_permission.user_permission import has_user_permission


# @frappe.whitelist()
# def check_user_permission(doctype, docname, ptype="read"):
#     user = frappe.session.user
#     doc = frappe.get_doc(doctype, docname)

#     # Check user permission first
#     if not has_user_permission(doc, user=user):
#         frappe.logger().info(
#             f"User {user} does not have user-specific permission for document {docname}"
#         )
#         return False

#     # If user permission passes, check the general permission
#     has_perm = frappe.permissions.has_permission(
#         doctype=doctype, ptype=ptype, doc=doc, user=user
#     )

#     frappe.logger().info(
#         f"Checking permission for user: {user}, doctype: {doctype}, docname: {docname}, permission type: {ptype}, result: {has_perm}"
#     )
#     return has_perm


import frappe


@frappe.whitelist()
def check_custom_user_permission(doctype, docname):
    user = frappe.session.user

    if user == "Administrator":
        return True

    # Fetch User Permission records for the logged-in user where allow = 'Employee'
    user_permissions = frappe.get_all(
        "User Permission",
        filters={"user": user, "allow": "Employee", "apply_to_all_doctypes": 1},
        fields=["for_value", "apply_to_all_doctypes"],
    )

    # If no records found, grant access
    if not user_permissions:
        # frappe.logger().info(
        #     f'No User Permission records found for user {user} with allow="Employee". Granting access.'
        # )
        return True

    # Check if any record has for_value matching the document name
    for permission in user_permissions:
        if permission.for_value == docname and permission.apply_to_all_doctypes:
            # frappe.logger().info(f"User {user} has permission for document {docname}.")
            return True
        if (
            permission.for_value == docname
            and not permission.apply_to_all_doctypes
            and permission.applicable_for == "Employee"
        ):
            # frappe.logger().info(f"User {user} has permission for document {docname}.")
            return True

    # If no matching record is found, deny access
    # frappe.logger().info(
    #     f"User {user} does not have permission for document {docname}."
    # )
    return False
