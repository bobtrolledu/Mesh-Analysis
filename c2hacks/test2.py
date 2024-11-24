from ursina import *
import Path_Finding as PF
import Heat_Map as HM

# Initialize the Ursina app
app = Ursina(development_mode=True)


nodes = []
obstacles = []
power_node = None
heatmap_nodes = []

popup_text = None

ambient = AmbientLight()

#sun = DirectionalLight(position=Vec3(5,5, -100))
#sun.look_at(Vec3(0,0,0))
#sun.intensity = 0.5

light1 = PointLight(position=Vec3(-6, -6, 10))
#light2 = PointLight(position=Vec3(6, -6, 10))
#light3 = PointLight(position=Vec3(-6, 6, 10))
#light4 = PointLight(position=Vec3(6, 6, 10))

type = "low"

low_value = 5.0
medium_value = 5.0
high_value = 5.0
industrial_value = 5.0
commercial_value = 5.0

power_weights = {
            "low": low_value,
            "medium": medium_value,
            "high": high_value,
            "commercial": industrial_value,
            "industrial": commercial_value,
            "park": 0,
            "power": 0
        }

pivot = Entity()
pivot_rotate = Entity()
camera.orthographic = True
camera.fov = 15  # Controls the size of the orthographic view (adjust as needed)
camera.parent = pivot
pivot.parent = pivot_rotate
start = None
grid_shift_x = 0
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
    print(Vec3(
        round(position.x / grid_size) * grid_size,
        round(position.y / grid_size) * grid_size,
        round(position.z / grid_size) * grid_size
    ))
    return Vec3(
        round(position.x / grid_size) * grid_size,
        round(position.y / grid_size) * grid_size,
        round(position.z / grid_size) * grid_size
    )

def update_params():
    global low_value, medium_value, high_value, commercial_value, industrial_value, power_weights
    low_value = round(low_density_slider.value, 4)
    medium_value = round(medium_density_slider.value, 4)
    high_value = round(high_density_slider.value, 4)
    commercial_value = round(commercial_slider.value, 4)
    industrial_value = round(industrial_slider.value, 4)
    power_weights = {
        "low": low_value,
        "medium": medium_value,
        "high": high_value,
        "commercial": industrial_value,
        "industrial": commercial_value,
        "park": 0,
        "power": 0
    }

# Function to show a popup with the building's name
def show_popup(cube):
    global popup_text, low_value, medium_value, high_value, commercial_value, industrial_value

    # If a popup already exists, destroy it
    if popup_text:
        destroy(popup_text)

    if cube.name == "Low Density Building":
        data = low_value
    elif cube.name == "Medium Density Building":
        data = medium_value
    elif cube.name == "High Density Building":
        data = high_value
    elif cube.name == "Commercial Building":
        data = commercial_value
    elif cube.name == "Industrial Building":
        data = industrial_value
    elif cube.name == "Park":
        data = 0
    elif cube.name == "Power Generation":
        data = 0
    # Create the popup
    popup_text = Text(
        text=f"Building: {cube.name} \n Power consumption: {data}",
        position=(mouse.position.x + 0.1, mouse.position.y + 0.1),  # Adjust the position of the popup
        origin=(0, 0),
        scale=1,
        background=True
    )

# Function to destroy the popup
def destroy_popup():
    global popup_text
    if popup_text:
        destroy(popup_text)
        popup_text = None


