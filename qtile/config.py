# Copyright (c) 2010 Aldo Cortesi
# Copyright (c) 2010, 2014 dequis
# Copyright (c) 2012 Randall Ma
# Copyright (c) 2012-2014 Tycho Andersen
# Copyright (c) 2012 Craig Barnes
# Copyright (c) 2013 horsik
# Copyright (c) 2013 Tao Sauvage
# Copyright (c) 2020 Aliaksei Urbanski
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import logging
import os
import subprocess

from libqtile.config import Key, Screen, Group, Drag, Click
from libqtile.lazy import lazy
from libqtile import layout, bar, widget, hook

from typing import List  # noqa: F401

TIME_FORMAT = '%Y-%m-%d %H:%M:%S'

mod = 'mod1'

logger = logging.getLogger('libqtile')


def spawncmd(qtile):
    qtile.cmd_spawncmd(
        prompt='run', widget=f'prompt_{qtile.current_screen.index}'
    )


def to_group(qtile, group_name):
    if qtile.current_screen.group.name == group_name:
        return

    group = qtile.groups_map[group_name]
    if group.screen:
        qtile.cmd_to_screen(group.screen.index)
    else:
        group.cmd_toscreen()


def move_to_screen(qtile, screen_index):
    qtile.current_screen.group.cmd_toscreen(screen_index)
    qtile.cmd_to_screen(screen_index)


keys = [
    # Switch between windows in current stack pane
    Key([mod], 'k', lazy.layout.down()),
    Key([mod], 'j', lazy.layout.up()),

    # Move windows up or down in current stack
    Key([mod, 'control'], 'k', lazy.layout.shuffle_down()),
    Key([mod, 'control'], 'j', lazy.layout.shuffle_up()),

    # Lock the screen
    Key([mod, 'control'], 'l', lazy.spawn('custom-lock')),
    Key([mod, 'control'], 'o', lazy.spawn('dpms-off')),

    # Switch window focus to other pane(s) of stack
    Key([mod], 'space', lazy.layout.next()),

    # Swap panes of split stack
    Key([mod, 'shift'], 'space', lazy.layout.rotate()),

    # Toggle between split and unsplit sides of stack.
    # Split = all windows displayed
    # Unsplit = 1 window displayed, like Max layout, but still with
    # multiple stack panes
    Key([mod, 'shift'], 'Return', lazy.layout.toggle_split()),

    # terminal
    Key([mod], 'Return', lazy.spawn('alacritty')),

    # Toggle between different layouts as defined below
    Key([mod], 'Tab', lazy.next_layout()),
    Key([mod, 'shift'], 'q', lazy.window.kill()),

    Key([mod, 'shift'], 'r', lazy.restart()),
    Key([mod, 'shift'], 'e', lazy.shutdown()),
    Key([mod], 'd', lazy.function(spawncmd)),

    # Key([mod], 'w', lazy.to_screen(0)),
    # Key([mod], 'r', lazy.to_screen(1)),

    # Key([mod, 'shift'], 'j', lazy.group.toscreen(0, focus=True)),  # TODO
    Key([mod, 'shift'], 'j', lazy.function(move_to_screen, 0)),
    Key([mod, 'shift'], 'l', lazy.function(move_to_screen, 1)),
]

groups = [
    Group('1', label=''),
    Group('2', label=''),
    Group('3', label=''),
    Group('4', label='4: ', layout='stack'),
    Group('5', label=''),
    Group('6', label=''),
    Group('7'),  # TODO: viber
    Group('8', label=''),
    Group('9', label='9: ', layout='stack'),
    Group('0', label='0: ', layout='stack'),
]

for group in groups:
    keys.extend([
        Key([mod], group.name, lazy.function(to_group, group.name)),

        # switch to & move focused window to group
        Key(
            [mod, 'shift'],
            group.name,
            lazy.window.togroup(group.name, switch_group=True)
        ),
        # Or, use below if you prefer not to switch to that group.
        # # mod + shift + letter of group = move focused window to group
        # Key([mod, 'shift'], group.name, lazy.window.togroup(group.name)),
    ])

layouts = [
    layout.Max(),
    layout.Stack(num_stacks=2, border_width=0, autosplit=True),
    # Try more layouts by unleashing below layouts.
    # layout.Bsp(),
    # layout.Columns(),
    # layout.Matrix(),
    # layout.MonadTall(),
    # layout.MonadWide(),
    # layout.RatioTile(),
    # layout.Tile(),
    # layout.TreeTab(),
    # layout.VerticalTile(),
    # layout.Zoomy(),
]

widget_defaults = dict(
    font='sans',
    fontsize=12,
    padding=3,
)
extension_defaults = widget_defaults.copy()

screens = [
    Screen(
        top=bar.Bar(
            [
                widget.CurrentLayout(),
                widget.GroupBox(hide_unused=True),
                widget.Prompt('prompt_0'),
                widget.WindowName(),
                widget.Clock(format=TIME_FORMAT),
            ],
            size=24,
            opacity=0.7,
        ),
    ),
    Screen(
        top=bar.Bar(
            [
                widget.CurrentLayout(),
                widget.GroupBox(hide_unused=True),
                widget.Prompt('prompt_1'),
                widget.WindowName(),
                widget.Systray(),
                widget.Clock(format=TIME_FORMAT),
            ],
            size=32,
            opacity=0.7,
        ),
    ),
]

# Drag floating layouts.
mouse = [
    Drag([mod], 'Button1', lazy.window.set_position_floating(),
         start=lazy.window.get_position()),
    Drag([mod], 'Button3', lazy.window.set_size_floating(),
         start=lazy.window.get_size()),
    Click([mod], 'Button2', lazy.window.bring_to_front())
]

dgroups_key_binder = None
dgroups_app_rules = []  # type: List
main = None
follow_mouse_focus = False
bring_front_click = False
cursor_warp = False
floating_layout = layout.Floating(float_rules=[
    # Run the utility of `xprop` to see the wm class and name of an X client.
    {'wmclass': 'confirm'},
    {'wmclass': 'dialog'},
    {'wmclass': 'download'},
    {'wmclass': 'error'},
    {'wmclass': 'file_progress'},
    {'wmclass': 'notification'},
    {'wmclass': 'splash'},
    {'wmclass': 'toolbar'},
    {'wmclass': 'confirmreset'},  # gitk
    {'wmclass': 'makebranch'},  # gitk
    {'wmclass': 'maketag'},  # gitk
    {'wname': 'branchdialog'},  # gitk
    {'wname': 'pinentry'},  # GPG key password entry
    {'wmclass': 'ssh-askpass'},  # ssh-askpass
])
auto_fullscreen = True
focus_on_window_activation = 'smart'


@hook.subscribe.startup
def startup():
    home = os.path.expanduser('~')
    subprocess.call([home + '/.config/qtile/startup.sh'])


# XXX: Gasp! We're lying here. In fact, nobody really uses or cares about this
# string besides java UI toolkits; you can see several discussions on the
# mailing lists, GitHub issues, and other WM documentation that suggest setting
# this string if your java app doesn't work correctly. We may as well just lie
# and say that we're a working one by default.
#
# We choose LG3D to maximize irony: it is a 3D non-reparenting WM written in
# java that happens to be on java's whitelist.
wmname = 'LG3D'
