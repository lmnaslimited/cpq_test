import frappe

def validate(doc, method):
	if doc.type == "Incoming" and doc.get("from"):
		name, doctype = get_lead_or_deal_from_number(doc.get("from"))
		doc.reference_doctype = doctype
		doc.reference_name = name

def get_lead_or_deal_from_number(number):
	"""Get lead/deal from the given number.
	"""

	def find_record(doctype, mobile_no, where=''):
		mobile_no = parse_mobile_no(mobile_no)
		
		query = f"""
			SELECT name, mobile_no
			FROM `tab{doctype}`
			WHERE CONCAT('+', REGEXP_REPLACE(mobile_no, '[^0-9]', '')) = {mobile_no}
		"""

		data = frappe.db.sql(query + where, as_dict=True)
		return data[0].name if data else None

	doctype = "CRM Deal"

	doc = find_record(doctype, number) or None
	if not doc:
		doctype = "CRM Lead"
		doc = find_record(doctype, number, 'AND converted is not True')
		if not doc:
			doc = find_record(doctype, number)

	return doc, doctype

def parse_mobile_no(mobile_no: str):
	"""Parse mobile number to remove spaces, brackets, etc.
	>>> parse_mobile_no('+91 (766) 667 6666')
	... '+917666676666'
	"""
	return ''.join([c for c in mobile_no if c.isdigit() or c == '+'])

@frappe.whitelist()
def create_whatsapp_message(reference_doctype, reference_name, message, to, attach, reply_to, content_type="text"):
	doc = frappe.new_doc("WhatsApp Message")

	if reply_to:
		reply_doc = frappe.get_doc("WhatsApp Message", reply_to)
		doc.update({
			"is_reply": True,
			"reply_to_message_id": reply_doc.message_id,
		})

	doc.update({
		"reference_doctype": reference_doctype,
		"reference_name": reference_name,
		"message": message or attach,
		"to": to,
		"attach": attach,
		"content_type": content_type,
	})
	doc.insert(ignore_permissions=True)
	return doc.name

@frappe.whitelist()
def send_whatsapp_template(reference_doctype, reference_name, template, to):
	doc = frappe.new_doc("WhatsApp Message")
	doc.update({
		"reference_doctype": reference_doctype,
		"reference_name": reference_name,
		"message_type": "Template",
		"message": "Template message",
		"content_type": "text",
		"use_template": True,
		"template": template,
		"to": to,
	})
	doc.insert(ignore_permissions=True)
	return doc.name

@frappe.whitelist()
def react_on_whatsapp_message(emoji, reply_to_name):
	reply_to_doc = frappe.get_doc("WhatsApp Message", reply_to_name)
	to = reply_to_doc.type == "Incoming" and reply_to_doc.get("from") or reply_to_doc.to
	doc = frappe.new_doc("WhatsApp Message")
	doc.update({
		"reference_doctype": reply_to_doc.reference_doctype,
		"reference_name": reply_to_doc.reference_name,
		"message": emoji,
		"to": to,
		"reply_to_message_id": reply_to_doc.message_id,
		"content_type": "reaction",
	})
	doc.insert(ignore_permissions=True)
	return doc.name