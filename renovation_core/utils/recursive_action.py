from __future__ import unicode_literals

import frappe
from frappe.desk.form.linked_with import get_linked_doctypes, get_linked_docs


ignore_doctypes = frappe.model.meta.Meta.special_doctypes + ('Activity Log', 'DocPerm')


@frappe.whitelist()
def recursive_delete(doctype, docname, **kwargs):
    if not frappe.permissions.has_permission(doctype, 'recursive_delete'):
        raise frappe.PermissionError
    if not frappe.db.exists(doctype, docname):
        return
    docs = get_related_doc_tree(doctype, docname)
    try:
        delete_recursively(docs, kwargs.get('force', 0))
        response = "Succes"
    except Exception as identifier:
        print(identifier)
        frappe.log_error(identifier)
        frappe.db.rollback()
        response = "Fail"
    return response

def delete_recursively(links, force=0):
    for d_type, values in links.items():
        for v in values:
            if v.get('related_docs'):
                delete_recursively(v['related_docs'], force)
            if not frappe.db.exists(d_type, v.name) or d_type in frappe.model.meta.Meta.special_doctypes + ('Activity Log',):
                continue
            do = frappe.get_doc(d_type, v.name)
            if do.docstatus == 1:
                do.cancel()
            frappe.delete_doc(do.doctype, do.name, force, flags=do.flags)


@frappe.whitelist()
def get_related_doc_tree(doctype, docname):
    docs = frappe._dict({doctype: [frappe._dict({
        "name": docname,
        "doctype": doctype,
        "related_docs": frappe._dict()
    })]})
    linked_docs(docs[doctype][0].related_docs, doctype, docname)
    return docs


def linked_docs(links_documents, doctype, docname):
    if doctype in ignore_doctypes:
        return
    linkinfo = get_linked_doctypes(doctype)
    links = get_linked_docs(doctype, docname, linkinfo)
    for d_type, doc_v in links.items():
        if d_type in ignore_doctypes:
            continue
        for c in doc_v:
            row = frappe._dict({
                "name": c['name'],
                "doctype": d_type,
                "related_docs": frappe._dict()
            })
            d = links_documents.setdefault(d_type, [])
            d.append(row)
            linked_docs(row.related_docs, d_type, row.name)
    return links_documents
