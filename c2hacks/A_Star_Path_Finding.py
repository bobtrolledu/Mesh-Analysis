import heapq
import matplotlib.pyplot as plt
from matplotlib import ticker

end_pointCoords = []

# Define the Cell class
class Cell:
    def __init__(self):
        self.parent_i = 0  # Parent cell's row index
        self.parent_j = 0  # Parent cell's column index
        self.f = float('inf')  # Total cost of the cell (g + h)
        self.g = float('inf')  # Cost from start to this cell
        self.h = 0  # Heuristic cost from this cell to destination
        self.start_node_color = 'green'
        self.end_node_color = 'red'
        self.slime_color = 'yellow'
        self.obstacle_color = 'gray'
        self.path_color = 'blue'

# Define the size of the grid
ROW = 20
COL = 20
src = []
dest = []
grid = []
total_paths = []
    # Check if a cell is valid (within the grid)
def is_valid(row, col):
    global COL
    return (row >= 0) and (row < ROW) and (col >= 0) and (col < COL)

# Check if a cell is unblocked
def is_unblocked(grid, row, col):
    return grid[int(row)][int(col)] == 1

# Check if a cell is the destination
def is_destination(row, col, dest):
    return row == dest[0] and col == dest[1]

# Calculate the heuristic value of a cell (Euclidean distance to destination)
def calculate_h_value(row, col, dest):
    return ((row - dest[0]) ** 2 + (col - dest[1]) ** 2) ** 0.5

# Trace the path from source to destination
def trace_path(cell_details, dest):
    print("The Path is ")
    path = []
    row = dest[0]
    col = dest[1]

    # Trace the path from destination to source using parent cells
    while not (cell_details[int(row)][int(col)].parent_i == row and cell_details[int(row)][int(col)].parent_j == col):
        path.append((row, col))
        temp_row = cell_details[int(row)][int(col)].parent_i
        temp_col = cell_details[int(row)][int(col)].parent_j
        row = temp_row
        col = temp_col

    # Add the source cell to the path
    path.append((row, col))
    # Reverse the path to get the path from source to destination
    path.reverse()

    # Print the path
    for i in path:
        print("->", i, end=" ")
    print()
    total_paths.append(path)

# Implement the A* search algorithm
def a_star_search(grid, src, dest):
    # Check if the source and destination are valid
    if not is_valid(src[0], src[1]) or not is_valid(dest[0], dest[1]):
        print("Source or destination is invalid")
        return

    # Check if the source and destination are unblocked
    if not is_unblocked(grid, src[0], src[1]) or not is_unblocked(grid, dest[0], dest[1]):
        print("Source or the destination is blocked")
        return

    # Check if we are already at the destination
    if is_destination(src[0], src[1], dest):
        print("We are already at the destination")
        return

    # Initialize the closed list (visited cells)
    closed_list = [[False for _ in range(COL)] for _ in range(ROW)]
    # Initialize the details of each cell
    cell_details = [[Cell() for _ in range(COL)] for _ in range(ROW)]

    # Initialize the start cell details
    i = int(src[0])
    j = int(src[1])

    cell_details[i][j].f = 0
    cell_details[i][j].g = 0
    cell_details[i][j].h = 0
    cell_details[i][j].parent_i = i
    cell_details[i][j].parent_j = j

    # Initialize the open list (cells to be visited) with the start cell
    open_list = []
    heapq.heappush(open_list, (0.0, i, j))

    # Initialize the flag for whether destination is found
    found_dest = False

    # Main loop of A* search algorithm
    while len(open_list) > 0:
        # Pop the cell with the smallest f value from the open list
        p = heapq.heappop(open_list)

        # Mark the cell as visited
        i = p[1]
        j = p[2]
        closed_list[i][j] = True

        # For each direction, check the successors
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0),(1, 1), (-1, -1), (-1, 1), (1, -1)]
        for dir in directions:
            new_i = i + dir[0]
            new_j = j + dir[1]

            # If the successor is valid, unblocked, and not visited
            if is_valid(new_i, new_j) and is_unblocked(grid, new_i, new_j) and not closed_list[new_i][new_j]:
                # If the successor is the destination
                if is_destination(new_i, new_j, dest):
                    # Set the parent of the destination cell
                    cell_details[new_i][new_j].parent_i = i
                    cell_details[new_i][new_j].parent_j = j
                    print("The destination cell is found")
                    # Trace and print the path from source to destination
                    trace_path(cell_details, dest)
                    found_dest = True
                    return
                else:
                    # Calculate the new f, g, and h values
                    g_new = cell_details[i][j].g + 1.0
                    h_new = calculate_h_value(new_i, new_j, dest)
                    f_new = g_new + h_new

                    # If the cell is not in the open list or the new f value is smaller
                    if cell_details[new_i][new_j].f == float('inf') or cell_details[new_i][new_j].f > f_new:
                        # Add the cell to the open list
                        heapq.heappush(open_list, (f_new, new_i, new_j))
                        # Update the cell details
                        cell_details[new_i][new_j].f = f_new
                        cell_details[new_i][new_j].g = g_new
                        cell_details[new_i][new_j].h = h_new
                        cell_details[new_i][new_j].parent_i = i
                        cell_details[new_i][new_j].parent_j = j

    # If the destination is not found after visiting all cells
    if not found_dest:
        print("Failed to find the destination cell")\

def set_starting(obstacles,start_coords,endpoints):
    for i in range(ROW):
        grid.append([])
        for j in range(COL):
            if (i,j) not in obstacles:
                grid[i].append(1)
            elif (i,j) in obstacles:
                grid[i].append(0)
                print("oops")
    src = start_coords
    for i in endpoints:
        dest.append((i.position.x * 2 + 10, i.position.y * 2 + 10))

    for i in dest:
        a_star_search(grid, src, i)
    return total_paths

def plot(obstacles, start_coords):
    """Visualize the results using matplotlib."""
    fig, ax = plt.subplots(figsize=(10, 10))

    # Plot obstacles
    for obstacle in obstacles:
        obstacle_x, obstacle_y = obstacle
        ax.scatter(
            obstacle_x, obstacle_y, color='grey', s=500, marker='s', label="Obstacles"
    )

    # Plot nodes (start and end points)
    start_x, start_y = start_coords
    ax.scatter(start_x, start_y, color='green', s=250, label='Start')
    for end in dest:
        end_x, end_y = end
        ax.scatter(end_x, end_y, color='red', s=250, label='End')

    # Plot slime paths
    for path in total_paths:
        if path:
            path_x, path_y = zip(*path)
            ax.plot(path_x, path_y, color='blue', linewidth=2)

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

