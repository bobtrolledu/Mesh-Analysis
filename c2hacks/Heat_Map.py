import matplotlib.pyplot as plt
import numpy as np
import math

class HeatMap:
    def __init__(self, nodes):
        self.nodes = nodes

    def generate_heatmap(self):
        power_weights = {
            "low": 0.1,
            "medium": 0.2,
            "high": 0.3,
            "commercial": 0.4,
            "industrial": 0.5,
            "park": 0,
            "power": 0
        }

        building_colors = {
            "low" : "blue",
            "medium" : "green",
            "high" : "red",
            "commercial" : "orange",
            "industrial" : "gray",
            "park" : "lime",
            "power" : "magenta"
        }

        # Extract positions and weights
        x = [node.position.x for node in self.nodes]
        y = [node.position.y for node in self.nodes]
        types = [node.name.split()[0].lower() for node in self.nodes]
        weights = [power_weights.get(t, 0) for t in types]

        if not x or not y:  # Skip if no nodes exist
            print("No buildings to generate heatmap!")
            return

        # KDE parameters
<<<<<<< HEAD
        grid_size = 0.3  # Grid size for KDE
        h = 3  # Radius of influence
=======
        grid_size = 1  # Grid size for KDE
        h = 10  # Radius of influence
>>>>>>> a222078fe8c175869f5e2a17d7b5b46c4741ee9e

        # Define grid bounds
        x_min, x_max = min(x) - h, max(x) + h
        y_min, y_max = min(y) - h, max(y) + h

        # Create grid
        x_grid = np.arange(x_min, x_max, grid_size)
        y_grid = np.arange(y_min, y_max, grid_size)
        x_mesh, y_mesh = np.meshgrid(x_grid, y_grid)
        xc = x_mesh + (grid_size / 2)
        yc = y_mesh + (grid_size / 2)

        # KDE Quartic Kernel
        def kde_quartic(d, h):
            dn = d / h
            P = (15 / 16) * (1 - dn**2)**2
            return P

        # Calculate intensity
        intensity_list = []
        for j in range(len(xc)):
            intensity_row = []
            for k in range(len(xc[0])):
                kde_value_list = []
                for i in range(len(x)):
                    # Calculate distance
                    d = math.sqrt((xc[j][k] - x[i])**2 + (yc[j][k] - y[i])**2)
                    if d <= h:
                        p = kde_quartic(d, h) * weights[i]
                    else:
                        p = 0
                    kde_value_list.append(p)
                intensity_row.append(sum(kde_value_list))
            intensity_list.append(intensity_row)

        # Convert to numpy array for plotting
        intensity = np.array(intensity_list)

        # Plot heatmap
        plt.figure(figsize=(10, 10))
        plt.pcolormesh(x_mesh, y_mesh, intensity, shading='auto', cmap='jet')
        plt.colorbar(label="Power Density")
        for building_type, color in building_colors.items():
            type_x = [x[i] for i in range(len(types)) if types [i] == building_type]
            type_y = [y[i] for i in range(len(types)) if types[i] == building_type]
            plt.scatter(type_x, type_y, c=color, label=building_type.capitalize(), s=20)  # Mark buildings
        plt.legend(title = "Building Types")
        plt.title("Building Power Density Heatmap")
        plt.xlabel("X")
        plt.ylabel("Y")
        plt.show()