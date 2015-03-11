#! /usr/bin/env python
__author__ = 'cteam'

from gi.repository import Gtk, GObject
from glob import glob
import os
import os.path
from string import rstrip
import sys
import ConfigParser


class BatteryTray:
    interval = 5000

    def __init__(self):

        battery_path = None
        self.theme_switcher_window = Gtk.Window(title="Theme Switcher")
        self.theme_switcher_window.set_position(Gtk.WindowPosition.CENTER)
        self.theme_switcher_window.set_border_width(10)
        self.theme_switcher_window.set_default_size(200, 20)

        self.config = ConfigParser.RawConfigParser()
        self.config.read('config/config.cfg')
        default_theme = self.config.get('config', 'default_theme')
        self.theme = self.config.get('themes', self.config.get('config', 'default_theme'))

        theme_combo = Gtk.ComboBox()
        theme_list = Gtk.ListStore(str, str)
        i = 0
        for name, path in self.config.items('themes'):
            if name == default_theme:
                theme_combo.set_active(i)

            i += 1
            theme_list.append([name, path])

        theme_combo.set_model(theme_list)
        theme_combo.connect("changed", self.on_theme_change)
        renderer_text = Gtk.CellRendererText()
        theme_combo.pack_start(renderer_text, True)
        theme_combo.add_attribute(renderer_text, "text", 0)
        theme_combo.show()

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        vbox.pack_start(theme_combo, False, False, True)
        vbox.show()

        self.theme_switcher_window.add(vbox)

        for psu in glob("/sys/class/power_supply/*"):
            with open(os.path.join(psu, 'type')) as f:
                if f.read().startswith('Battery'):
                    battery_path = psu

        if not battery_path:
            print "No battery found!"
            sys.exit(1)

        self.battery_full = os.path.join(battery_path, "charge_full")
        self.battery_charging = os.path.join(battery_path, "charge_now")

        if not os.path.exists(self.battery_full):
            self.battery_full = os.path.join(battery_path, "energy_full")
            self.battery_charging = os.path.join(battery_path, "energy_now")

        self.battery_state = os.path.join(battery_path, "status")
        self.image_location = os.path.join(os.path.dirname(sys.argv[0]), self.theme + "/battery")
        self.tray = Gtk.StatusIcon()
        self.tray.connect('activate', self.refresh)

        # Create menu
        menu = Gtk.Menu()

        theme_switcher = Gtk.MenuItem("Theme Switcher")
        theme_switcher.show()
        theme_switcher.connect("activate", self.show_theme_switcher)
        menu.append(theme_switcher)

        about_item = Gtk.MenuItem("About")
        about_item.show()
        about_item.connect("activate", self.show_about)
        menu.append(about_item)

        quit_item = Gtk.MenuItem("Quit")
        quit_item.show()
        quit_item.connect("activate", self.quit)
        menu.append(quit_item)

        self.tray.connect('popup-menu', self.show_menu, menu)

        self.refresh(None)
        self.tray.set_visible(True)

        ## keep looking <:
        GObject.timeout_add(self.interval, self.refresh, False)

    def save_default(self, theme):
        self.config.set('config', 'default_theme', theme)
        with open('config/config.cfg', 'wb') as configfile:
            self.config.write(configfile)

    def show_theme_switcher(self, widget):
        self.theme_switcher_window.show()

    def on_theme_change(self, combo):
        tree_iter = combo.get_active_iter()
        if tree_iter is not None:
            model = combo.get_model()
            theme = model[tree_iter][0]
            self.theme = self.config.get('themes', theme)
            self.save_default(theme)
            self.image_location = os.path.join(os.path.dirname(sys.argv[0]), self.theme + "/battery")
            self.refresh(None)

    def show_menu(self, widget, event_button, event_time, menu):
        menu.popup(None, None,
                   None,
                   None,
                   event_time,
                   Gtk.get_current_event_time()
        )

    def show_about(self, widget):

        dialog = Gtk.MessageDialog(widget.get_toplevel(), 0, Gtk.MessageType.INFO, Gtk.ButtonsType.OK, "Battery 1.0")
        dialog.set_title('About')
        dialog.set_position(Gtk.WindowPosition.CENTER)
        dialog.format_secondary_text("By Cteam-Lab")
        dialog.run()

        dialog.destroy()

    def quit(self, widget):
        Gtk.main_quit()

    def refresh(self, widget):
        def slurp(filename):
            f = open(filename)
            return f.read()

        b_level = int(round(float(slurp(self.battery_charging)) / float(slurp(self.battery_full)) * 100))
        b_file = self.image_location + "-" + str(b_level / 30) + ".png"

        if rstrip(slurp(self.battery_state)) == "Charging":
            b_file = self.image_location + "-connect.png"

        self.tray.set_tooltip_text(
            "%s: %d%%" %
            (rstrip(slurp(self.battery_state)), b_level)
        )

        if os.path.exists(b_file):
            self.tray.set_from_file(b_file)

        return True


if __name__ == '__main__':
    app = BatteryTray()
    Gtk.main()
