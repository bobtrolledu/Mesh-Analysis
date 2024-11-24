import matplotlib.pyplot as plt
import numpy as np
import math
import display_plot as DP
from PIL import Image
from io import BytesIO
from ursina import *

class HeatMap:
    def __init__(self, nodes, power_weights):
        self.nodes = nodes
        self.power_weights = power_weights
        self.intensity_array = []

    def generate_heatmap(self):
        building_colors = {
            "low": "blue",
            "medium": "green",
            "high": "red",
            "commercial": "orange",
            "industrial": "gray",
            "park": "lime",
            "power": "magenta"
        }

        # Extract positions and weights
        x = [node.position.x * 2 + 10 for node in self.nodes]
        y = [node.position.y * 2 + 10for node in self.nodes]
        types = [node.name.split()[0].lower() for node in self.nodes]
        weights = [self.power_weights.get(t, 0) for t in types]

        if not x or not y:  # Skip if no nodes exist
            print("No buildings to generate heatmap!")
            return

        # KDE parameters
        h = 4  # Increased radius of influence

        # Create grid
        x_grid, y_grid = [], []
        for i in range(41):
            x_grid.append(i / 2)
            y_grid.append(i / 2)
        x_mesh, y_mesh = np.meshgrid(x_grid, y_grid)

        # KDE Quartic Kernel
        def kde_quartic(d, h):
            dn = d / h
            P = (15 / 16) * (1 - dn ** 2) ** 2
            return max(0, P)  # Ensure non-negative values

        # Calculate intensity
        intensity_list = []
        for j in range(len(x_mesh)):
            intensity_row = []
            for k in range(len(x_mesh[0])):
                kde_value_list = []
                for i in range(len(x)):
                    d = math.sqrt((x_mesh[j][k] - x[i]) ** 2 + (y_mesh[j][k] - y[i]) ** 2)
                    p = kde_quartic(d, h) * weights[i] if d <= h else 0
                    kde_value_list.append(p)
                intensity_row.append(sum(kde_value_list))
            intensity_list.append(intensity_row)

        # Convert to numpy array for plotting
        intensity = np.array(intensity_list)
        self.intensity_array = intensity.tolist()

        # Plot heatmap
        plt.figure(figsize=(10, 10))
        plt.pcolormesh(x_mesh, y_mesh, intensity, shading='auto', cmap='jet')
        plt.colorbar(label="Power Density")
        for building_type, color in building_colors.items():
            type_x = [x[i] for i in range(len(types)) if types[i] == building_type]
            type_y = [y[i] for i in range(len(types)) if types[i] == building_type]
            plt.scatter(type_x, type_y, c=color, label=building_type.capitalize(), s=20)
        plt.legend(title="Building Types")
        plt.title("Building Power Density Heatmap")
        plt.xlabel("X")
        plt.ylabel("Y")
        plt.gca().set_aspect('equal', adjustable='box')  # Maintain aspect ratio

        buf = BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)

        # Convert the image to a texture
        img = Image.open(buf)
        texture = Texture(img)
        buf.close()
        DP.add_plot(texture)

    def get_intensity_array(self):
        return self.intensity_array
