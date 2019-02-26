import frappe


@frappe.whitelist()
def get_all_dashboards(user=None, **kwargs):
    dashboards = get_permitted_dashboard()
    all_dashboards={}
    for d in dashboards.keys():
        all_dashboards[d] = get_dashboard(d)
    return all_dashboards


@frappe.whitelist()
def get_dashboard(dashboard, user=None, **kwargs):
    dashboards = get_permitted_dashboard()
    if dashboard not in dashboards.keys():
        raise frappe.PermissionError
    if frappe.cache().hget('dashboard:{}'.format(dashboard), user):
        return frappe.cache().hget('dashboard', dashboard)
    doc = frappe.get_doc("Renovation Dashboard", dashboard)
    data = doc.get_chart_data(**kwargs)
    frappe.cache().hset('dashboard', dashboard, data)
    return data


def get_permitted_dashboard(parent="Renovation Dashboard", user=None):
    if not user: user = frappe.session.user
    if frappe.cache().hget('dashboard_list', user):
        return frappe.cache().hget('dashboard_list', user)
    roles = frappe.get_roles(user)
    has_role = {}
    column = get_column(parent)

    standard_roles = frappe.db.sql("""
        select distinct
            `tab{parent}`.name,
            `tab{parent}`.modified,
            {column}
        from `tabHas Role`, `tab{parent}`
        where
            `tabHas Role`.role in ('{roles}')
            and `tabHas Role`.parent = `tab{parent}`.name
            {condition}
        """.format(parent=parent, column=column, roles = "', '".join(roles),
            field=parent.lower(), condition="and `tab{}`.enable=1".format(parent)), as_dict=True)

    for p in standard_roles:
        if p.name not in has_role:
            has_role[p.name] = {"modified":p.modified, "title": p.title}

    doctype_with_no_roles = frappe.db.sql("""
        select
            `tab{parent}`.name, `tab{parent}`.modified, {column}
        from `tab{parent}`
        where
            (select count(*) from `tabHas Role`
            where `tabHas Role`.parent=`tab{parent}`.name) = 0
    """.format(parent=parent, column=column), as_dict=1)

    for p in doctype_with_no_roles:
        if p.name not in has_role:
            has_role[p.name] = {"modified": p.modified, "title": p.title}

    frappe.cache().hset('dashboard_list', user, has_role)
    return has_role


def get_column(doctype):
    column = "`tab{}`.title as title".format(doctype)
    if doctype == "Renovation Dashboard":
        column = "`tab{0}`.name as name, `tab{0}`.title as title".format(doctype)

    return column
