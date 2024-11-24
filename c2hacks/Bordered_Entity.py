from ursina import *

app = Ursina()

class Bordered_Entity:
        def __init__(self, model, color, position, collider, scale, border_thickness=0.05, border_color=color.black):
                super().__init__()
                # Border
                self.border = Entity(
                        parent=self,
                        model='quad',
                        scale=(scale[0] + border_thickness, scale[1] + border_thickness),
                        color=border_color,
                        z=0.01  # Ensures border is rendered behind the entity
                )

                self.main = Entity(
                        model='cube',
                        color=color,
                        position=position,
                        collider=collider,  # Add a box collider for detecting mouse hover
                        scale=scale
                )
