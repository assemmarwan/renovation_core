from frappe.model.db_query import DatabaseQuery
from six import string_types
import json
import frappe


class UpdatedDBQuery(DatabaseQuery):
    def execute(self, query=None, fields=None, filters=None, or_filters=None,
        docstatus=None, group_by=None, order_by=None, limit_start=False,
        limit_page_length=None, as_list=False, with_childnames=False, debug=False,
        ignore_permissions=False, user=None, with_comment_count=False,
        join='left join', distinct=False, start=None, page_length=None, limit=None,
        ignore_ifnull=False, save_user_settings=False, save_user_settings_fields=False,
        update=None, add_total_row=None, user_settings=None, join_relation=None):
        """Join Relation should be like this format:
        {
            "Child DocType": {
                "patent_doctype": "Name of Parent Doctyep or None",
                "parent_field": "parent file like parent",
                "main_field": "Name of Child Field like name",
                "join": "like left join"
            }
        }
        """
        self.join_relation = {}
        if join_relation:
            if isinstance(join_relation, string_types):
                self.join_relation = json.loads(join_relation)
            else:
                self.join_relation = join_relation

        return super(UpdatedDBQuery, self).execute(query=query, fields=fields, filters=filters, or_filters=or_filters,
        docstatus=docstatus, group_by=group_by, order_by=order_by, limit_start=False,
        limit_page_length=limit_page_length, as_list=as_list, with_childnames=with_childnames, debug=debug,
        ignore_permissions=ignore_permissions, user=user, with_comment_count=with_comment_count,
        join=join, distinct=distinct, start=start, page_length=page_length, limit=limit,
        ignore_ifnull=ignore_ifnull, save_user_settings=save_user_settings, save_user_settings_fields=save_user_settings_fields,
        update=update, add_total_row=add_total_row, user_settings=user_settings)

    def prepare_args(self):
        args = super(UpdatedDBQuery, self).prepare_args()
        # query dict
        args.tables = self.tables[0]
        # left join parent, child tables
        for child in self.tables[1:]:
            join_rel = self.join_relation.get(child, {})
            args.tables += " {join} {child} on ({child}.{parent_field} = {main}.{main_field})".format(join=join_rel.get('join', self.join),
                child=child, parent_field=join_rel.get('parent_field', 'parent'), main=join_rel.get('parent_dotype', self.tables[0]), main_field=join_rel.get('main_field', 'name'))
        return args


@frappe.whitelist()
def get_list(doctype, *args, **kwargs):
	'''wrapper for DatabaseQuery'''
	kwargs.pop('cmd', None)
	return UpdatedDBQuery(doctype).execute(None, *args, **kwargs)
