import click
from frappe.commands import pass_context


@click.command('serve')
@click.option('--port', default=8000)
@click.option('--profile', is_flag=True, default=False)
@click.option('--noreload', "no_reload", is_flag=True, default=False)
@click.option('--nothreading', "no_threading", is_flag=True, default=False)
@pass_context
def serve(context, port=None, profile=False, no_reload=False, no_threading=False, sites_path='.', site=None):
	"Start development web server Form US."
	import frappe.app
	import renovation_core.app
	frappe.app.init_request.__code__ = renovation_core.app.init_request.__code__

	if not context.sites:
		site = None
	else:
		site = context.sites[0]
	frappe.app.serve(port=port, profile=profile, no_reload=no_reload, no_threading=no_threading, site=site, sites_path='.')


commands = [serve]
