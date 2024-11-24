from ursina import *

if __name__ == '__main__':
    app = Ursina()


    def input(key):

        if key == 'left mouse down':  # Add a new entity on left mouse click
            t = time.time()
            print(t)
    app.run()
