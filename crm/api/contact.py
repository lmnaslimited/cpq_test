import frappe


def validate(doc, method):
	set_primary_email(doc)
	set_primary_mobile_no(doc)
	doc.set_primary_email()
	doc.set_primary("mobile_no")


def set_primary_email(doc):
	if not doc.email_ids:
		return

	if len(doc.email_ids) == 1:
		doc.email_ids[0].is_primary = 1

def set_primary_mobile_no(doc):
	if not doc.phone_nos:
		return

	if len(doc.phone_nos) == 1:
		doc.phone_nos[0].is_primary_mobile_no = 1

@frappe.whitelist()
def create_new(contact, field, value):
	"""Create new email or phone for a contact"""
	if not frappe.has_permission("Contact", "write", contact):
		frappe.throw("Not permitted", frappe.PermissionError)

	contact = frappe.get_doc("Contact", contact)

	if field == "email":
		contact.append("email_ids", {"email_id": value})
	elif field in ("mobile_no", "phone"):
		contact.append("phone_nos", {"phone": value})
	else:
		frappe.throw("Invalid field")

	contact.save()
	return True


@frappe.whitelist()
def set_as_primary(contact, field, value):
	"""Set email or phone as primary for a contact"""
	if not frappe.has_permission("Contact", "write", contact):
		frappe.throw("Not permitted", frappe.PermissionError)

	contact = frappe.get_doc("Contact", contact)

	if field == "email":
		for email in contact.email_ids:
			if email.email_id == value:
				email.is_primary = 1
			else:
				email.is_primary = 0
	elif field in ("mobile_no", "phone"):
		name = "is_primary_mobile_no" if field == "mobile_no" else "is_primary_phone"
		for phone in contact.phone_nos:
			if phone.phone == value:
				phone.set(name, 1)
			else:
				phone.set(name, 0)
	else:
		frappe.throw("Invalid field")

	contact.save()
	return True
