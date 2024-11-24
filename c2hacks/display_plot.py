from ursina import *
import matplotlib.pyplot as plt
from PIL import Image
from io import BytesIO

total_textures = []

def create_matplotlib_texture(xvar, yvar, label):
    # Generate a Matplotlib plot
    fig, ax = plt.subplots()

    ax.plot(xvar, yvar)
    ax.set_title(label)
    ax.legend()

    # Save the plot to an in-memory buffer
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)

    # Convert thez image to a texture
    img = Image.open(buf)
    texture = Texture(img)
    buf.close()

    total_textures.append(texture)

def create_simple_texture(buffer):
    img = Image.open(buffer)
    texture = Texture(img)
    buffer.close()
    total_textures.append(texture)

def add_plot(plot):
    total_textures.append(plot)

def display():
    return total_textures

