import random
import matplotlib.pyplot as plt
from matplotlib import ticker

end_pointCoords = []
obstacles = []

class SlimeMoldSimulator:

    def __init__(self, grid_size, endpoints, obstacle_chance, start_coords, obstacles):
        self.end_pointCoords = end_pointCoords
        self.obstacles = obstacles
        self.grid_size = grid_size + 1
        self.endpoints = endpoints
        for i in endpoints:
            end_pointCoords.append((i.position.x * 2 + 10, i.position.y * 2 + 10))

        self.obstacle_chance = obstacle_chance
        # Constants
        self.start_node_color = 'green'
        self.end_node_color = 'red'
        self.slime_color = 'yellow'
        self.obstacle_color = 'gray'
        self.path_color = 'blue'

        # Grid and nodes
        self.grid = [(x, y) for x in range(self.grid_size) for y in range(self.grid_size)]
        self.start = start_coords

        self.obstacles = self.generate_obstacles(obstacles)
        self.paths = []

    def generate_obstacles(self, obstacle_list):
        for i in obstacle_list:
            obstacle_x = i.position.x * 2 + 10
            obstacle_y = i.position.y * 2 + 10
            obstacles.append((obstacle_x, obstacle_y))
        return obstacles

    def is_valid_position(self, position):
        """Check if the position is valid (within grid and not an obstacle)."""
        if position not in self.obstacles:
            x, y = position
            return 0 <= x < self.grid_size and 0 <= y < self.grid_size
        return False

    def slime_mold_algorithm(self, start, end_points):
        """Run the slime mold algorithm to find a path to any endpoint."""
        slime_positions = [start]
        visited = {start}
        parent_map = {start: None}  # To reconstruct the path

        while slime_positions:
            new_positions = []

            for slime in slime_positions:
                # Spread the slime in 4 cardinal directions (up, down, left, right)
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    new_position = (slime[0] + dx, slime[1] + dy)

                    if self.is_valid_position(new_position) and new_position not in visited:
                        visited.add(new_position)
                        new_positions.append(new_position)
                        parent_map[new_position] = slime

                        # Check if we reached any of the end points
                        if new_position in end_points:
                            return parent_map, new_position

            slime_positions = new_positions

        return None, None  # Return None if no path is found

    def reconstruct_path(self, parent_map, start, end):
        """Reconstruct the path from the parent map."""
        path = []
        current = end
        while current != start:
            path.append(current)
            current = parent_map.get(current)
        path.append(start)
        path.reverse()
        return path

    def run(self):
        """Run the slime mold simulation and find paths to all endpoints."""
        self.paths = []
        for end in self.end_pointCoords:
            parent_map, found_end = self.slime_mold_algorithm(self.start, [end])
            if parent_map:
                path = self.reconstruct_path(parent_map, self.start, found_end)
                self.paths.append(path)

    def plot(self):
        """Visualize the results using matplotlib."""
        fig, ax = plt.subplots(figsize=(10, 10))

        # Plot obstacles
        for obstacle in self.obstacles:
            obstacle_x, obstacle_y = obstacle
            ax.scatter(
                obstacle_x, obstacle_y, color=self.obstacle_color, s=500, marker='s', label="Obstacles"
        )

        # Plot nodes (start and end points)
        start_x, start_y = self.start
        ax.scatter(start_x, start_y, color=self.start_node_color, s=250, label='Start')
        for end in self.end_pointCoords:
            end_x, end_y = end
            ax.scatter(end_x, end_y, color=self.end_node_color, s=250, label='End')

        # Plot slime paths
        for path in self.paths:
            if path:
                path_x, path_y = zip(*path)
                ax.plot(path_x, path_y, color=self.path_color, linewidth=2)

        # Label the plot
        ax.set_title("Slime Mold Algorithm Finding Paths to Multiple Endpoints in Grid")
        ax.set_xlabel("X Coordinate")
        ax.set_ylabel("Y Coordinate")
        ax.yaxis.set(major_locator = ticker.MultipleLocator(5), minor_locator = ticker.MultipleLocator(1))
        ax.xaxis.set(major_locator = ticker.MultipleLocator(5), minor_locator = ticker.MultipleLocator(1))
        ax.grid(which='major', alpha=0.5)
        ax.grid(which='minor', alpha=0.2, linestyle='--')
        plt.xlim(-0.5, 20.5)
        plt.ylim(-0.5, 20.5)
        plt.grid(True)
        plt.show()

    def get_path(self):
        return self.paths