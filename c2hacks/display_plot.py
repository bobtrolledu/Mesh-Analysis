from ursina import *
import matplotlib.pyplot as plt
from PIL import Image
from io import BytesIO

def create_matplotlib_texture():
    # Generate a Matplotlib plot
    fig, ax = plt.subplots()
    x = [1, 2, 3, 4, 5]
    y = [2, 3, 5, 7, 11]
    ax.plot(x, y, label='Example Data')
    ax.set_title("Matplotlib in Ursina")
    ax.legend()

    # Save the plot to an in-memory buffer
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)

    # Convert thez image to a texture
    img = Image.open(buf)
    texture = Texture(img)
    buf.close()
    return texture

app = Ursina()

# Create a texture from the Matplotlib plot
plot_texture = create_matplotlib_texture()

# Display the texture in Ursina
plot_entity = Entity(
    model='quad',
    texture=plot_texture,
    scale=(6, 4),  # Adjust scale as needed
    position=(0, 0, 0)  # Centered
)

app.run()
