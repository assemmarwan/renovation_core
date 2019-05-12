# -*- coding: utf-8 -*-
# Copyright (c) 2018, Leam Technology Systems and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from six import string_types
import ast
from renovation_core.utils.meta import clear_meta_cache


class RenovationDocField(Document):
    def validate(self):
        if not frappe.get_meta(self.p_doctype).has_field(self.fieldname):
            frappe.throw("Field '{}' not present in parent '{}' DocType".format(self.fieldname, self.p_doctype))

    def autoname(self):
        self.name = self.p_doctype + "-" + self.fieldname


def toggle_enabled(doctype, fieldname, enabled=0):
    clear_meta_cache(doctype)
    # get doc 
    existing = frappe.get_list("Renovation DocField", filters={
        "p_doctype": doctype,
        "fieldname": fieldname,
    })
    
    if existing:
        doc = frappe.get_doc("Renovation DocField", existing[0].name)
    else:
        doc = frappe.new_doc("Renovation DocField")
        doc.p_doctype = doctype
        doc.fieldname = fieldname
    
    doc.renovation_enabled = enabled
    doc.save()


@frappe.whitelist()
def add_all_reqd_table_fields(doctypes=None):
    if not doctypes:
        doctypes = [x.name for x in frappe.get_all("DocType")]
    elif isinstance(doctypes, string_types):
        if doctypes.startswith('['):
            doctypes = ast.literal_eval(doctypes)
        else:
            doctypes = [doctypes]
    existing_fields = {}
    for f in frappe.get_all("Renovation DocField", fields=['fieldname', 'p_doctype']):
        if not existing_fields.get(f.p_doctype):
            existing_fields[f.p_doctype] = []
        existing_fields[f.p_doctype].append(f.fieldname)
    batch_size = 50
    for i in range(0, len(doctypes), batch_size):
        for doctype in doctypes[i:i + batch_size]:
            meta = frappe.get_meta(doctype)
            fields = [[f.fieldname, f.name]  for f in meta.get("fields") if f.get('fieldname')]
            for field in fields:
                if field[0] in existing_fields.get(doctype, []):
                    continue
                doc = frappe.new_doc('Renovation DocField')
                doc.update({
                    "fieldname": field[0],
                    "p_doctype": doctype,
                    "reference_id": field[1]
                })
                doc.insert()
        frappe.db.commit()