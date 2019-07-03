import frappe, jwt

@frappe.whitelist(allow_guest=True)
def get_user_info(token=None, sid=None):

  if token:
    token_info = jwt.decode(token, frappe.utils.password.get_encryption_key())
    frappe.form_dict['sid'] = token_info.get('sid')


  from frappe.sessions import Session

  # sid is obtained from frappe.form_dict.sid (which is present here)
  # sessions.py LN#183
  session = Session(None, resume=True).get_session_data()
  return {
    'user': session.user,
    'sid': frappe.session.sid
  }