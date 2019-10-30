# -*- coding: utf-8 -*-
#
# Copyright (C) 2012-2015 bendikro bro.devel+yarss2@gmail.com
#
# This file is part of YaRSS2 and is licensed under GNU General Public License 3.0, or later, with
# the additional special exception to link portions of this program with the OpenSSL library.
# See LICENSE for more details.
#

import deluge.component as component

from .common import Gtk
from .base import DialogBase


class DialogCookie(DialogBase):

    def __init__(self, gtkui, cookie_data):
        super().__init__("dialog_cookie.ui", "dialog_cookie")
        self.gtkUI = gtkui
        self.cookie_data = cookie_data
        self.builder.connect_signals({
            "on_button_add_cookie_data_clicked": self.on_button_add_cookie_data_clicked,
            "on_button_remove_cookie_data_clicked": self.on_button_remove_cookie_data_clicked,
            "on_button_save_clicked": self.on_button_save_clicked,
            "on_button_cancel_clicked": self.destroy,
            "on_txt_site_url_query_tooltip": self.on_txt_site_url_query_tooltip,
            "on_dialog_cookies_response": self.on_dialog_response,
        })
        self.treeview = self.setup_cookie_list()

        if self.cookie_data:
            self.get_object("text_site").set_text(self.cookie_data["site"])

        # Update cookie data list
        self.update_cookie_values_list()

    def show(self):
        cookie_list = self.get_object("viewport_list_cookie_values")
        cookie_list.add(self.treeview)
        cookie_list.show_all()
        self.dialog.set_transient_for(component.get("Preferences").pref_dialog)
        self.dialog.set_title("Edit Cookies" if "key" in self.cookie_data else "Add Cookies")
        self.dialog.run()

    def update_cookie_values_list(self):
        """Update list from values"""
        self.list_store.clear()
        for key in self.cookie_data["value"]:
            self.list_store.append((key, self.cookie_data["value"][key]))
        self.update_remove_cookie_sensitive()

    def on_button_save_clicked(self, button):
        """Saves cookie to config"""
        site = self.get_object("text_site").get_text().strip()
        if site != "":
            self.cookie_data["site"] = site
            self.gtkUI.save_cookie(self.cookie_data)
            self.destroy()

    def on_button_remove_cookie_data_clicked(self, button):
        tree_sel = self.treeview.get_selection()
        (tm, ti) = tree_sel.get_selected()
        if not ti:
            return
        v0 = tm.get_value(ti, 0)
        del self.cookie_data["value"][v0]
        self.update_cookie_values_list()

    def on_button_add_cookie_data_clicked(self, button):
        key = self.get_object("text_key").get_text().strip()
        value = self.get_object("text_value").get_text().strip()

        if len(key) > 0 and len(value):
            if key in self.cookie_data["value"]:
                return
            self.cookie_data["value"][key] = value
            self.update_cookie_values_list()
            self.get_object("text_key").set_text("")
            self.get_object("text_value").set_text("")

    def update_remove_cookie_sensitive(self, *args):
        """
        Set sensitivity of remove button depending on whether
        a cookie is currently selected or not

        """
        tree_sel = self.treeview.get_selection()
        (tm, ti) = tree_sel.get_selected()
        self.get_object("button_remove_cookie_data").set_sensitive(ti is not None)

    def setup_cookie_list(self):
        # name and key
        self.list_store = Gtk.ListStore(str, str)
        treeview = Gtk.TreeView(model=self.list_store)

        tree_sel = treeview.get_selection()
        tree_sel.connect("changed", self.update_remove_cookie_sensitive)

        renderertext = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Key/Name", renderertext, text=0)
        treeview.append_column(column)

        renderertext = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Value", renderertext, text=1)
        treeview.append_column(column)
        return treeview

    def on_txt_site_url_query_tooltip(self, widget, x, y, keyboard_mode, tooltip):
        return set_tooltip_markup(tooltip, "This value is used to match the URLs of the RSS feeds")
