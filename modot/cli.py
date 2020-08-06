''' CLI for modot command (MOdular DOTfiles).'''
from pathlib import Path
import sys

import click

from modot.state import State
from modot.themeengine import ThemeEngine


@click.group(invoke_without_command=True)
@click.version_option()
@click.pass_context
def cli(ctx: click.Context):
    '''Modular dotfile manager.

    Run without a command for a summary of current state.
    '''
    ctx.ensure_object(dict)
    ctx.obj['state'] = State()
    if ctx.invoked_subcommand is None:
        state = ctx.obj['state']
        host = state.get_deployed_host()
        print(f'Deployed: {str(host)}' if host else 'No deployed host config')
        deployed_theme = state.get_theme()
        print(f'Deployed theme: {deployed_theme}' if deployed_theme else
              'No deployed theme')
        deployed_color = state.get_color()
        print(f'Deployed color: {deployed_color}' if deployed_color else
              'No deployed color')
        print('--help for usage')


@cli.command()
@click.argument('host', type=click.Path(exists=True, dir_okay=False))
@click.option('theme_flag', '-t', '--theme')
@click.option('color_flag', '-c', '--color')
@click.option('--interactive/--non-interactive', default=True)
@click.pass_context
def deploy(
        ctx, host: str, theme_flag: str, color_flag: str, interactive: bool):
    '''Configure and deploy dotfiles using configuration from HOST.'''
    state = ctx.obj['state']
    state.set_host_path(Path(host))
    config = ThemeEngine(state)
    _pick_theme_maybe_interactive(state, theme_flag, interactive)
    _pick_color_maybe_interactive(state, color_flag, interactive)
    config.deploy()


@cli.command()
@click.argument('host', type=click.Path(exists=True, dir_okay=False))
@click.option('theme_flag', '-t', '--theme')
@click.option('color_flag', '-c', '--color')
@click.option('--interactive/--non-interactive', default=True)
@click.pass_context
def dryrun(
        ctx, host: str, theme_flag: str, color_flag: str, interactive: bool):
    '''Configure and print intended actions from HOST.'''
    state = ctx.obj['state']
    state.set_host_path(Path(host))
    config = ThemeEngine(state)
    _pick_theme_maybe_interactive(state, theme_flag, interactive)
    _pick_color_maybe_interactive(state, color_flag, interactive)
    config.print_actions()
    print(state.get_themecolor_dict())


@cli.command()
@click.pass_context
def reload(ctx):
    '''Redeploy dotfiles from the previously deployed configuration.'''
    state = ctx.obj['state']
    deployed_host_tgt = state.get_deployed_host()
    if not deployed_host_tgt or not deployed_host_tgt.exists():
        sys.exit('No deployed host found')
    config = ThemeEngine(state)
    config.deploy()


@cli.group()
def theme():
    '''Commands controlling the deployed theme.'''


@theme.command('list')
@click.pass_context
def list_themes_cmd(ctx):
    '''List all themes found in the themes directory.'''
    state = ctx.obj['state']
    for theme_name in state.list_themes():
        print(theme_name)


@theme.command('get')
@click.pass_context
def get_theme_cmd(ctx):
    '''Print the currently deployed color.'''
    state = ctx.obj['state']
    deployed_theme = state.get_theme()
    if deployed_theme:
        print(deployed_theme)
    else:
        sys.exit('No theme currently deployed')


@theme.command('set')
@click.argument('name')
@click.pass_context
def set_theme_cmd(ctx, name: str):
    '''Set the theme to NAME and redeploy.'''
    state = ctx.obj['state']
    config = ThemeEngine(state)
    if name not in state.list_themes():
        sys.exit(f'Could not find specified theme {name}')
    state.set_theme(name)
    config.deploy()


@cli.group()
def color():
    '''Commands controlling the deployed colorscheme.'''


@color.command('list')
@click.pass_context
def list_colors_cmd(ctx):
    '''List all colors found in the colors directory.'''
    state = ctx.obj['state']
    for color_name in state.list_colors():
        print(color_name)


@color.command('get')
@click.pass_context
def get_color_cmd(ctx):
    '''Print the currently deployed color.'''
    state = ctx.obj['state']
    deployed_color = state.get_color()
    if deployed_color:
        print(deployed_color)
    else:
        sys.exit('No color currently deployed')


@color.command('set')
@click.argument('name')
@click.pass_context
def set_color_cmd(ctx, name: str):
    '''Set the color to NAME and redeploy.'''
    state = ctx.obj['state']
    config = ThemeEngine(state)
    if name not in state.list_colors():
        sys.exit(f'Could not find specified theme {name}')
    state.set_color(name)
    config.deploy()


def _pick_theme_maybe_interactive(
        state: State, flag: str, interactive: bool) -> str:
    '''Picks a theme and maybe prompts based on current state/interactivity.'''
    deployed_theme = state.get_theme()
    default_theme = state.get_host_config().get('default_theme', '')
    if interactive:
        picked_theme = flag or deployed_theme or click.prompt(
            'Select a theme',
            default=default_theme if default_theme else None,
            type=click.Choice(state.list_themes()))
    else:
        picked_theme = flag or deployed_theme or default_theme
    if not picked_theme:
        sys.exit(
            'Could not find a theme to use, set with \'theme\' subcommand')
    return picked_theme


def _pick_color_maybe_interactive(
        state: State, flag: str, interactive: bool) -> str:
    '''Picks a color and maybe prompts based on current state/interactivity.'''
    deployed_color = state.get_color()
    default_color = state.get_host_config().get('default_color', '')
    if interactive:
        picked_color = flag or deployed_color or click.prompt(
            'Select a color',
            default=default_color if default_color else None,
            type=click.Choice(state.list_colors()))
    else:
        picked_color = flag or deployed_color or default_color
    if not picked_color:
        sys.exit(
            'Could not find a color to use, set with \'color\' subcommand')
    return picked_color
