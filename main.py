import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from NotificationsWindow import NotificationsWindow

def main():
    win = NotificationsWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()