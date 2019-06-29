import frappe


@frappe.whitelist(allow_guest=True)
def get_all_dashboard_meta(user=None, **kwargs):
    return get_all_dashboard_data(user, True, **kwargs)


@frappe.whitelist(allow_guest=True)
def get_all_dashboards(user=None, **kwargs):
    return get_all_dashboard_data(user, False, **kwargs)


def get_all_dashboard_data(user=None, meta=False, **kwargs):
    dashboards = get_permitted_dashboard(user=user)
    all_dashboards={}
    for d in dashboards.keys():
        all_dashboards[d] = get_dashboard(d, user, meta, dashboards)
    return all_dashboards


@frappe.whitelist(allow_guest=True)
def get_dashboard_data(dashboard, user=None, no_meta=False, **kwargs):
    if no_meta:
        return get_dashboard(dashboard, user, **kwargs)
    else:
        return {
            "meta": get_dashboard(dashboard, user, True, **kwargs),
            "data": get_dashboard(dashboard, user, **kwargs)
        }


@frappe.whitelist(allow_guest=True)
def get_dashboard(dashboard, user=None, meta=False, dashboards=None, **kwargs):
    if not dashboards:
        dashboards = get_permitted_dashboard(user=user)
    if dashboard not in dashboards.keys():
        raise frappe.PermissionError
    cache_key = dashboard if not meta else "{}_meta".format(dashboard)
    if frappe.cache().hget('dashboard', cache_key):
        return frappe.cache().hget('dashboard', cache_key)
    doc = frappe.get_doc("Renovation Dashboard", dashboard)
    if meta:
        data = doc.get_chart_meta(**kwargs)
    else:
        data = doc.ready_chart_data(**kwargs)
    frappe.cache().hset('dashboard', cache_key, data)
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


def clear_cache_on_doc_events(doc, method):
    if doc.doctype == "Renovation Dashboard":
        frappe.cache().hdel('dashboard', "%s_meta"%doc.name)
    else:
        for dashboard in get_dashboards_for_clear_cahe(doc.doctype):
            frappe.cache().hdel('dashboard', dashboard)


def get_dashboards_for_clear_cahe(doctype):
    cache_key = '_{}_puge_cache'.format(doctype)
    if frappe.cache().hget('dashboard', cache_key):
        return frappe.cache().hget('dashboard', cache_key)
    data = [x.parent for x in frappe.get_all('Renovation Purge Cache', {'link_doctype': doctype, 'parenttype': 'Renovation Dashboard'}, 'parent')]
    frappe.cache().hset('dashboard', cache_key, data)
    return data
