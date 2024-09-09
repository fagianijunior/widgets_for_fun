import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib
import subprocess
import json
from Utils import Utils
import os

class NotificationsWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="widget - Central de Notificações")
        
        self.config_file = os.path.expanduser("~/.config/notifications_widget_config.json")
        self.load_config()
        
        self.set_default_size(self.width, self.height)
        if self.x is not None and self.y is not None:
            self.move(self.x, self.y)
        
        self.setup_ui()
        self.refresh_notifications()
        GLib.timeout_add_seconds(60, self.refresh_notifications)
        
        self.connect("configure-event", self.on_configure_event)
        self.connect("delete-event", self.on_delete_event)
        
    def load_config(self):
        default_config = {
            "width": 400,
            "height": Utils.get_screen_size(Gdk.Display.get_default())[1] - 4,
            "x": None,
            "y": None
        }
        if os.path.exists(self.config_file):
            with open(self.config_file, "r") as f:
                config = json.load(f)
        else:
            config = default_config
        
        self.width = config.get("width", default_config["width"])
        self.height = config.get("height", default_config["height"])
        self.x = config.get("x")
        self.y = config.get("y")
        
    def save_config(self):
        config = {
            "width": self.get_allocated_width(),
            "height": self.get_allocated_height(),
            "x": self.get_position()[0],
            "y": self.get_position()[1]
        }
        with open(self.config_file, "w") as f:
            json.dump(config, f)
        
    def on_configure_event(self, widget, event):
        self.save_config()
        return False
        
    def on_delete_event(self, widget, event):
        self.save_config()
        return False

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

        # Adicionar campo de filtro
        filter_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.box.pack_start(filter_box, False, False, 0)

        filter_label = Gtk.Label(label="Filtrar:")
        filter_box.pack_start(filter_label, False, False, 0)

        self.filter_entry = Gtk.Entry()
        self.filter_entry.connect("changed", self.on_filter_changed)
        filter_box.pack_start(self.filter_entry, True, True, 0)

        self.notifications_list = Gtk.ListBox()
        self.notifications_list.set_filter_func(self.filter_notifications)
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

        self.notifications_list.invalidate_filter()
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

    def on_filter_changed(self, entry):
        self.notifications_list.invalidate_filter()

    def filter_notifications(self, row):
        text = self.filter_entry.get_text().lower()
        if not text:
            return True
        label = row.get_children()[0].get_children()[0]
        return text in label.get_text().lower()