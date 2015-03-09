#! /usr/bin/env python
__author__ = 'cteam'

from gi.repository import Gtk, GObject
from glob import glob
import os
import os.path
from string import rstrip
import sys


class BatteryTray:
    def __init__(self):

        battery_path = None

        for psu in glob("/sys/class/power_supply/*"):
            with open(os.path.join(psu, 'type')) as f:
                if f.read().startswith('Battery'):
                    print "Found battery at %s" % psu
                    battery_path = psu

        if not battery_path:
            print "No battery found!"
            sys.exit(1)

        INTERVAL = 20000

        self.BATT_FULL = os.path.join(battery_path, "charge_full")
        self.BATT_NOW = os.path.join(battery_path, "charge_now")

        if not os.path.exists(self.BATT_FULL):
            self.BATT_FULL = os.path.join(battery_path, "energy_full")
            self.BATT_NOW = os.path.join(battery_path, "energy_now")

        self.BATT_STATE = os.path.join(battery_path, "status")
        self.IMAGE_LOC = os.path.join(os.path.dirname(sys.argv[0]), "images/battery")

        self.tray = Gtk.StatusIcon()
        self.tray.connect('activate', self.refresh)

        # Create menu
        menu = Gtk.Menu()
        about_item = Gtk.MenuItem("About...")
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

        GObject.timeout_add(INTERVAL, self.refresh, False)

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

        b_level = int(round(float(slurp(self.BATT_NOW)) / float(slurp(self.BATT_FULL)) * 100))
        b_file = self.IMAGE_LOC + "." + str(b_level / 10) + ".png"

        self.tray.set_tooltip_text(
            "%s: %d%%" %
            (rstrip(slurp(self.BATT_STATE)), b_level)
        )

        if os.path.exists(b_file):
            self.tray.set_from_file(b_file)

        return True

if __name__ == '__main__':
    app = BatteryTray()
    Gtk.main()