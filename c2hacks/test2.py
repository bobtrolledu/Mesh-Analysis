from ursina import *
import random

# Initialize the Ursina app
app = Ursina()

pivot = Entity()

camera.orthographic = True
camera.fov = 10  # Controls the size of the orthographic view (adjust as needed)
camera.parent = pivot


# Variables for rotation tracking
is_dragging = False  # Tracks whether the right mouse button is held
previous_mouse_position = Vec2(0, 0)  # Tracks the previous mouse position

# Variables for the sidebar button
orthographic_locked = True
zoom_factor = 1  # Used for scaling the FOV (in orthographic mode)

# Define a function to add a new entity at the mouse's x and y position
def add_entity():
    # Use the mouse's position in 2D screen space to set the x and y of the entity
    mouse_x, mouse_y,_ = mouse.position  # Mouse position in screen space (-1 to 1)
    # Create a new entity at the x and y position with z set to 0
    new_entity = Entity(
        model='cube',
        color=color.random_color(),
        position=(mouse_x * 10, mouse_y * 10, 0)  # Scale mouse position for better spread
    )

# Input handling
def input(key):
    global is_dragging, previous_mouse_position
    if key == 'left mouse down':  # Add a new entity on left mouse click
        add_entity()
    elif key == 'right mouse down':  # Start dragging on right mouse down
        is_dragging = True
        previous_mouse_position = Vec2(mouse.x, mouse.y)  # Store the starting mouse position
    elif key == 'right mouse up':  # Stop dragging on right mouse up
        is_dragging = False

# Update function for handling rotation
def update():
    global is_dragging, previous_mouse_position
    if is_dragging:
        # Calculate mouse movement delta
        delta = Vec2(mouse.x, mouse.y) - previous_mouse_position
        previous_mouse_position = Vec2(mouse.x, mouse.y)  # Update the previous mouse position

        # Apply rotation to the camera based on the delta
        pivot.rotation_y += delta.x * 100  # Rotate around the y-axis (horizontal drag)
        pivot.rotation_x -= delta.y * 100  # Rotate around the x-axis (vertical drag)

# Function to toggle orthographic view
def toggle_orthographic():
    global orthographic_locked
    orthographic_locked = not orthographic_locked  # Toggle the state
    camera.orthographic = orthographic_locked
    button.text = f"Orthographic: {'On' if orthographic_locked else 'Off'}"
    camera.fov = 100

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


button = Button(
    text="Orthographic: On",
    color=color.azure,
    scale=(0.2, 0.1),
    position=(-0.5, 0),  # Adjust position to act as a sidebar
    on_click=toggle_orthographic
)

# Instructions for the user
Text("Click LEFT MOUSE BUTTON to add a new entity at the mouse's X and Y position.", position=(0, 0.45), origin=(0, 0), scale=1.5)
grid = Entity(model=Grid(80, 80), scale=(10, 10, 1), color=color.light_gray)

# Run the app
app.run()
