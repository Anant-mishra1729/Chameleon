# window.py
#
# Copyright 2026 Amish
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

from gi.repository import Adw
from gi.repository import Gtk, Gdk,Gio

@Gtk.Template(resource_path='/io/github/forklore/Chameleon/window.ui')
class ChameleonWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'ChameleonWindow'

    main_box = Gtk.Template.Child()
    toast_overlay = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        drop_target = Gtk.DropTarget.new(
            Gdk.FileList,
            Gdk.DragAction.COPY
        )

        # Connect drop signal
        drop_target.connect("drop", self.on_drop)
        drop_target.connect("enter", self.on_drag_enter)
        drop_target.connect("leave", self.on_drag_leave)

        # Enable drag & drop on main_box
        self.main_box.add_controller(drop_target)
    
    def _all_images(self, files):
        for file in files:
            info = file.query_info(
                "standard::content-type",
                0,
                None
            )
            if not info.get_content_type().startswith("image/"):
                return False
        return True

    def on_drag_enter(self, target, x, y):
        self.main_box.add_css_class("dragging")
        return Gdk.DragAction.COPY

    def on_drag_leave(self, target):
        self.main_box.remove_css_class("dragging")

    def on_drop(self, target, value, x, y):
        self.main_box.remove_css_class("dragging")

        files = value.get_files()

        all_images = True

        for file in files:
            info = file.query_info(
                "standard::content-type",
                0,
                None
            )
            if not info.get_content_type().startswith("image/"):
                all_images = False

        if not all_images:
            toast = Adw.Toast.new("Please drop only image files")
            toast.set_timeout(2)
            self.toast_overlay.add_toast(toast)
            return False
        
        for file in files:
            print(file.get_uri())

        return True
