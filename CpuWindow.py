import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, Gdk
import psutil
import cairo
import json
import os

class CpuWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="widget - Uso da CPU")
        
        self.config_file = os.path.expanduser("~/.config/cpu_widget_config.json")
        self.load_config()
        
        self.set_default_size(self.width, self.height)
        if self.x is not None and self.y is not None:
            self.move(self.x, self.y)
        
        self.cpu_usage = []
        self.cpu_cores_usage = []
        self.max_data_points = 60  # 1 minuto de dados
        self.show_cores = False
        
        self.setup_ui()
        GLib.timeout_add(1000, self.update_cpu_usage)
        
        self.connect("configure-event", self.on_configure_event)
        self.connect("delete-event", self.on_delete_event)
        
    def load_config(self):
        default_config = {"width": 400, "height": 300, "x": None, "y": None}
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
        self.drawing_area = Gtk.DrawingArea()
        self.drawing_area.connect("draw", self.on_draw)
        self.drawing_area.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.drawing_area.connect("button-press-event", self.on_click)
        self.add(self.drawing_area)
        
    def on_click(self, widget, event):
        self.show_cores = not self.show_cores
        self.drawing_area.queue_draw()
        return True

    def update_cpu_usage(self):
        cpu_percent = psutil.cpu_percent()
        self.cpu_usage.append(cpu_percent)
        
        if len(self.cpu_usage) > self.max_data_points:
            self.cpu_usage.pop(0)
        
        self.cpu_cores_usage = psutil.cpu_percent(percpu=True)
        
        self.drawing_area.queue_draw()
        return True
    
    def on_draw(self, widget, cr):
        width = widget.get_allocated_width()
        height = widget.get_allocated_height()
        
        # Desenhar fundo
        cr.set_source_rgb(0.1, 0.1, 0.1)
        cr.rectangle(0, 0, width, height)
        cr.fill()
        
        if self.show_cores:
            self.draw_cores_graph(cr, width, height)
        else:
            self.draw_overall_graph(cr, width, height)
        
    def draw_overall_graph(self, cr, width, height):
        # Desenhar grade
        cr.set_source_rgba(0.5, 0.5, 0.5, 0.5)
        cr.set_line_width(0.5)
        for i in range(0, 101, 20):
            y = height - (i / 100.0 * height)
            cr.move_to(0, y)
            cr.line_to(width, y)
            cr.stroke()
        
        # Desenhar gráfico
        if len(self.cpu_usage) > 1:
            cr.set_source_rgb(0, 0.7, 0)
            cr.set_line_width(2)
            cr.move_to(0, height - (self.cpu_usage[0] / 100.0 * height))
            for i, usage in enumerate(self.cpu_usage):
                x = i / (len(self.cpu_usage) - 1) * width
                y = height - (usage / 100.0 * height)
                cr.line_to(x, y)
            cr.stroke()
        
        # Desenhar texto de porcentagem
        if self.cpu_usage:
            cr.set_source_rgb(1, 1, 1)
            cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            cr.set_font_size(20)
            text = f"{self.cpu_usage[-1]:.1f}%"
            (x, y, width, height, dx, dy) = cr.text_extents(text)
            cr.move_to(10, 30)
            cr.show_text(text)

    def draw_cores_graph(self, cr, width, height):
        if not self.cpu_cores_usage:
            return

        num_cores = len(self.cpu_cores_usage)
        bar_width = width / (num_cores * 2)
        
        for i, usage in enumerate(self.cpu_cores_usage):
            x = i * bar_width * 2 + bar_width / 2
            bar_height = (usage / 100.0) * height
            
            # Desenhar barra
            cr.set_source_rgb(0, 0.7, 0)
            cr.rectangle(x, height - bar_height, bar_width, bar_height)
            cr.fill()
            
            # Desenhar texto de porcentagem
            cr.set_source_rgb(1, 1, 1)
            cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            cr.set_font_size(12)
            text = f"{usage:.1f}%"
            (tx, ty, twidth, theight, dx, dy) = cr.text_extents(text)
            cr.move_to(x + (bar_width - twidth) / 2, height - bar_height - 5)
            cr.show_text(text)
            
            # Desenhar número do core
            # text = f"{i}"
            # (tx, ty, twidth, theight, dx, dy) = cr.text_extents(text)
            # cr.move_to(x + (bar_width - twidth) / 2, height - 5)
            # cr.show_text(text)

def main():
    win = CpuWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()