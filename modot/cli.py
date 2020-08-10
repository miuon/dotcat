''' CLI for modot command (MOdular DOTfiles).'''
from pathlib import Path
import sys

import click

from modot.cat import Cat
from modot import hostconfig
from modot import module_utils
from modot.templater import Templater


MODOT_PATH = Path('~/.local/share/modot').expanduser()
ACTIVE_HOST_PATH = MODOT_PATH / 'config.yaml'


@click.group(invoke_without_command=True)
@click.version_option()
@click.pass_context
def cli(ctx: click.Context):
    '''Modular dotfile manager.

    Run without a command for a summary of current state.
    '''
    MODOT_PATH.mkdir(exist_ok=True)
    if ctx.invoked_subcommand is None:
        host = hostconfig.get_deployed_host(ACTIVE_HOST_PATH)
        print(f'Deployed: {str(host)}' if host else 'No deployed host config')
        templater = Templater(MODOT_PATH)
        deployed_theme = templater.get_theme()
        print(f'Deployed theme: {deployed_theme}' if deployed_theme else
              'No deployed theme')
        deployed_color = templater.get_color()
        print(f'Deployed color: {deployed_color}' if deployed_color else
              'No deployed color')
        print('--help for usage')


@cli.command()
@click.argument('host', type=click.Path(exists=True, dir_okay=False))
@click.option('theme_flag', '-t', '--theme')
@click.option('color_flag', '-c', '--color')
@click.option('--interactive/--non-interactive', default=True)
@click.option('--dryrun', is_flag=True, default=False)
def deploy(host: str, theme_flag: str, color_flag: str,
           interactive: bool, dryrun: bool):
    '''Configure and deploy dotfiles using configuration from HOST.'''
    host_path = Path(host)
    deployed_host_tgt = hostconfig.get_deployed_host(ACTIVE_HOST_PATH)
    if deployed_host_tgt:
        if deployed_host_tgt == host_path:
            print(f'Redeploying same host: {str(deployed_host_tgt)}')
        else:
            ACTIVE_HOST_PATH.unlink()
            ACTIVE_HOST_PATH.symlink_to(host_path)
            print(f'Deploying over old host: {str(deployed_host_tgt)}')
    else:
        print('Deploying host config: ' + str(host_path))
        ACTIVE_HOST_PATH.symlink_to(host_path)
    host_cfg = hostconfig.from_file(ACTIVE_HOST_PATH)
    templater = Templater(MODOT_PATH, host_cfg)
    if interactive:
        _pick_theme_interactive(templater, host_cfg, theme_flag)
        _pick_color_interactive(templater, host_cfg, color_flag)
    else:
        _pick_theme_noninteractive(templater, host_cfg, theme_flag)
        _pick_color_noninteractive(templater, host_cfg, color_flag)
    _check_and_deploy(host_cfg, templater, dryrun)


@cli.command()
def reload():
    '''Redeploy dotfiles from the previously deployed configuration.'''
    host_cfg = hostconfig.from_file(ACTIVE_HOST_PATH)
    templater = Templater(MODOT_PATH, host_cfg)
    _check_and_deploy(host_cfg, templater, dryrun=False)


@cli.group()
def theme():
    '''Commands controlling the deployed theme.'''


@theme.command('get')
def get_theme():
    '''Print the currently deployed theme.'''
    deployed_theme = Templater(MODOT_PATH).get_theme()
    if deployed_theme:
        print(deployed_theme)
    else:
        sys.exit('No theme currently deployed')


@theme.command('list')
def list_themes():
    '''List all themes found in the themes directory.'''
    templater = Templater(MODOT_PATH,
                          hostconfig.from_file(ACTIVE_HOST_PATH))
    for name in templater.list_themes():
        print(name)


@theme.command('set')
@click.argument('name')
def set_theme(name: str):
    '''Set the theme to NAME and redeploy.'''
    host_cfg = hostconfig.from_file(ACTIVE_HOST_PATH)
    templater = Templater(MODOT_PATH, host_cfg)
    if name not in templater.list_themes():
        sys.exit(f'Could not find specified theme {name}')
    templater.set_theme(name)
    _check_and_deploy(host_cfg, templater, dryrun=False)


@cli.group()
def color():
    '''Commands controlling the deployed colorscheme.'''


@color.command('get')
def get_color():
    '''Print the currently deployed color.'''
    deployed_color = Templater(MODOT_PATH).get_color()
    if deployed_color:
        print(deployed_color)
    else:
        sys.exit('No color currently deployed')


@color.command('list')
def list_colors():
    '''List all colors found in the colors directory.'''
    templater = Templater(MODOT_PATH,
                          hostconfig.from_file(ACTIVE_HOST_PATH))
    for name in templater.list_colors():
        print(name)


@color.command('set')
@click.argument('name')
def set_color(name: str):
    '''Set the color to NAME and redeploy.'''
    host_cfg = hostconfig.from_file(ACTIVE_HOST_PATH)
    templater = Templater(MODOT_PATH, host_cfg)
    if name not in templater.list_colors():
        sys.exit(f'Could not find specified color {name}')
    templater.set_color(name)
    _check_and_deploy(host_cfg, templater, dryrun=False)


def _check_and_deploy(
        host_cfg: hostconfig.HostConfig, templater: Templater,
        dryrun: bool = True):
    '''Parse the modules, check rules, and deploy files.'''
    cat_dict = {}
    for module_path in module_utils.get_module_paths(host_cfg):
        for rule in module_utils.get_rules(module_path):
            if rule.out not in cat_dict:
                cat_dict[rule.out] = Cat(templater)
            cat_dict[rule.out].rules.append(rule)
    for cat in cat_dict.values():
        if dryrun:
            print(cat)
    for outpath, cat in cat_dict.items():
        if not cat.check():
            sys.exit(f'cat checks failed for outpath: {outpath}')
    for cat in cat_dict.values():
        if not dryrun:
            cat.deploy()


def _pick_theme_noninteractive(
        templater: Templater, host_cfg: hostconfig.HostConfig, flag: str
        ) -> str:
    '''Picks a theme without prompting.'''
    return flag or templater.get_theme() or host_cfg.default_theme


def _pick_theme_interactive(
        templater: Templater, host_cfg: hostconfig.HostConfig, flag: str
        ) -> str:
    '''Picks a theme and maybe prompts based on current state.'''
    return flag or templater.get_theme() or click.prompt(
        'Select a theme',
        default=host_cfg.default_theme,
        type=click.Choice(templater.list_themes()))


def _pick_color_noninteractive(
        templater: Templater, host_cfg: hostconfig.HostConfig, flag: str
        ) -> str:
    '''Picks a color without prompting.'''
    return flag or templater.get_color() or host_cfg.default_color


def _pick_color_interactive(
        templater: Templater, host_cfg: hostconfig.HostConfig, flag: str
        ) -> str:
    '''Picks a color and maybe prompts based on current state.'''
    return flag or templater.get_color() or click.prompt(
        'Select a color',
        default=host_cfg.default_color,
        type=click.Choice(templater.list_colors()))
