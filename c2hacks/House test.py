from ursina import *

app = Ursina()

cube = Entity(
        model = 'folder/industrial.obj', double_sided = True,scale =1)


app.run()