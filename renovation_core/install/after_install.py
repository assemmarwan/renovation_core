from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
def after_install():
    make_app_field_in_custom_field_and_property_setter()
    make_app_field_in_custom_field_and_property_setter()


def make_app_field_in_custom_field_and_property_setter():
    create_custom_fields({
        "Custom Field": {
            "fieldname": "app_name",
            "label": "App Name",
            "fieldtype": "Data",
            "insert_after": "dt",
            "print_hide": 1,
            "options": ""
        },
        "Property Setter": {
            "fieldname": "app_name",
            "label": "App Name",
            "fieldtype": "Data",
            "insert_after": "doc_type",
            "print_hide": 1,
            "options": ""
        }
    })