def add_cube(position):
    global type, power_node, obstacles, nodes
    size = None
    current_color = None
    name = None
    snapped_position = snap_to_grid(position, grid_size = 0.5)  # Snap to the grid

    if type == "low":
        size = (0.5, 0.5, 0.5)
        current_color = color.hex("9ee2f0")
        name = "Low Density Building"
    elif type == "medium":
        size = (0.5, 0.5, 0.5)
        current_color = color.hex("fbb1b1")
        name = "Medium Density Building"
    elif type == "high":
        size = (0.5, 0.5, 1.0)
        current_color = color.hex("fde58b")
        name = "High Density Building"
    elif type == "commercial":
        size = (0.5, 0.5, 0.5)
        current_color = color.hex("d08d2e")
        name = "Commercial Building"
    elif type == "industrial":
        size = (0.5, 0.5, 0.5)
        current_color = color.hex("2a2b2a")
        name = "Industrial Building"
    elif type == "park":
        size = (0.5, 0.5, 0.5)
        current_color = color.hex("629460")
        name = "Park"
    elif type == "power":
        size = (0.5, 0.5, 1)
        current_color = color.magenta
        name = "Power Generation"

    if name == "Low Density Building":
        Look = 'folder/house.obj'
    elif name == "Medium Density Building":
        Look = 'folder/medium.obj'
    elif name == "Park":
        Look = 'folder/park.obj'
    elif name == "Industrial Building":
        Look = 'folder/industrial.obj'
    elif name == "Commercial Building":
        Look = 'folder/market.obj'
    elif name == "High Density Building":
        Look = 'folder/medium.obj'
    elif name == "Power Generation":
        Look = 'folder/market.obj'
    else:
        Look = 'cube'
    if name == "Industrial Building":
        snapped_position = snapped_position - (0, 0, -0.25)
    if name == "Park":
        snapped_position = snapped_position - (0, 0, -0.1)
    cube = Entity(

        model = Look, double_sided = True,
        color = current_color,
        position = snapped_position - (0, 0, size[2] / 2),
        collider = 'box',  # Add a box collider for detecting mouse hover
        scale = (size[0]/2, size[1]/2, size[2]/2),
        name = name,
        cast_shadows = True
    )

    heatmap_nodes.append(cube)

    if type == "power":
        if power_node is None:
            global start
            power_node = cube
            start = (cube.position.x * 2 + 10, cube.position.y * 2 + 10)
        else:
            destroy(cube)
            return
    elif type == "park":
        obstacles.append(cube)
        return
    else:
        nodes.append(cube)

# Define a function to add a new entity at the mouse's x and y position
def add_entity():
    # Use the mouse's position in 2D screen space to set the x and y of the entity
    mouse_x, mouse_y, _ = mouse.position  # Mouse position in screen space (-1 to 1)
    # Create a new entity at the x and y position with z set to 0
    add_cube(position = mouse.position * camera.fov)



# Input handling
def input(key):
    global is_dragging, previous_mouse_position, power_node

    if key == 'left mouse down':  # Add a new entity on left mouse click
        if mouse.hovered_entity != button:
            if mouse.hovered_entity not in button_group:
                if orthographic_locked:
                    if mouse.hovered_entity in nodes:
                        hovered_cube = mouse.hovered_entity
                        nodes.remove(hovered_cube)
                        heatmap_nodes.remove(hovered_cube)
                        destroy(hovered_cube)
                    elif mouse.hovered_entity in obstacles:
                        hovered_cube = mouse.hovered_entity
                        obstacles.remove(hovered_cube)
                        heatmap_nodes.remove(hovered_cube)
                        destroy(hovered_cube)
                    elif mouse.hovered_entity is power_node:
                        hovered_cube = mouse.hovered_entity
                        power_node = None
                        #if not heatmap_nodes:
                        #    heatmap_nodes.remove(hovered_cube)
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
        pivot_rotate.rotation_z += (delta.x + delta.y) * 100

    if not orthographic_locked:
        for entity in nodes:
            if entity.hovered:
                show_popup(entity)
        for entity in obstacles:
            if entity.hovered:
                show_popup(entity)
        if power_node and power_node.hovered:
            show_popup(power_node)

        if not mouse.hovered_entity or mouse.hovered_entity is grid:
            destroy_popup()

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

def analyze_nodes():
    global start
    simulator = PF.SlimeMoldSimulator(grid_size=20, endpoints=nodes, obstacle_chance=0, start_coords=start, obstacles=obstacles)
    simulator.run()
    simulator.plot()

