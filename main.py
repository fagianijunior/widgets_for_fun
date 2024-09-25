import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from NotificationsWindow import NotificationsWindow
from CpuWindow import CpuWindow
from GithubWindow import GithubWindow

def main():
    notifications_win = NotificationsWindow()
    notifications_win.connect("destroy", Gtk.main_quit)
    notifications_win.show_all()

    cpu_win = CpuWindow()
    cpu_win.connect("destroy", Gtk.main_quit)
    cpu_win.show_all()

    github_win = GithubWindow()
    github_win.connect("destroy", Gtk.main_quit)
    github_win.show_all()

    Gtk.main()

if __name__ == "__main__":
    main()