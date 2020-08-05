# dotcat (DOTfile conCATenator)

## Overview
dotcat is a dotfile manager written in python. It is motivated by a few overlapping requirements -- different security domains, different hosts, the desire to switch colors and themes frequently, and a fanatical adherence to DRY. Two primary things distinguish it from other dotfile managers: flexibility around combining different config repos, and that it creates readonly copies rather than symlinks. It requires more configuration than most dotfile managers but once initially set up, adding new hosts or tools is simple.

### Definitions
* host config: A machine-specific configuration. Doesn't need to actually be specific to a machine, but this is a specific setup that can be deployed as a unit. Defined by a `config.yaml` file.
* domain: A logical unit of config reuse. In practice, a directory containing modules. A host config should point to one or more domains that it intends to use.
* module: A directory containing dotfiles and a module config specifying how to deploy them. If a module is named in the host config, every module by that name in the enabled domains will be deployed.

### Motivating example
Let's say I have 4 hosts: `personal1`, `personal2`, `work1`, and `work2`. I have many config lines that I want everywhere, config lines specific to each host, and config lines that I want on both work hosts. Additionally, the config lines for work contain internal-only information and have to be stored separately from my personal dotfiles, which I want to be public. Maybe one or more of these hosts is headless, and I'd prefer to keep configs for graphical applications off of it.

To handle this with `dotcat` we might create domains for each of the hosts, a common domain for shared config, and a work domain for shared work config. Each host should then have a `config.yaml` pointing to the domains it needs. In this example, `work2` would use the common domain, the work domain, and the work2 domain.

## Install

## Configuration

### Suggested use

## Design

### Goals
* Handle complex cases of host-specific configuration without requiring any repeated dotfiles/dotfile segments. E.g. if you have config you use everywhere you go, config you use on all work machines (even if it needs to stay on-prem) and host-specific config -- dotcat can handle that cleanly.
* Very minimal opinion about how your repositories should be structured -- for the most part no need to heavily nest your files or name them anything specific.
* Templating that allows switching out color schemes and themes independently of each other and across all deployed modules at once. Easy to use in rofi/dmenu scripts.

### Non-goals
* Strictly limited to shuffling files around -- intended to work well with hot reloading scripts/schemes but doesn't implement that itself. Not interested in messing with package managers or source control.
* Managing files that need to be dynamically modified in some way -- e.g. if you wanted to share shell history.
* No `stow`-style magic of replicating/merging directory layouts -- any file you add has to be accounted for in the module config and has to specify an output path.

### Pros
* No dangling symlinks, no extra files/state aside from some symlinks in `~/.local/share/dotcat` to track the deployed host/color/theme.
* Define only what you need -- a host configuration can be as little as a single config file.
* Model for storing secrets is simple and flexible -- create a dotcat domain for each security domain you have, manage the directory however you want, once you've cloned/downloaded/whatever-ed it to a host, just add it as a domain to that host config. The existence of the directory is disclosed in the host config, but since host configs can be anywhere that's easy to fix.
* Mostly hides differences between tools with config importing and those without.

### Cons
* Can't do e.g. `vim .bashrc` anymore. dotcat will automatically make these files readonly so your edits will fail, but it could be annoying getting in the habit of `vim <path to the sourcefile>`.
* Ability to do host-specific things is strictly limited to what you can accomplish with file concatenation. E.g. if something host-specific absolutely needs to be injected in the middle of a line, etc. As far as I know this is purely theoretical, though.
* You have to clean up after yourself -- if you want to rename or remove a file you need to make the changes in any module configs that point to it and delete the generated files from your homedir.