def draw_heatmap():
    heatmap = HM.HeatMap(nodes=heatmap_nodes,power_weights=power_weights)
    heatmap.generate_heatmap()

def enable_wp():
    wp.enabled = True

#UI
# Create a group of buttons
button_group = []

# Define the buttons and add them to the group
park = Button(model="quad", text = "Park", color=color.gray, position=(-0.6, 0.3), scale=(0.2, 0.1))
low = Button(model="quad", text="Low Density", color=color.gray, position=(-0.6, 0.2), scale=(0.2, 0.1))
medium = Button(model="quad", text="Medium Density", color=color.gray, position=(-0.6, 0.1), scale=(0.2, 0.1))
high = Button(model="quad", text="High Density", color=color.gray, position=(-0.6, 0), scale=(0.2, 0.1))
commercial = Button(model="quad", text = "Commercial", color=color.gray, position=(-0.6, -0.1), scale=(0.2, 0.1))
industrial = Button(model="quad", text = "Industrial", color=color.gray, position=(-0.6, -0.2), scale=(0.2, 0.1))
power = Button(model="quad", text = "Power", color=color.gray, position=(-0.6, -0.3), scale=(0.2, 0.1))

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
low.color = color.hex("629460")  # Make the first button selected initially

# Function to handle button selection
def on_button_click(button):
    global type
    # Deactivate all buttons in the group
    for b in button_group:
        b.color = color.gray  # Change color to indicate inactive state

    # Activate the selected button
    button.color = color.hex("629460")  # Change color to indicate active state

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
    position=(0.6, -0.4),  # Adjust position to act as a sidebar
    on_click=toggle_orthographic
)

analyze_button = Button(
    model='quad',
    text= "Analyze",
    color=color.azure,
    scale=(0.25, 0.1),
    position=(0.6, -0.3),
    on_click=analyze_nodes
)

heatmap_button = Button(
    model='quad',
    text="Show Heatmap",
    color=color.azure,
    scale=(0.25, 0.1),
    position=(0.6, -0.2),
    on_click=draw_heatmap
)

parameters_button = Button(
    model='quad',
    text="Show Parameters",
    color=color.azure,
    scale=(0.25, 0.1),
    position=(0.6, -0.1),
    on_click=enable_wp
)

bar = Entity(
    parent=camera.ui,
    model='quad',
    color=color.random_color(),
    scale=(0.3, 1),
    position=(-0.6, 0),
    z = 10
)

# Create individual elements first
low_density_slider = ThinSlider(0, 10, default=5, step=0.25, dynamic= False, on_value_changed = update_params)
medium_density_slider = ThinSlider(0, 10, default=5, step=0.25, dynamic= False, on_value_changed = update_params)
high_density_slider = ThinSlider(0, 10, default=5, step=0.25, dynamic= False, on_value_changed = update_params)
commercial_slider = ThinSlider(0, 10, default=5, step=0.25, dynamic= False, on_value_changed = update_params)
industrial_slider = ThinSlider(0, 10, default=5, step=0.25, dynamic= False, on_value_changed = update_params)

# Now define the window panel
wp = WindowPanel(
    title='Set Parameters',
    content=(
        Text("Low Density"),
        low_density_slider,
        Text("Medium Density"),
        medium_density_slider,
        Text("High Density"),
        high_density_slider,
        Text("Commercial"),
        commercial_slider,
        Text("Industrial"),
        industrial_slider
    ),
    popup=True
)
wp.y = wp.panel.scale_y / 2 * wp.scale_y    # center the window panel
wp.layout()

# Instructions for the user
grid = Entity(model=Grid(20, 20), scale=(10, 10, 1), color=color.light_gray, collider = 'box', position=(grid_shift_x, grid_shift_y, 0), receive_shadows = True)

# Run the app
app.run()
