from frappe import throw, _, msgprint
import frappe
from six import string_types
from frappe.core.doctype.sms_settings.sms_settings import get_headers, create_sms_log, send_request


def validate_receiver_nos(receiver_list):
	validated_receiver_list = []
	for d in receiver_list:
		# remove invalid character
		for x in [' ', '-', '(', ')']:
			d = d.replace(x, '')

		validated_receiver_list.append(d)

	if not validated_receiver_list:
		throw(_("Please enter valid mobile nos"))
	return validated_receiver_list


@frappe.whitelist()
def send_sms(receiver_list, msg, sender_name = '', success_msg = True):

	import json
	if isinstance(receiver_list, string_types):
		receiver_list = json.loads(receiver_list)
		if not isinstance(receiver_list, list):
			receiver_list = [receiver_list]

	receiver_list = validate_receiver_nos(receiver_list)

	arg = {
		'receiver_list' : receiver_list,
		'message'		: frappe.safe_decode(msg).encode('utf-8'),
		'success_msg'	: success_msg
	}

	if frappe.db.get_value('SMS Settings', None, 'sms_gateway_url'):
		return send_via_gateway(arg)
	else:
		msgprint(_("Please Update SMS Settings"))
		return "Fail"

def send_via_gateway(arg):
	ss = frappe.get_doc('SMS Settings', 'SMS Settings')
	headers = get_headers(ss)

	args = {ss.message_parameter: arg.get('message')}
	for d in ss.get("parameters"):
		if not d.header:
			args[d.parameter] = d.value

	success_list = []
	for d in arg.get('receiver_list'):
		args[ss.receiver_parameter] = d
		status = send_request(ss.sms_gateway_url, args, headers, ss.use_post)

		if 200 <= status < 300:
			success_list.append(d)

	if len(success_list) > 0:
		args.update(arg)
		create_sms_log(args, success_list)
		if arg.get('success_msg'):
			frappe.msgprint(_("SMS sent to following numbers: {0}").format("\n" + "\n".join(success_list)))
	return success_list
