frappe.provide('renovation');

frappe.pages['DocField Manager'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Renovation DocField Manager',
		single_column: true
	});
	wrapper.docfield_manager = new renovation.DocFieldManager(wrapper);
	frappe.breadcrumbs.add("Renovation Core");
}

renovation.DocFieldManager = Class.extend({
	init: function(wrapper) {
		this.wrapper = wrapper;
		this.page = wrapper.page;
		this.make();
	},
	make: function() {
		this.page.add_field({
			label: 'DocType',
			fieldname: 'doctype',
			fieldtype: 'Link',
			options: 'DocType',
			onchange: () => { this.ondoctype_changed(); } // to have proper this in ondoctype_changed()
		})
	},
	ondoctype_changed: function() {
		if (!this.page.fields_dict['doctype'].value || this.page.fields_dict['doctype'].value === this.doctype) { return; }
		
		
		this.doctype = this.page.fields_dict['doctype'].value;
		let me = this;
		frappe.call({
			module: 'renovation_core.renovation_core',
			page: 'docfield_manager',
			method: 'get_doctype_fields',
			args: {
				doctype: this.doctype
			},
			freeze: true,
			callback(r) {
				if (!r.exc && r.message) {
					me.fields = r.message.meta_fields;
					me.enabled_dict = r.message.enabled_dict;
					me.make_table();
				} else {
					frappe.msgprint("Something went wrong, please try again");
				}
			}
		});
	},
	make_table: function() {
		if (!this.table)
			this.page.add_break();
		
		let me = this;
		let rows = '';
		this.fields.forEach((obj) => {
			rows += 
			'<tr>' +
				'<td width="200px">' + (obj.label || '') + '</td>' +
				'<td>' + obj.fieldname + '</td>' +
				'<td>' + obj.fieldtype + (obj.fieldtype === "Table" ? ' ('+ obj.options +')' : '') + '</td>' +
				'<td>' + 
					'<input class="enabled_check" type="checkbox" ' + 
						'data-fieldname="' + obj.fieldname + '"' + 
						'data-doctype="' + me.doctype + '"' + 
					(this.enabled_dict[obj.fieldname] ? 'checked' : '') + '>'
				'</td>' +
			'</tr>'
		})
		
		let table = // do I get a transpiler here ? :p
		'<table class="renovation_table table table-condensed table-hover table-striped">' +
			'<thead>' +
				'<tr>' +
					'<th>Label</th>' +
					'<th>Field Name</th>' +
					'<th>Field Type</th>' +
					'<th>Enabled</th>' +
				'</tr>' +
			'</thead>' +
			'<tbody>' +
				rows +
			'</tbody>' +
		'</table>'
		;
		this.page.page_form.append(table);
		if (this.table) {
			$('.enabled_check').off("change", this.enabled_change);
			this.table.remove();
		}
		this.table = $('table.renovation_table')[0];
		$('.enabled_check').on("change", this.enabled_change);
	},
	
	enabled_change: function(e) {
			let fieldname = $(this).data('fieldname');
			let doctype = $(this).data('doctype');
			let enabled = this.checked;
			
			frappe.call({
				module: 'renovation_core.renovation_core',
				page: 'docfield_manager',
				method: 'toggle_enabled',
				args: {
					doctype: doctype,
					fieldname: fieldname,
					enabled: enabled ? 1 : 0
				},
				callback(r) {
					if (r.exc) {
						frappe.throw("Update failed for " + doctype + " Field: " + fieldname);
					} 
				}
			})
	}
})