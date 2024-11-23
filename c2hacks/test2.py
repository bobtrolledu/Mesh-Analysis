from ursina import *
import random

# Initialize the Ursina app
app = Ursina()

cubes = []

pivot = Entity()
pivot_rotate = Entity()

camera.orthographic = True
camera.fov = 15  # Controls the size of the orthographic view (adjust as needed)
camera.parent = pivot
pivot.parent = pivot_rotate

# Variables for rotation tracking
is_dragging = False  # Tracks whether the right mouse button is held
previous_mouse_position = Vec2(0, 0)  # Tracks the previous mouse position

# Variables for the sidebar button
orthographic_locked = True
is_animating = False
zoom_factor = 1  # Used for scaling the FOV (in orthographic mode)

def add_cube(position, type):
    if type == "low":
        cube = Entity(
            model='cube',
            color=color.random_color(),
            position=position,
            collider='box',  # Add a box collider for detecting mouse hover
        )
    elif type == "medium":
        cube = Entity(
            model='cube',
            color=color.random_color(),
            position=position,
            collider='box',  # Add a box collider for detecting mouse hover
            scale = (1,1,2)
        )
    elif type == "high":
        cube = Entity(
            model='cube',
            color=color.random_color(),
            position=position,
            collider='box',  # Add a box collider for detecting mouse hover
            scale = (1,1,3)
        )
    elif type == "commercial":
        cube = Entity(
            model='cube',
            color=color.random_color(),
            position=position,
            collider='box',  # Add a box collider for detecting mouse hover
            scale = (2,2,1)
        )
    elif type == "industrial":
        cube = Entity(
            model='cube',
            color=color.random_color(),
            position=position,
            collider='box',  # Add a box collider for detecting mouse hover
            scale = (2,2,2)
        )

    cubes.append(cube)

# Define a function to add a new entity at the mouse's x and y position
def add_entity():
    # Use the mouse's position in 2D screen space to set the x and y of the entity
    mouse_x, mouse_y, _ = mouse.position  # Mouse position in screen space (-1 to 1)
    # Create a new entity at the x and y position with z set to 0
    add_cube(position = mouse.position * camera.fov, type = "medium")

# Input handling
def input(key):
    global is_dragging, previous_mouse_position
    if key == 'left mouse down':  # Add a new entity on left mouse click
        if mouse.hovered_entity != button:
            if orthographic_locked:
                if mouse.hovered_entity in cubes:
                    hovered_cube = mouse.hovered_entity
                    cubes.remove(hovered_cube)
                    destroy(hovered_cube)
                else:
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

# Scroll wheel zoom function
def scroll_wheel():
    global zoom_factor, camera
    # Zoom in (scroll up) or zoom out (scroll down)
    if mouse.scroll != 0:
        if orthographic_locked:
            # In orthographic mode, adjust the FOV
            camera.fov += mouse.scroll * 0.5  # Adjust the multiplier for desired zoom speed
            camera.fov = max(1, min(camera.fov, 50))  # Limit the FOV to a range between 1 and 50
        else:
            # In perspective mode, adjust the camera's position
            camera.position.z += mouse.scroll * 0.5  # Adjust the multiplier for zoom speed
            camera.position.z = max(-20, min(camera.position.z, -1))  # Limit the zoom range

#UI
# Create a group of buttons
button_group = []

# Define the buttons and add them to the group
low = Button(text="Low Density", color=color.gray, position=(-0.5, 0.2), scale=(0.2, 0.1))
medium = Button(text="Medium Density", color=color.gray, position=(-0.5, 0.1), scale=(0.2, 0.1))
high = Button(text="High Density", color=color.gray, position=(-0.5, 0), scale=(0.2, 0.1))
commercial = Button(text = "Commercial", color=color.gray, position=(-0.5, -0.1), scale=(0.2, 0.1))
industrial = Button(text = "Industrial", color=color.gray, position=(-0.5, -0.2), scale=(0.2, 0.1))

# Add buttons to the button group
button_group.append(low)
button_group.append(medium)
button_group.append(high)
button_group.append(commercial)
button_group.append(industrial)

# Set the on_click handlers for each button
low.on_click = lambda: on_button_click(low)
medium.on_click = lambda: on_button_click(medium)
high.on_click = lambda: on_button_click(high)
commercial.on_click = lambda: on_button_click(commercial)
industrial.on_click = lambda: on_button_click(industrial)

# Set the first button as the default selected one
low.color = color.green  # Make the first button selected initially

# Function to handle button selection
def on_button_click(button):
    # Deactivate all buttons in the group
    for b in button_group:
        b.color = color.gray  # Change color to indicate inactive state

    # Activate the selected button
    button.color = color.green  # Change color to indicate active state
    print(f'{button.text} is selected')

button = Button(
    model='quad',
    text="Orthographic: On",
    color=color.azure,
    scale=(0.25, 0.1),
    position=(-0.6, 0),  # Adjust position to act as a sidebar
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
grid = Entity(model=Grid(50, 50), scale=(10, 10, 1), color=color.light_gray)

# Run the app
app.run()
