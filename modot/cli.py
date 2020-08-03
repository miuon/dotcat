# MOdular DOTfiles
# Modular Overengineered Dotfile Organizer and Templater
import click
import os
import sys

from pathlib import Path
from typing import Optional

from .constants import *
from .themeengine import ThemeEngine
from .utils import get_deployed_host, link_atomic

@click.group(invoke_without_command=True)
@click.version_option()
@click.pass_context
def cli(ctx: click.Context):
    """Modular dotfile manager.

    Run without a command for a summary of current state.
    """
    MODOT_DIR.mkdir(exist_ok=True)
    if ctx.invoked_subcommand is None:
        host = get_deployed_host()
        print(f'Deployed: {str(host)}' if host else 'No deployed host config')
        theme = get_theme()
        print(f'Deployed theme: {theme}' if theme else 'No deployed theme')
        color = get_color()
        print(f'Deployed color: {color}' if color else 'No deployed color')
        print('--help for usage')

@cli.command()
@click.argument("host", type=click.Path(exists=True, dir_okay=False))
@click.option('theme_flag', '-t', '--theme')
@click.option('color_flag', '-c', '--color')
@click.option('--interactive/--non-interactive', default=True)
def deploy(host: str, theme_flag: str, color_flag: str, interactive: bool):
    """Configure and deploy dotfiles using configuration from HOST."""
    host_path = Path(host)
    deployed_host_tgt = get_deployed_host()
    if deployed_host_tgt:
        if deployed_host_tgt == host_path:
            print(f'Redeploying same host: {str(deployed_host_tgt)}')
        else:
            print(f'Deploying over old host: {str(deployed_host_tgt)}')
    else:
        print('Deploying host config: ' + str(host_path))
    link_atomic(host_path, DEPLOYED_HOST)
    config = ThemeEngine(host_path)
    pick_theme_maybe_interactive(config, theme_flag, interactive)
    pick_color_maybe_interactive(config, color_flag, interactive)
    config.deploy()

@cli.command()
@click.argument("host", type=click.Path(exists=True, dir_okay=False))
@click.option('theme_flag', '-t', '--theme')
@click.option('color_flag', '-c', '--color')
@click.option('--interactive/--non-interactive', default=True)
def dryrun(host: str, theme_flag: str, color_flag: str, interactive: bool):
    """Configure and print intended actions from HOST."""
    host_path = Path(host)
    deployed_host_tgt = get_deployed_host()
    if deployed_host_tgt:
        if deployed_host_tgt == host_path:
            print(f'Redeploying same host: {str(deployed_host_tgt)}')
        else:
            print(f'Deploying over old host: {str(deployed_host_tgt)}')
    else:
        print('Deploying host config: ' + str(host_path))
    link_atomic(host_path, DEPLOYED_HOST)
    config = ThemeEngine(host_path)
    pick_theme_maybe_interactive(config, theme_flag, interactive)
    pick_color_maybe_interactive(config, color_flag, interactive)
    config.print_actions()
    print(config.template_dict)

@cli.command()
def reload():
    """Redeploy dotfiles from the previously deployed configuration."""
    deployed_host_tgt = get_deployed_host()
    if not deployed_host_tgt or not deployed_host_tgt.exists():
        sys.exit('No deployed host found')
    config = ThemeEngine(deployed_host_tgt)
    config.read_template_dict()
    config.deploy()

@cli.group()
def theme():
    pass

@theme.command("list")
def list_themes_cmd():
    """List all themes found in the themes directory."""
    config = ThemeEngine(get_deployed_host())
    for filename in config.list_themes():
        print(filename)

@theme.command("get")
def get_theme_cmd():
    """Print the currently deployed color."""
    theme = get_theme()
    if theme:
        print(theme)
    else:
        sys.exit('No theme currently deployed')

def get_theme():
    if ACTIVE_THEME_PATH.exists():
        return Path(os.readlink(ACTIVE_THEME_PATH)).stem
    else:
        return None

@theme.command("set")
@click.argument("name")
def set_theme_cmd(name: str):
    """Set the theme to NAME and redeploy."""
    config = ThemeEngine(get_deployed_host())
    if name not in config.list_themes():
        sys.exit(f'Could not find specified theme {name}')
    config.set_theme(name)
    config.deploy()

@cli.group()
def color():
    """Commands controlling the deployed colorscheme."""
    pass

@color.command("list")
def list_colors_cmd():
    """List all colors found in the colors directory."""
    config = ThemeEngine(get_deployed_host())
    for filename in config.list_colors():
        print(filename)

@color.command("get")
def get_color_cmd():
    """Print the currently deployed color."""
    color = get_color()
    if color:
        print(color)
    else:
        sys.exit('No color currently deployed')

def get_color() -> Optional[str]:
    if ACTIVE_COLOR_PATH.exists():
        return Path(os.readlink(ACTIVE_COLOR_PATH)).stem
    else:
        return None

@color.command("set")
@click.argument("name")
def set_color_cmd(name: str):
    """Set the color to NAME and redeploy."""
    config = ThemeEngine(get_deployed_host())
    if name not in config.list_colors():
        sys.exit(f'Could not find specified theme {name}')
    config.set_color(name)
    config.deploy()

def pick_theme_maybe_interactive(
        config: ThemeEngine, flag: str, interactive: bool):
    deployed_theme = get_theme()
    if flag:
        theme = flag
    elif deployed_theme:
        theme = deployed_theme
    elif interactive:
        if config.default_theme:
            theme = click.prompt(
                    'Select a theme',
                    default=config.default_theme,
                    type=click.Choice(config.list_themes()))
        else:
            theme = click.prompt(
                    'Select a theme',
                    type=click.Choice(config.list_themes()))
    elif config.default_theme:
        theme = config.default_theme
    else:
        sys.exit('Could not find a theme to use, set with "theme" subcommand')
    config.set_theme(theme)

def pick_color_maybe_interactive(
        config: ThemeEngine, flag: str, interactive: bool):
    deployed_color = get_color()
    if flag:
        color = flag
    elif deployed_color:
        color = deployed_color
    elif interactive:
        if config.default_color:
            color = click.prompt(
                    'Select a color',
                    default=config.default_color,
                    type=click.Choice(config.list_colors()))
        else:
            color = click.prompt(
                    'Select a color',
                    type=click.Choice(config.list_colors()))
    elif config.default_color:
        color = config.default_color
    else:
        sys.exit('Could not find a color to use, set with "color" subcommand')
    config.set_color(color)

