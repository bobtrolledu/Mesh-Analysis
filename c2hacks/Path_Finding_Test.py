import random
import matplotlib.pyplot as plt

# Constants
GRID_SIZE = 100  # Define grid size (10x10 grid)
NUM_END_POINTS = 10  # Number of end points
SLIME_RADIUS = 1  # How far the slime spreads each iteration (1 unit step)
OBSTACLE_CHANCE = 0.1  # Chance to create an obstacle in the space
START_NODE_COLOR = 'red'
END_NODE_COLOR = 'green'
SLIME_COLOR = 'yellow'
OBSTACLE_COLOR = 'gray'
PATH_COLOR = 'blue'
obstacles = []

# Create a grid where each cell is (x, y)
grid = [(x, y) for x in range(GRID_SIZE) for y in range(GRID_SIZE)]

# Randomly generate the start node and multiple end nodes (ensuring they are distinct)
start = random.choice(grid)
end_points = random.sample([p for p in grid if p != start], NUM_END_POINTS)

# Generate obstacles in the grid
for _ in range(int(len(grid) * OBSTACLE_CHANCE)):  # Add random obstacles
    obstacle = random.choice([p for p in grid if p != start and p not in end_points])
    if obstacle not in obstacles:
        obstacles.append(obstacle)

# Function to check if a position is valid (not an obstacle)
def is_valid_position(position):
    if position not in obstacles:
        (x, y) = position
        if x >= 0 and y >= 0 and x <= GRID_SIZE - 1 and y <= GRID_SIZE - 1:
            return True
    return False

# Function to run the slime mold algorithm to find a path to any endpoint
def slime_mold_algorithm(start, end_points):
    slime_positions = [start]
    visited = set([start])
    parent_map = {start: None}  # To reconstruct the path

    while slime_positions:
        new_positions = []

        for slime in slime_positions:
            # Spread the slime in 4 cardinal directions (up, down, left, right)
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                new_position = (slime[0] + dx, slime[1] + dy)

                if is_valid_position(new_position) and new_position not in visited:
                    visited.add(new_position)
                    new_positions.append(new_position)
                    parent_map[new_position] = slime

                    # Check if we reached any of the end points
                    if new_position in end_points:
                        return parent_map, new_position  # Return the path once we reach any end point

        slime_positions = new_positions

    return None, None  # Return None if no path is found

# Function to reconstruct the path from the parent map
def reconstruct_path(parent_map, start, end):
    path = []
    current = end
    while current != start:
        path.append(current)
        current = parent_map.get(current)
    path.append(start)
    path.reverse()
    return path

# Run the slime mold algorithm to find paths to all end points
paths = []
for end in end_points:
    parent_map, found_end = slime_mold_algorithm(start, [end])
    if parent_map:
        path = reconstruct_path(parent_map, start, found_end)
        paths.append(path)

# Plotting the results

fig, ax = plt.subplots(figsize=(20, 20))

# Plot obstacles
obstacle_x, obstacle_y = zip(*obstacles) if obstacles else ([], [])
ax.scatter([x for x, y in obstacles], [y for x, y in obstacles], color=OBSTACLE_COLOR, s=100, marker='s',
           label="Obstacles")

# Plot nodes (start and end points)
start_x, start_y = start
ax.scatter(start_x, start_y, color=START_NODE_COLOR, s=100, label='Start')
for end in end_points:
    end_x, end_y = end
    ax.scatter(end_x, end_y, color=END_NODE_COLOR, s=100, label='End')

# Plot slime paths (yellow points and blue paths)
for path in paths:
    if path:
        path_x, path_y = zip(*path)
        ax.plot(path_x, path_y, color=PATH_COLOR, linewidth=2)

# Label the plot
ax.set_title("Slime Mold Algorithm Finding Paths to Multiple Endpoints in Grid")
ax.legend(loc="best")
ax.set_xlim(-0.5, GRID_SIZE - 0.5)
ax.set_ylim(-0.5, GRID_SIZE - 0.5)
#ax.set_xticks(range(GRID_SIZE))
#ax.set_yticks(range(GRID_SIZE))
ax.set_xlabel("X Coordinate")
ax.set_ylabel("Y Coordinate")
ax.grid(False)

plt.show()

