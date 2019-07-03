import click

@click.group()
def renovation():
  pass

@click.command("setup")
def setup():
  from renovation_core.install.benchconfig import update_config
  update_config()


renovation.add_command(setup)
commands = [renovation]