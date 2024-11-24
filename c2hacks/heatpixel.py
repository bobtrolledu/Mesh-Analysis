from ursina import *

class heatpixel(Entity):
    value = 0

    def __init__(self, model, color, position, scale, value):
        super().__init__()
        self.model = model
        self.color = color
        self.position = position
        self.scale = scale
        self.value = value

    def get_intensity(self):
        return self.value

