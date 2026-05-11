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
    add_image_files_button = Gtk.Template.Child()

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

        # File dialog support
        self.add_image_files_button.connect(
            "clicked",
            self.on_add_image_files_clicked,
        )    
        self._file_dialog = None
    
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

        if not self._all_images(files):
            toast = Adw.Toast.new("Only image files are supported")
            toast.set_timeout(3)
            self.toast_overlay.add_toast(toast)
            return False

        if len(files) < 2:
            toast = Adw.Toast.new("Drop at least 2 images")
            toast.set_timeout(3)
            self.toast_overlay.add_toast(toast)
            return False

        for file in files:
            print(file.get_uri())

        return True
    
    def on_add_image_files_clicked(self, button):

        self._file_dialog = Gtk.FileChooserNative(
            title="Select Images",
            transient_for=self,
            action=Gtk.FileChooserAction.OPEN,
            accept_label="_Open",
            cancel_label="_Cancel",
        )
        self._file_dialog.set_select_multiple(True)

        image_filter = Gtk.FileFilter()
        image_filter.set_name("Image Files")

        for pattern in (
            "*.png",
            "*.jpg",
            "*.jpeg",
            "*.webp",
            "*.heic",
        ):
            image_filter.add_pattern(pattern)

        self._file_dialog.add_filter(image_filter)
        self._file_dialog.set_filter(image_filter)

        self._file_dialog.connect(
            "response",
            self.on_add_image_files_response,
        )

        self._file_dialog.show()

    def on_add_image_files_response(self, dialog, response):
        if response == Gtk.ResponseType.ACCEPT:
            model = dialog.get_files()

            for i in range(model.get_n_items()):
                file = model.get_item(i) 
                path = file.get_path()
                print(f"Selected: {path}")


        dialog.destroy()
        self._file_dialog = None