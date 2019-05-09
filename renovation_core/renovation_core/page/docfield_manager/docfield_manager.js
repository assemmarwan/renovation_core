frappe.provide('renovation');

frappe.pages['DocField Manager'].on_page_load = function (wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Renovation DocField Manager',
		single_column: true
	});
	wrapper.docfield_manager = new DocFieldManager(wrapper)
	frappe.breadcrumbs.add("Renovation Core");
}

class DocFieldManager {
	constructor(wrapper) {
		this.wrapper = wrapper
		this.page = wrapper.page
		this.fields_multicheck = {};
		this.multicheck_selected = {};
		this.doctypes_fields = {};
		this.values = {};
		this.user = null
		this.make()
	}

	make() {
		this.page.add_field({
			label: 'DocType',
			fieldname: 'doctype',
			fieldtype: 'Link',
			options: 'DocType',
			reqd: 1,
			onchange: () => {
				this.ondoctype_changed()
			} // to have proper this in ondoctype_changed()
		})
		this.page.add_field({
			label: 'User',
			fieldname: 'user',
			fieldtype: 'Link',
			options: 'User',
			onchange: () => {
				this.ondoctype_changed()
			} // to have proper this in ondoctype_changed()
		})
		this.$multicheckWrapper = $(`<div class="col-xs-12">`).appendTo(this.page.page_form)
		this.page.set_primary_action(__("Update"), () => {
			this.update_data()
		})
	}

	update_data() {
		$.each(this.fields_multicheck, (key, el) => {
			this.values[key] = el.selected_options
		})
		let unchecked_values = {}
		$.each(this.multicheck_selected, (key, val) => {
			let obj = this.values[key] || []
			if (typeof unchecked_values[key] === "undefined")
				unchecked_values[key] = [];
			val.forEach(v => {
				if (!obj.includes(v))
					unchecked_values[key].push(v)
			})
		})
		const args = {
			"selected_values": this.values,
			"unselected_values": unchecked_values
		}
		frappe.call({
			method: 'renovation_core.renovation_core.page.docfield_manager.docfield_manager.update_values',
			args: {
				values: args
			},
			callback: r => {
				if (!r.xhr) {
					frappe.show_alert({
						body: __("Successfully Updated"),
						indicator: 'green'
					})
				}
			}
		})
	}

	ondoctype_changed() {
		if (!this.page.fields_dict['doctype'].value || (this.page.fields_dict['doctype'].value === this.doctype &&
				this.page.fields_dict['user'].value === this.user)) {
			return;
		}
		this.doctype = this.page.fields_dict['doctype'].value;
		this.user = this.page.fields_dict['user'].value
		frappe.call({
			method: "renovation_core.renovation_core.page.docfield_manager.docfield_manager.get_docfield_and_selected_val",
			args: {
				doctype: this.doctype,
				user: this.user
			},
			freeze: true,
			freeze_message: __("Fetching Data"),
			callback: r => {
				if (r['message']) {
					this.multicheck_selected = r.message.selected_values
					this.doctypes_fields = r.message.doctypes_fields
				}
				this.set_field_options()
			}
		})
	}

	set_field_options() {
		const doctype = this.doctype;
		const related_doctypes = this.get_doctypes(doctype);

		this.$multicheckWrapper.empty();

		// Add 'Select All', 'Select All Mandetory' and 'Unselect All' button
		this.make_multiselect_buttons()
		this.fields_multicheck = {}
		related_doctypes.forEach(dt => {
			this.fields_multicheck[dt] = this.add_doctype_field_multicheck_control(dt);
		});
	}

	make_multiselect_buttons() {
		const button_container = $(this.$multicheckWrapper)
			.append('<div class="flex"></div>')
			.find('.flex');

		["Select All", "Unselect All", "Select All Mandetory"].map(d => {
			frappe.ui.form.make_control({
				parent: $(button_container),
				df: {
					label: __(d),
					fieldname: frappe.scrub(d),
					fieldtype: "Button",
					click: () => {
						checkbox_toggle(d);
					}
				},
				render_input: true
			});
		});

		$(button_container).find('.frappe-control').map((index, button) => {
			$(button).css({
				"margin-right": "1em"
			});
		});
		let me = this

		function checkbox_toggle(d) {
			let checked = d === 'Unselect All';
			let selector = `:checkbox`
			if (d === "Select All Mandetory")
				selector = `:checkbox.text-danger`;
			$(me.$multicheckWrapper).find('[data-fieldtype="MultiCheck"]').map((index, element) => {
				$(element).find(selector).prop("checked", checked).trigger('click');
			});
		}
	}

	get_doctypes(parentdt) {
		if (!this.doctypes_fields)
			return [parentdt];
		return [parentdt].concat(
			Object.keys(this.doctypes_fields)
		);
	}

	add_doctype_field_multicheck_control(doctype) {
		const fields = this.get_fields(doctype);

		const values = this.multicheck_selected[doctype] || [];
		const options = fields
			.map(df => {
				return {
					label: (df.label || df.fieldname) + ' <strong>(' + (df.fieldtype || "") + ')</strong>',
					value: df.fieldname,
					danger: df.reqd || df.fieldtype === "Table",
					checked: values.includes(df.fieldname)
				};
			});
		const multicheck_control = frappe.ui.form.make_control({
			parent: this.$multicheckWrapper,
			df: {
				"label": doctype,
				"fieldname": doctype + '_fields',
				"fieldtype": "MultiCheck",
				"options": options,
				"selected_options": values,
				"columns": 3,
			},
			render_input: true
		});
		multicheck_control.$checkbox_area.find('.label-area.text-danger').prev().addClass('text-danger')
		multicheck_control.refresh_input();

		return multicheck_control;
	}
	filter_fields(df) {
		return (frappe.model.is_value_type(df) || ["Table", "Section Break"].includes(df.fieldtype)) && !df.hidden
	}
	get_fields(dt) {
		return this.get_docfields(dt).filter(this.filter_fields)
	}
	get_docfields(dt) {
		return this.doctypes_fields[dt] || []
	}
}