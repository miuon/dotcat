# MODOT
MOdular DOTfiles

Modular Overengineered Dotfile Organizer and Templater

## Overview

### Goals
* Handle complex cases of host-specific configuration without requiring any repeated dotfiles/dotfile segments. E.g. if you have config you use everywhere you go, config you use on all work machines (even if it needs to stay on-prem) and host-specific config -- modot can handle that cleanly.
* Very minimal opinion about how your repositories should be structured -- for the most part no need to heavily nest your files or name them anything specific.
* Templating that allows switching out color schemes and more complete themes independently of each other and across all deployed modules at once. Easy to use in rofi/dmenu scripts.

### Non-goals
* Strictly limited to shuffling files around -- intended to work well with hot reloading scripts/schemes but doesn't implement that itself. Not interested in messing with package managers or source control.
* Managing files that need to be dynamically modified in some way -- e.g. if you wanted to share shell history.
* No `stow`-style magic of replicating/merging directory layouts -- any file you add has to be accounted for in the module config and has to specify an output path.
* Implement conventions for how you structure/use your domains/modules/themes/colors. These are designed to be very flexible and you can easily end up with a complete mess on your hands. The [suggested configuration](#Suggested-use) should work very well though.
* Implementing pywal-like autogeneration of colors or making interoperability with pywal/wpgtk easier. With the right conventions you could probably make this work with pywal/wpgtk but modot operates on a notably different model re: what is responsible for what.

### Pros
* No dangling symlinks, no extra files/state aside from some symlinks in `~/.local/share/modot` to track the deployed host/color/theme.
* Define only what you need -- a host configuration can be as little as a single config file.
* Model for storing secrets is simple and flexible -- create a modot domain for each security domain you have, manage the directory however you want, once you've cloned/downloaded/whatever-ed it to a host, just add it as a domain to that host config. The existence of the directory is disclosed in the host config, but since host configs can be anywhere that's easy to fix.

### Cons
* Can't do e.g. `vim .bashrc` anymore. modot will automatically make these files readonly so your edits will fail, but it could be annoying getting in the habit of `vim <path to the sourcefile>`.
* Ability to do host-specific things is strictly limited to what you can accomplish with file concatenation. E.g. if something host-specific absolutely needs to be injected in the middle of a line, etc. As far as I know this is purely theoretical, though.
* You have to clean up after yourself -- if you want to rename or remove a file you need to make the changes in any module configs that point to it and delete the generated files from your homedir.

## Install

## Configuration

### Suggested use
