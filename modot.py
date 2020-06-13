# MOdular DOTfiles
# Modular Overengineered Dotfile Organizer and Templater
import asyncio
import chevron
import click
import os
import shutil
import sys
import yaml

from pathlib import Path

COMMON = Path('common')
HOST = Path('host')
CONFIG_DIR = Path('~/.config/modot').expanduser()
CONFIG_FILE = Path('config.yaml')
THEME = Path('theme')
THEMES = Path('themes')
BUILT_THEME = Path('built_theme')
COLOR = Path('color.yaml')
COLORS = Path('colors')

@click.command()
@click.option('-t', '--theme', 'theme_opt', help='Theme to apply')
@click.option('-c', '--color', 'color_opt', help='Color to apply')
@click.option(
    '-f', '--full', 'force_mode', flag_value='full',
    help='Force full reload')
@click.option(
    '-q', '--quick', 'force_mode', flag_value='quick',
    help='Force quick reload')
@click.option('--list-themes', 'list_opt', flag_value='themes')
@click.option('--list-colors', 'list_opt', flag_value='colors')
def modot(theme_opt, color_opt, force_mode, list_opt):
    with open(CONFIG_DIR / CONFIG_FILE, 'r') as stream:
        config = yaml.safe_load(stream)

    dots_dir = Path(config.get('dots_path')).expanduser()
    theme_path = config.get('theme_path', '')
    theme_dir = Path(theme_path).expanduser() if theme_path else \
        dots_dir / THEMES
    color_path = config.get('color_path', '')
    color_dir = Path(color_path).expanduser() if color_path else \
        dots_dir / COLORS
    
    if list_opt == 'themes':
        themes = os.listdir(theme_dir)
        for theme in themes: print(theme)
        return
    elif list_opt == 'colors':
        colors = [os.path.splitext(fn)[0] for fn in os.listdir(color_dir)]
        for color in colors: print(color)
        return

    theme_found, theme_changed = link_theme(
            theme_opt, theme_dir, config.get('default_theme', None))
    color_found, _ = link_color(
            color_opt, color_dir, config.get('default_color', None))
    maybe_fail_not_found(theme_found, color_found)
    build_templates(config.get('modules', {}))
    run_scripts(
        config,
        dots_dir / COMMON,
        dots_dir / HOST,
        CONFIG_DIR / BUILT_THEME,
        quick=is_quick_reload(force_mode, theme_changed))

def link_theme(theme_opt, theme_dir, default_theme):
    theme_found = True
    theme_changed = True
    if theme_opt and (theme_dir / Path(theme_opt)).exists():
        link(theme_dir / Path(theme_opt), CONFIG_DIR / THEME)
    elif (CONFIG_DIR / THEME).exists():
        theme_changed = False
    elif default_theme and \
            (theme_dir / Path(default_theme)).exists():
        link(theme_dir / Path(default_theme),
                CONFIG_DIR / THEME)
    else:
        theme_found = False
    return (theme_found, theme_changed)

def link_color(color_opt, color_dir, default_color):
    color_found = True
    color_changed = True
    if color_opt and (color_dir / Path(color_opt + '.yaml')).exists():
        link(color_dir / Path(color_opt + '.yaml'), CONFIG_DIR / COLOR)
    elif (CONFIG_DIR / COLOR).exists():
        color_changed = False
    elif default_color \
            and (color_dir / Path(default_color)).exists():
        link(color_dir / Path(default_color),
                CONFIG_DIR / COLOR)
    else:
        color_found = False
    return (color_found, color_changed)

def build_templates(modules):
    built_theme_dir = CONFIG_DIR / BUILT_THEME
    # TODO: make atomic?
    shutil.rmtree(built_theme_dir)
    built_theme_dir.mkdir()
    with open(CONFIG_DIR / COLOR, 'r') as stream:
        color_dict = yaml.safe_load(stream)
    for module in modules:
        subdir = module.get('subdir', '')
        if not subdir:
            continue # maybe log or something
        theme_module_dir = CONFIG_DIR / THEME / Path(subdir)
        built_theme_module_dir = built_theme_dir / Path(subdir)
        module_theme_files = [item for item in
                theme_module_dir.rglob('*') if item.is_file()]
        for theme_file in module_theme_files:
            base_file_path = theme_file
            gen_file_path = (
                built_theme_module_dir / theme_file.relative_to(theme_module_dir))
            template(color_dict, base_file_path, gen_file_path)

def link(tgt, link_name):
    """ Forcibly create symlink from link_name to src. """
    tmp_path = link_name.parent / Path('modottmp')
    os.symlink(tgt, tmp_path)
    os.rename(tmp_path, link_name)

def template(color_dict, src_path, tgt_path):
    """ Template the src file against the colors to create the tgt file. """
    tgt_path.parent.mkdir(parents=True, exist_ok=True)
    with open(src_path, 'r') as src_file:
        rendered_str = chevron.render(src_file, color_dict)
    with open(tgt_path, 'w') as tgt_file:
        tgt_file.write(rendered_str)
    
def run_scripts(config, common_base_dir, host_base_dir, theme_base_dir, quick):
    # TODO: is this running concurrently? if not find a way to do so
    for module in config.get('modules', []):
        script = module.get('script', '')
        subdir = module.get('subdir', '')
        if script and subdir:
            asyncio.run(run_script(
                script,
                common_base_dir / subdir,
                host_base_dir / subdir,
                theme_base_dir / subdir,
                quick))

async def run_script(script, common_dir, host_dir, theme_dir, quick):
    modot_env = dict(os.environ)
    modot_env['MODOT_COMMON'] = common_dir
    modot_env['MODOT_HOST'] = host_dir
    modot_env['MODOT_THEME'] = theme_dir
    modot_env['MODOT_QUICK'] = 'true' if quick else 'false'
    proc = await asyncio.create_subprocess_shell(
            script,
            env=modot_env,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await proc.communicate()
    print(f'[{script!r} exited with {proc.returncode}]')
    if stdout:
        print(f'[stdout]\n{stdout.decode()}')
    if stderr:
        print(f'[stderr]\n{stderr.decode()}')

def maybe_fail_not_found(theme_found, color_found):
    if not theme_found and not color_found:
        sys.exit("could not find a theme or color to use")
    if not theme_found:
        sys.exit("could not find a theme to use")
    if not color_found:
        sys.exit("could not find a color to use")

def is_quick_reload(force_mode, theme_changed):
    if force_mode == 'full':
        return False
    elif force_mode == 'quick':
        return True
    else:
        return not theme_changed
