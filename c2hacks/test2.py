from sympy.codegen.cnodes import sizeof
from ursina import *
import Path_Finding as PF

# Initialize the Ursina app
app = Ursina()

power_check = False
cubes = []
obstacles = []

type = "low"

pivot = Entity()
pivot_rotate = Entity()
camera.orthographic = True
camera.fov = 15  # Controls the size of the orthographic view (adjust as needed)
camera.parent = pivot
pivot.parent = pivot_rotate
start = None
grid_shift_x = 5
grid_shift_y = 0

# Variables for rotation tracking
is_dragging = False  # Tracks whether the right mouse button is held
previous_mouse_position = Vec2(0, 0)  # Tracks the previous mouse position

# Variables for the sidebar button
orthographic_locked = True
is_animating = False
zoom_factor = 1  # Used for scaling the FOV (in orthographic mode)

# Grid snapping function
def snap_to_grid(position, grid_size):
    return Vec3(
        round(position.x / grid_size) * grid_size,
        round(position.y / grid_size) * grid_size,
        round(position.z / grid_size) * grid_size
    )

def add_cube(position):
    global type, power_check, start
    size = None
    current_color = None
    snapped_position = snap_to_grid(position, grid_size = 1)  # Snap to the grid

    if type == "low":
        size = (1, 1, 1)
        current_color = color.hex("9ee2f0")
    elif type == "medium":
        size = (1, 1, 2)
        current_color = color.hex("fbb1b1")
    elif type == "high":
        size = (1, 1, 3)
        current_color = color.hex("fde58b")
    elif type == "commercial":
        size = (1, 1, 1)
        current_color = color.hex("d08d2e")
    elif type == "industrial":
        size = (1, 1, 2)
        current_color = color.hex("2a2b2a")
    elif type == "park":
        size = (1, 1, 0.5)
        current_color = color.hex("629460")
    elif type == "power":
        size = (1, 1, 0.5)
        current_color = color.hex("629466")

    cube = Entity(
        model = 'cube',
        color = current_color,
        position = snapped_position - (0, 0, size[2] / 2),
        collider = 'box',  # Add a box collider for detecting mouse hover
        scale = size,
    )

    if type == "park":
        obstacles.append(cube)

    if type == "power":
        if not power_check:
            power_check = cube
            start = (cube.position.x + (5 - grid_shift_x), cube.position.y + (5 - grid_shift_y))
            return
        else:
            destroy(cube)
            return
    elif type != "power":
        cubes.append(cube)

# Define a function to add a new entity at the mouse's x and y position
def add_entity():
    # Use the mouse's position in 2D screen space to set the x and y of the entity
    mouse_x, mouse_y, _ = mouse.position  # Mouse position in screen space (-1 to 1)
    # Create a new entity at the x and y position with z set to 0
    add_cube(position = mouse.position * camera.fov)

# Input handling
def input(key):
    global is_dragging, previous_mouse_position
    if key == 'left mouse down':  # Add a new entity on left mouse click
        if mouse.hovered_entity != button:
            if mouse.hovered_entity not in button_group:
                if orthographic_locked:
                    if mouse.hovered_entity in cubes:
                        hovered_cube = mouse.hovered_entity
                        cubes.remove(hovered_cube)
                        destroy(hovered_cube)
                    elif mouse.hovered_entity == grid:
                        add_entity()
    elif key == 'right mouse down':  # Start dragging on right mouse down
        if mouse.hovered_entity != button:
            if not orthographic_locked:
                is_dragging = True
                previous_mouse_position = Vec2(mouse.x, mouse.y)  # Store the starting mouse position
    elif key == 'right mouse up':  # Stop dragging on right mouse up
        is_dragging = False

def orthographic_out_spin_animation():
    pivot.animate('rotation_x', pivot.rotation_x - 50, duration=2, curve=curve.in_out_expo)


def orthographic_in_spin_animation():
    pivot.animate('rotation_x', pivot.rotation_x + 50, duration=2, curve=curve.in_out_expo)

# Update function for handling rotation
def update():
    global is_dragging, previous_mouse_position
    if is_dragging:
        # Calculate mouse movement delta
        delta = Vec2(mouse.x, mouse.y) - previous_mouse_position
        previous_mouse_position = Vec2(mouse.x, mouse.y)  # Update the previous mouse position

        # Apply rotation to the camera based on the delta
        #pivot_rotate.rotation_y += delta.x * 100  # Rotate around the y-axis (horizontal drag)
        #pivot_rotate.rotation_x -= delta.y * 100  # Rotate around the x-axis (vertical drag)
        pivot_rotate.rotation_z += (delta.x + delta.y) * 100

