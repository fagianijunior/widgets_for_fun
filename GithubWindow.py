import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, Gdk
import requests
from ConfigManager import ConfigManager

class GithubWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Widget - GitHub Repositórios")
        
        self.load_config()
        
        self.set_default_size(self.width, self.height)
        if self.x is not None and self.y is not None:
            self.move(self.x, self.y)
        
        self.setup_ui()
        self.update_github_info()
        GLib.timeout_add_seconds(300, self.update_github_info)  # Atualiza a cada 5 minutos
        
        self.connect("configure-event", self.on_configure_event)
        self.connect("delete-event", self.on_delete_event)
        
    def load_config(self):
        config = ConfigManager.load_config("github")
        default_config = {"width": 400, "height": 300, "x": None, "y": None}
        
        self.width = config.get("width", default_config["width"])
        self.height = config.get("height", default_config["height"])
        self.x = config.get("x")
        self.y = config.get("y")
        
        # Lista de usuários a serem monitorados
        self.users = config.get("users", [])
        
    def save_config(self):
        config = {
            "width": self.get_allocated_width(),
            "height": self.get_allocated_height(),
            "x": self.get_position()[0],
            "y": self.get_position()[1],
            "users": self.users
        }
        ConfigManager.save_config("github", config)
        
    def on_configure_event(self, widget, event):
        self.save_config()
        return False
        
    def on_delete_event(self, widget, event):
        self.save_config()
        return False

    def setup_ui(self):
        self.scroll = Gtk.ScrolledWindow()
        self.scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.add(self.scroll)
        
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.scroll.add(self.box)
        
        self.total_repos_label = Gtk.Label()
        self.box.pack_start(self.total_repos_label, False, False, 0)
        
        self.repos_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.box.pack_start(self.repos_box, True, True, 0)

    def update_github_info(self):
        try:
            # Limpar widgets antigos
            for child in self.repos_box.get_children():
                self.repos_box.remove(child)
            
            total_repos = 0
            
            for user in self.users:
                response = requests.get(f'https://api.github.com/users/{user}/repos')
                repos = response.json()
                
                total_repos += len(repos)
                self.total_repos_label.set_text(f"Total de repositórios públicos: {total_repos}")
                
                for repo in repos:
                    if repo['open_issues_count'] > 0:
                        repo_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
                        
                        repo_name = Gtk.Label(label=f"{user}/{repo['name']}")
                        repo_box.pack_start(repo_name, False, False, 0)
                        
                        issues_count = Gtk.Label(label=f"Issues: {repo['open_issues_count']}")
                        repo_box.pack_end(issues_count, False, False, 0)
                        
                        self.repos_box.pack_start(repo_box, False, False, 0)
            
            self.show_all()
        except Exception as e:
            print(f"Erro ao obter informações do GitHub: {e}")
        
        return True

def main():
    win = GithubWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()