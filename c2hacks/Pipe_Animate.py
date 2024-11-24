from ursina import *

class Pipe_Animate:
    # Initial path for the Pipe
    initial_path = []  # Start with two points for the initial Pipe
    full_path = []

    def __init__(self, initial, final):
        self.initial_path = initial
        self.full_path = final
        self.pipe_entity = Entity(model=Pipe(path=initial, cap_ends=False, thicknesses=((0.1,0.1),)))

    # Full path the Pipe will grow into

    # Function to animate the Pipe
    def update_pipe(self):
        if len(self.pipe_entity.model.path) < len(self.full_path):  # If the Pipe is not fully drawn
            next_point = self.full_path[len(self.pipe_entity.model.path)]  # Get the next point
            self.pipe_entity.model.path.append(next_point)  # Add it to the Pipe's path
            self.pipe_entity.model.generate()  # Regenerate the Pipe model to reflect changes

    # Schedule the animation using `invoke`
    def animate_pipe(self):
        for i in range(1, len(self.full_path)):
            invoke(self.update_pipe, delay=i * 0.1)  # Add a delay for each point

    def get_pipe(self):
        return self.pipe_entity
