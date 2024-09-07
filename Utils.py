class Utils:
    @staticmethod
    def get_screen_size(display):
        mon_geoms = [display.get_monitor(i).get_geometry() for i in range(display.get_n_monitors())]
        
        if not mon_geoms:
            return 0, 0
        
        x_min = min(r.x for r in mon_geoms)
        x_max = max(r.x + r.width for r in mon_geoms)
        y_min = min(r.y for r in mon_geoms)
        y_max = max(r.y + r.height for r in mon_geoms)
        
        return x_max - x_min, y_max - y_min