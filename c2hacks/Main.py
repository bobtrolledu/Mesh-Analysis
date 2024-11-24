from ursina import *
import Heat_Map as HM
import Pipe_Animate as PA
import heatpixel as HP
import A_Star_Path_Finding as PF
import display_plot as DP
import matplotlib.pyplot as plt
from PIL import Image
from io import BytesIO

# Initialize the Ursina app
app = Ursina(development_mode=True)
# Set window size (width, height) in pixels
window.size = (16*100, 9*100)  # Adjust the window size as needed
window.title = "Energy Emulator"  # Set the window title
window.draggable = True
window.resizable = True
window.borderless = False
window.show_ursina_splash = True
scene.background_color = color.white

nodes, paths, pipes, initial_path, draw_path, obstacles, heatmap_nodes, heat_pixel,total_energy_use, plot_entity_list = [],[],[],[],[],[],[],[],[],[]

power_node = None
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

low_value, medium_value, high_value, commercial_value, industrial_value = 0, 0, 0, 0, 0

power_weights = {
    "low": low_value,
    "medium": medium_value,
    "high": high_value,
    "commercial": commercial_value,
    "industrial": industrial_value,
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

# Grid snapping function
def snap_to_grid(position, grid_size):
    return Vec3(
        round(position.x / grid_size) * grid_size,
        round(position.y / grid_size) * grid_size,
        round(position.z / grid_size) * grid_size
    )

def update_params():
    global low_value, medium_value, high_value, commercial_value, industrial_value, power_weights
    low_value = round(low_density_slider.value, 4) * 2
    medium_value = round(medium_density_slider.value, 4) * 500
    high_value = round(high_density_slider.value, 4) * 1000
    commercial_value = round(commercial_slider.value, 4) * 50
    industrial_value = round(industrial_slider.value, 4) * 1200
    power_weights = {
        "low": low_value,
        "medium": medium_value,
        "high": high_value,
        "commercial": commercial_value,
        "industrial": industrial_value,
        "park": 0,
        "power": 0
    }

def update_power_weights():
    global low_value, medium_value, high_value, commercial_value, industrial_value, power_weights
    power_weights = {
        "low": low_value,
        "medium": medium_value,
        "high": high_value,
        "commercial": commercial_value,
        "industrial": industrial_value,
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
        popup_data = low_value
    elif cube.name == "Medium Density Building":
        popup_data = medium_value
    elif cube.name == "High Density Building":
        popup_data = high_value
    elif cube.name == "Commercial Building":
        popup_data = commercial_value
    elif cube.name == "Industrial Building":
        popup_data = industrial_value
    elif cube.name == "Park":
        popup_data = 0
    elif cube.name == "Power Generation":
        popup_data = calculate_energy_usage()



        # Create the popup
    popup_text = Text(
        text= if_power_text(cube, popup_data),
        position=(mouse.position.x + 0.1, mouse.position.y + 0.1),  # Adjust the position of the popup
        origin=(0, 0),
        scale=1,
        background=True
    )

def if_power_text(cube, popup_data):
    if cube.name == "Power Generation":
        return f"{cube.name} \n Power Generation needed: {popup_data} kW/h"
    else:
        return f"{cube.name} \n Power consumption Intensity: {popup_data} kW/h"

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
        scale = (size[0]/2.3, size[1]/2.3, size[2]/2.3),
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

def animate_line():
    global paths, draw_path
    draw_path = []
    for i in paths:
        for j in i:
            x, y = j
            draw_path.append(((x - 10) / 2, (y - 10) / 2, 0))

        new_pipe = PA.Pipe_Animate([draw_path[0], draw_path[1]], draw_path)
        new_pipe.animate_pipe()
        pipes.append(new_pipe.get_pipe())
        draw_path = []

def clear():
    global nodes, paths, pipes, initial_path, draw_path, obstacles, heatmap_nodes, heat_pixel, power, power_node
    PF.clean()
    for i in nodes:
        destroy(i)
    for i in pipes:
        destroy(i)
    for i in draw_path:
        destroy(i)
    for i in obstacles:
        destroy(i)
    for i in heatmap_nodes:
        destroy(i)
    for i in heat_pixel:
        for x in i:
            destroy(x)
    nodes, paths, pipes, initial_path, draw_path, obstacles, heatmap_nodes, heat_pixel = [],[],[],[],[],[],[],[]
    power_node = None

# Input handling
def input(key):
    global is_dragging, previous_mouse_position, power_node

    if key == 'left mouse down':  # Add a new entity on left mouse click
        if mouse.hovered_entity != orthogonal:
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
        if mouse.hovered_entity != orthogonal:
            if not orthographic_locked:
                is_dragging = True
                previous_mouse_position = Vec2(mouse.x, mouse.y)  # Store the starting mouse position
    elif key == 'right mouse up':  # Stop dragging on right mouse up
        is_dragging = False

    elif key == 'scroll up':
        if not orthographic_locked:
            camera.fov = max(10, min(80, camera.fov))
            camera.fov -= 500 * time.dt
    elif key == 'scroll down':
        if not orthographic_locked:
            camera.fov = max(10, min(80, camera.fov))
            camera.fov += 500 * time.dt

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

    update_params()

    if orthographic_locked:
        orthographic_locked = not orthographic_locked  # Toggle the state
        camera.orthographic = orthographic_locked
        orthogonal.text = f"Go 2D"
        camera.animate('fov', value = 60, curve=curve.in_out_expo)
        pivot.animate('rotation_x', pivot.rotation_x - 50, duration=2, curve=curve.in_out_expo)
        orthographic_locked = False
    else:
        orthographic_locked = not orthographic_locked  # Toggle the state
        camera.orthographic = orthographic_locked
        orthogonal.text = f"Go 3D"
        pivot_rotate.animate('rotation_z', pivot_rotate.rotation_z - pivot_rotate.rotation_z, duration=2, curve=curve.in_out_expo)
        pivot.animate('rotation_x', pivot.rotation_x + 50, duration=2, curve=curve.in_out_expo)
        camera.animate('fov', value = 15, curve=curve.in_out_expo)
        orthographic_locked = True

    invoke(lambda: reset_animation_flag(), delay=2)

def reset_animation_flag():
    global is_animating
    is_animating = False

def analyze_nodes():
    global start, paths
    if not power_node:
        return

    PF.clean()
    obstacle_coord = []
    for i in obstacles:
        obstacle_coord.append(((i.position.x * 2 + 10), (i.position.y * 2) + 10))
    paths = PF.set_starting(obstacle_coord, start, nodes)
    PF.plot(obstacle_coord, start)
    animate_line()

def calculate_energy_usage():
    global nodes, low_value, medium_value, high_value, commercial_value, industrial_value
    sum = 0
    for node in nodes:
        if node.name == "Low Density Building":
            sum += low_value
        elif node.name == "Medium Density Building":
            sum += medium_value
        elif node.name == "High Density Building":
            sum += high_value
        elif node.name == "Commercial Building":
            sum += commercial_value
        elif node.name == "Industrial Building":
            sum += industrial_value

    print(sum)
    return sum

def map_range(x, in_min, in_max, out_min, out_max):
  return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min

# Function to map intensity to a color gradient
def intensity_to_color(value):
    value = value/255

    if value <= 0.25:
        return lerp(color.blue, color.green, value * 4)  # Blue to Green
    elif value <= 0.5:
        return lerp(color.green, color.yellow, (value - 0.25) * 4)  # Green to Yellow
    elif value <= 0.75:
        return lerp(color.yellow, color.orange, (value - 0.5) * 4)  # Yellow to Orange
    else:
        return lerp(color.orange, color.red, (value - 0.75) * 4)  # Orange to Red

def draw_heatmap():
    global heat_pixel
    heatmap = HM.HeatMap(nodes=heatmap_nodes,power_weights=power_weights)
    heatmap.generate_heatmap()
    intensity_array = heatmap.get_intensity_array()
    max_value = []
    for i in intensity_array:
        max_value.append(max(i))

    normalized_intensity_array = []

    for i in intensity_array:
        new_i = []
        for j in i:
            new_i.append(map_range(j, 0, max(max_value), 0, 255))
        normalized_intensity_array.append(new_i)

    for y, row in enumerate(normalized_intensity_array, 0):
        heat_pixel.append([])
        for x, value in enumerate(row, 0):
            color_value = intensity_to_color(value)
            pixel = HP.heatpixel(
                model="cube",
                color=color_value,
                position= ((x - 20) / 4, (y  - 20) / 4, -(value/100) + 3),  # Adjust position for grid layout
                scale=(1/4, 1/4, 1),
                value=value
            )
            heat_pixel[y].append(pixel)

def update_heatmap(hour):
    global heat_pixel
    simulate_button.text = f"Hour(s) " + str(hour)
    heatmap = HM.HeatMap(nodes=heatmap_nodes, power_weights=power_weights)
    heatmap.generate_heatmap()
    intensity_array = heatmap.get_intensity_array()
    max_value = []
    for i in intensity_array:
        max_value.append(max(i))

    normalized_intensity_array = []

    for i in intensity_array:
        new_i = []
        for j in i:
            new_i.append(map_range(j, 0, max(max_value), 0, 255))
        normalized_intensity_array.append(new_i)

    for y in range(41):
        for x in range(41):
            new_value = normalized_intensity_array[y][x]
            if heat_pixel[y][x].get_intensity() != new_value:
                heat_pixel[y][x].color = intensity_to_color(new_value)
                heat_pixel[y][x].position = ((x - 20) / 4, (y  - 20) / 4, -(new_value/100) + 3)

def simulate(bias, hour):
    global low_value, medium_value, high_value, commercial_value, industrial_value
    if bias:
        if low_value > 10:
            low_value -= 10
        if medium_value > 200:
            medium_value -= 30
        if high_value > 500:
            high_value -= 60
        if commercial_value < 100:
            commercial_value += 10
        if industrial_value < 9000:
            industrial_value += 100
    else:
        if low_value < 600:
            low_value += 30
        if medium_value < 5000:
            medium_value += 60
        if high_value < 8000:
            high_value += 80
        if commercial_value > 50:
            commercial_value -= 10
        if industrial_value > 50:
            industrial_value -= 80

    total_energy_use.append(calculate_energy_usage())
    update_power_weights()
    update_heatmap(hour)

def display_graphs():

    x = []

    for i in range(24):
        x.append(i+1)

    plt.plot(x, total_energy_use)
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)

    # Convert the image to a texture
    img = Image.open(buf)
    texture1 = Texture(img)
    buf.close()
    DP.add_plot(texture1)

    textures = DP.display()

    real_texture_list = [textures[0], textures[1], textures[-1]]

    global plot_entity_list
    counter = -1
    for i in real_texture_list:
        plot_entity = Entity(
            parent=camera.ui,
            model='quad',
            texture=i,
            scale=(0.5, 0.5),  # Adjust scale as needed
            position=(-0.6 * counter, 0, 0),  # Centered
            visible=False,
            z=-80
        )
        counter += 1
        plot_entity_list.append(plot_entity)



def simulate_queue():

    if not heat_pixel:
        print("No heatmap")
        return

    for i in range(24):
        if i > 8 and i < 17:
            invoke(lambda: simulate(1, i + 1), delay=i/4)
        else:
            invoke(lambda: simulate(0, i + 1), delay=i/4)
    simulate_button.text = f"Simulate!"

def enable_wp():
    wp.enabled = True

def enable_analysis_interface():
    analysis_screen.visible = True
    analysis_screen.collider = 'box'
    display_graphs()

    for i in plot_entity_list:
        i.visible = True

def enable_sandbox_interface():
    analysis_screen.visible = False
    analysis_screen.collider = None

    for i in plot_entity_list:
        i.visible = False

#UI
# Create a group of buttons
button_group = []

# Define the buttons and add them to the group
park = Button(model="quad", text = "Green Space", color=color.gray, position=(-0.74, 0.30), scale=(0.2, 0.08), text_size=0.75)
low = Button(model="quad", text="Low Density", color=color.gray, position=(-0.74, 0.21), scale=(0.2, 0.08), text_size=0.75)
medium = Button(model="quad", text="Medium Density", color=color.gray, position=(-0.74, 0.12), scale=(0.2, 0.08), text_size=0.75)
high = Button(model="quad", text="High Density", color=color.gray, position=(-0.74, 0.03), scale=(0.2, 0.08), text_size=0.75)
commercial = Button(model="quad", text = "Commercial", color=color.gray, position=(-0.74, -0.06), scale=(0.2, 0.08), text_size=0.75)
industrial = Button(model="quad", text = "Industrial", color=color.gray, position=(-0.74, -0.15), scale=(0.2, 0.08), text_size=0.75)
power = Button(model="quad", text = "Power Plant", color=color.gray, position=(-0.74, -0.24), scale=(0.2, 0.08), text_size=0.75)

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

orthogonal = Button(
    model='quad',
    text="Go 3D",
    color=color.gray,
    scale=(0.25, 0.1),
    position=(0.745, 0.20),
    on_click=toggle_orthographic
)

simulate_button = Button(
    model='quad',
    text="Simulate Day",
    color=color.gray,
    scale=(0.25, 0.1),
    position=(0.745, -0.19),
    on_click=simulate_queue
)

analyze_button = Button(
    model='quad',
    text= "Generate Lines",
    color=color.gray,
    scale=(0.25, 0.1),
    position=(0.745, 0.07),
    on_click=analyze_nodes
)

heatmap_button = Button(
    model='quad',
    text="Show Heatmap",
    color=color.gray,
    scale=(0.25, 0.1),
    position=(0.745, -0.06),
    on_click=draw_heatmap
)

parameters_button = Button(
    model='quad',
    text="Show Parameters",
    color=color.hex("696fff"),
    scale=(0.25, 0.1),
    position=(-0.74, -0.37),
    on_click=enable_wp
)

clear_all = Button(
    model='quad',
    text="CLEAR ALL",
    color=color.hex("cf142b"),
    scale=(0.2, 0.07),
    position=(0.745, -0.43),
    on_click=clear
)

sandbox = Button(
    model='quad',
    text="Sandbox",
    color=color.hex("696fff"),
    scale=(0.2, 0.07),
    position=(-0.3, 0.45),
    on_click=enable_sandbox_interface,
    z = -100
)

data = Button(
    model='quad',
    text="Data Analytics",
    color=color.hex("696fff"),
    scale=(0.2, 0.07),
    position=(0.3, 0.45),
    z = -100,
    on_click=enable_analysis_interface
)

bar = Entity(
    parent=camera.ui,
    model='quad',
    color=color.hex("d3d3d3"),
    scale=(0.3, 1),
    position=(-.74, 0),
    z = 3
)

bar1 = Entity(
    parent=camera.ui,
    model='quad',
    color=color.hex("d3d3d3"),
    scale=(0.3, 1),
    position=(.74, 0),
    z = 3
)

toolbar = Entity(
    parent=camera.ui,
    model='quad',
    color=color.hex("d3d3d3"),
    scale=(2, 0.1),
    position=(0, 0.45),
    z = 2
)

shadow = Entity(
    parent=camera.ui,
    model='quad',
    color=color.hex("555555"),
    scale=(2, 0.1),
    position=(0, 0.446),
    z = 3
)

logo = Entity(
    parent=camera.ui,
    model='quad',             # Flat 2D surface
    texture='folder/logo.png', # Path to the PNG image
    scale=(0.35, 0.05),             # Adjust width and height
    position=(-0.70, 0.45),
    z = -200# Position in the scene
)

analysis_screen = Entity(
    parent=camera.ui,
    model='quad',
    color=color.hex("d3d3d3"),
    scale=(3, 3),
    position=(0, 0),
    z = -50,
    collider = None,
    visible = False,
)

# Create individual elements first
low_density_slider = ThinSlider(1, 100, default=80, step=1, dynamic= True, on_value_changed = update_params)
medium_density_slider = ThinSlider(1, 20, default=10, step=1, dynamic= True, on_value_changed = update_params)
high_density_slider = ThinSlider(1, 15, default=3, step=1, dynamic= True, on_value_changed = update_params)
commercial_slider = ThinSlider(1, 10, default=5, step=1, dynamic= True, on_value_changed = update_params)
industrial_slider = ThinSlider(1, 3, default=1, step=1, dynamic= True, on_value_changed = update_params)

# Now define the window panel
wp = WindowPanel(
    title='Set Zoning Density',
    content=(
        Text("Households per Low Density Zone"),
        low_density_slider,
        Text("Apartments per Medium Density Zone"),
        medium_density_slider,
        Text("High rises per High Density Zone"),
        high_density_slider,
        Text("Shops per Commercial Zone"),
        commercial_slider,
        Text("Factories per Industrial Zone"),
        industrial_slider
    ),
    popup=True
)
wp.y = wp.panel.scale_y / 2 * wp.scale_y    # center the window panel
wp.layout()

# Instructions for the user
grid = Entity(model=Grid(20, 20), scale=(10, 10, 1), color=color.light_gray, collider = 'box', position=(grid_shift_x, grid_shift_y, 0), receive_shadows = True)

# Run the app
update_params()
app.run()
