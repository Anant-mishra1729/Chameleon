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

from gi.repository import Adw, Gtk, Gdk


@Gtk.Template(resource_path="/io/github/forklore/Chameleon/window.ui")
class ChameleonWindow(Adw.ApplicationWindow):
    __gtype_name__ = "ChameleonWindow"

    main_box = Gtk.Template.Child()
    toast_overlay = Gtk.Template.Child()
    add_image_files_button = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        drop_target = Gtk.DropTarget.new(
            Gdk.FileList,
            Gdk.DragAction.COPY,
        )

        drop_target.connect("drop", self.on_drop)
        drop_target.connect("enter", self.on_drag_enter)
        drop_target.connect("leave", self.on_drag_leave)

        self.main_box.add_controller(drop_target)

        self.add_image_files_button.connect(
            "clicked",
            self.on_add_image_files_clicked,
        )

        self.images = []

    def toast(self, message):
        toast = Adw.Toast.new(message)
        toast.set_timeout(3)
        self.toast_overlay.add_toast(toast)

    def _all_images(self, files):
        return all(
            file.query_info(
                "standard::content-type",
                0,
                None,
            )
            .get_content_type()
            .startswith("image/")
            for file in files
        )

    def _select_images(self, files):
        if len(files) < 2:
            self.toast("Select at least 2 images")
            return

        if not self._all_images(files):
            self.toast("Only image files are supported")
            return

        self.images = [file.get_path() for file in files]

        print(self.images)

    def on_drag_enter(self, target, x, y):
        self.main_box.add_css_class("dragging")
        return Gdk.DragAction.COPY

    def on_drag_leave(self, target):
        self.main_box.remove_css_class("dragging")

    def on_drop(self, target, value, x, y):
        self.main_box.remove_css_class("dragging")

        self._select_images(value.get_files())

        return True

    def on_add_image_files_clicked(self, button):
        dialog = Gtk.FileChooserNative(
            title="Select Images",
            transient_for=self,
            action=Gtk.FileChooserAction.OPEN,
            accept_label="_Open",
            cancel_label="_Cancel",
        )

        dialog.set_select_multiple(True)

        image_filter = Gtk.FileFilter()
        image_filter.set_name("Images")

        for pattern in (
            "*.png",
            "*.jpg",
            "*.jpeg",
            "*.webp",
            "*.heic",
        ):
            image_filter.add_pattern(pattern)

        dialog.add_filter(image_filter)
        dialog.set_filter(image_filter)

        dialog.connect("response", self.on_file_dialog_response)

        dialog.show()

    def on_file_dialog_response(self, dialog, response):
        if response == Gtk.ResponseType.ACCEPT:
            model = dialog.get_files()

            files = [model.get_item(i) for i in range(model.get_n_items())]

            self._select_images(files)

        dialog.destroy()