# Function to toggle orthographic view
def toggle_orthographic():
    global orthographic_locked, is_animating
    simulator = PF.SlimeMoldSimulator(grid_size=10, endpoints=cubes, obstacle_chance=0, start_coords=start)
    simulator.run()
    simulator.plot()
    if is_animating:
        return

    is_animating = True

    if orthographic_locked:
        orthographic_locked = not orthographic_locked  # Toggle the state
        camera.orthographic = orthographic_locked
        button.text = f"Orthographic: Off"
        camera.fov = 60
        orthographic_out_spin_animation()
        orthographic_locked = False
    else:
        orthographic_locked = not orthographic_locked  # Toggle the state
        camera.orthographic = orthographic_locked
        button.text = f"Orthographic: On"
        pivot_rotate.animate('rotation_z', pivot_rotate.rotation_z - pivot_rotate.rotation_z, duration=2, curve=curve.in_out_expo)
        orthographic_in_spin_animation()
        camera.fov = 15
        orthographic_locked = True

    invoke(lambda: reset_animation_flag(), delay=2)



def reset_animation_flag():
    global is_animating
    is_animating = False

#UI
# Create a group of buttons
button_group = []

# Define the buttons and add them to the group
park = Button(text = "Park", color=color.gray, position=(-0.6, 0.3), scale=(0.2, 0.1))
low = Button(text="Low Density", color=color.gray, position=(-0.6, 0.2), scale=(0.2, 0.1))
medium = Button(text="Medium Density", color=color.gray, position=(-0.6, 0.1), scale=(0.2, 0.1))
high = Button(text="High Density", color=color.gray, position=(-0.6, 0), scale=(0.2, 0.1))
commercial = Button(text = "Commercial", color=color.gray, position=(-0.6, -0.1), scale=(0.2, 0.1))
industrial = Button(text = "Industrial", color=color.gray, position=(-0.6, -0.2), scale=(0.2, 0.1))
power = Button(text = "Power", color=color.gray, position=(-0.6, -0.3), scale=(0.2, 0.1))

# Add buttons to the button group
button_group.append(park)
button_group.append(low)
button_group.append(medium)
button_group.append(high)
button_group.append(commercial)
button_group.append(industrial)
button_group.append(power)

# Set the on_click handlers for each button
park.on_click = lambda: on_button_click(park)
low.on_click = lambda: on_button_click(low)
medium.on_click = lambda: on_button_click(medium)
high.on_click = lambda: on_button_click(high)
commercial.on_click = lambda: on_button_click(commercial)
industrial.on_click = lambda: on_button_click(industrial)
power.on_click = lambda: on_button_click(power)

# Set the first button as the default selected one
low.color = color.green  # Make the first button selected initially

# Function to handle button selection
def on_button_click(button):
    global type
    # Deactivate all buttons in the group
    for b in button_group:
        b.color = color.gray  # Change color to indicate inactive state

    # Activate the selected button
    button.color = color.green  # Change color to indicate active state

    if button == low:
        type = "low"
    elif button == medium:
        type = "medium"
    elif button == high:
        type = "high"
    elif button == commercial:
        type = "commercial"
    elif button == industrial:
        type = "industrial"
    elif button == park:
        type = "park"
    elif button == power:
        type = "power"

button = Button(
    model='quad',
    text="Orthographic: On",
    color=color.azure,
    scale=(0.25, 0.1),
    position=(-0.6, -0.4),  # Adjust position to act as a sidebar
    on_click=toggle_orthographic
)

bar = Entity(
    parent=camera.ui,
    model='quad',
    color=color.random_color(),
    scale=(0.3, 1),
    position=(-0.6, 0),
    z = 10
)

# Instructions for the user
Text("Click LEFT MOUSE BUTTON to add a new entity at the mouse's X and Y position.", position=(0, 0.45), origin=(0, 0), scale=1.5)
grid = Entity(model=Grid(10, 10), scale=(10, 10, 1), color=color.light_gray, collider = 'box', position=(grid_shift_x, grid_shift_y, 0))

# Run the app
app.run()

