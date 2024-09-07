import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib
import subprocess
import json
from Utils import Utils

class NotificationsWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="widget - Central de Notificações")
        
        self.set_default_size(400, Utils.get_screen_size(Gdk.Display.get_default())[1] - 4)
        
        self.setup_ui()
        self.refresh_notifications()
        GLib.timeout_add_seconds(60, self.refresh_notifications)
        
    def setup_ui(self):
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(self.box)

        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.box.pack_start(button_box, False, False, 0)

        for label, callback in [("Atualizar", self.refresh_notifications), ("Pausar", self.toggle_notifications)]:
            button = Gtk.Button(label=label)
            button.connect("clicked", callback)
            button_box.pack_start(button, True, True, 0)

        self.pause_button = button_box.get_children()[1]

        self.notifications_list = Gtk.ListBox()
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.add(self.notifications_list)
        self.box.pack_start(scrolled, True, True, 0)

    def toggle_notifications(self, widget):
        subprocess.run(["dunstctl", "set-paused", "toggle"])
        self.update_pause_button()
        
    def update_pause_button(self):
        paused = subprocess.run(["dunstctl", "is-paused"], capture_output=True, text=True).stdout.strip()
        self.pause_button.set_label("Retomar" if paused == "true" else "Pausar")

    def refresh_notifications(self, widget=None):
        self.notifications_list.foreach(lambda widget: self.notifications_list.remove(widget))

        history = json.loads(subprocess.run(["dunstctl", "history"], capture_output=True, text=True).stdout)

        for notification in history["data"][0]:
            row = self.create_notification_row(notification)
            self.notifications_list.add(row)

        self.notifications_list.show_all()
        return True

    def create_notification_row(self, notification):
        row = Gtk.ListBoxRow()
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        row.add(vbox)

        message = Gtk.Label(xalign=0)
        message.set_markup(notification["message"]["data"])
        message.set_line_wrap(True)
        vbox.pack_start(message, True, True, 0)

        delete_button = Gtk.Button(label="Excluir")
        delete_button.connect("clicked", self.remove_notification, notification["id"]["data"])
        vbox.pack_start(delete_button, False, False, 0)

        return row

    def remove_notification(self, widget, id_notification):
        subprocess.run(["dunstctl", "history-rm", str(id_notification)])
        self.refresh_notifications()