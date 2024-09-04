from random import random
import bpy
from math import pi

N_PLANETS = 7
START_FRAME = 1
END_FRAME = 360


def find_3dview_space():
    # find the 3D view panel and its screen space
    area = None
    for a in bpy.data.window_managers[0].windows[0].screen.areas:
        if a.type == "VIEW_3D":
            area = a
            break
    return area.spaces[0] if area else bpy.context.space_data

def setup_scene():
    # (set a black background)
    bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[0].default_value = (0, 0, 0, 1)
    # (make sure we use the EEVEE render engine + enable bloom effect)
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.eevee.use_bloom = True
    # (set the animation start/end/current frames)
    scene.frame_start = START_FRAME
    scene.frame_end = END_FRAME
    scene.frame_current = START_FRAME
    # get the current 3D view (among all visible windows
    # in the workspace)
    space = find_3dview_space()
    # apply a "rendered" shading mode + hide all
    # additional markers, grids, cursors...
    space.shading.type = 'RENDERED'
    space.overlay.show_floor = False
    space.overlay.show_axis_x = False
    space.overlay.show_axis_y = False
    space.overlay.show_cursor = False
    space.overlay.show_object_origins = False




# Function for creating a single planet
def create_sphere(radius, distance_to_sun, obj_name):
    # instantiate a UV sphere with a given
    # radius, at a given distance from the
    # world origin point
    obj = bpy.ops.mesh.primitive_uv_sphere_add(
        radius=radius,
        location=(distance_to_sun, 0, 0),
        scale=(1, 1, 1)
    ) 
    # rename the object
    bpy.context.object.name = obj_name
    # apply smooth shading
    bpy.ops.object.shade_smooth()
    # return the object reference
    return bpy.context.object

# Function for creating a single star in position
def create_sphere_at_pos(radius, x, y, z, obj_name):
    # instantiate a UV sphere with a given
    # radius, at a given distance from the
    # world origin point
    obj = bpy.ops.mesh.primitive_uv_sphere_add(
        radius=radius,
        location=(x,y,z),
        scale=(1, 1, 1)
    ) 
    # rename the object
    bpy.context.object.name = obj_name
    # apply smooth shading
    bpy.ops.object.shade_smooth()
    # return the object reference
    return bpy.context.object

# Function for creating the rotation axis of a single planet 
def create_torus(radius, obj_name):
    # (same as the create_sphere method)
    obj = bpy.ops.mesh.primitive_torus_add(
        location=(0, 0, 0),
        major_radius=radius,
        minor_radius=0.1,
        major_segments=60
    )
    bpy.context.object.name = obj_name
     # apply smooth shading
    bpy.ops.object.shade_smooth()
    return bpy.context.object

# Function for the emission shader
def create_emission_shader(color, strength, mat_name):
    # create a new material resource (with its associated shader)
    mat = bpy.data.materials.new(mat_name)
    # enable the node-graph edition mode
    mat.use_nodes = True
    
    # clear all starter nodes
    nodes = mat.node_tree.nodes
    nodes.clear()

    # add the Emission node
    node_emission = nodes.new(type="ShaderNodeEmission")
    # (input[0] is the color)
    node_emission.inputs[0].default_value = color
    # (input[1] is the strength)
    node_emission.inputs[1].default_value = strength
    
    # add the Output node
    node_output = nodes.new(type="ShaderNodeOutputMaterial")
    
    # link the two nodes
    links = mat.node_tree.links
    link = links.new(node_emission.outputs[0], node_output.inputs[0])

    # return the material reference
    return mat

# setup scene settings
setup_scene()

# Removing old objects
# Source: https://blender.stackexchange.com/questions/27234/python-how-to-completely-remove-an-object
objs = [ob for ob in bpy.context.scene.objects if ob.type in ( 'MESH')]
bpy.ops.object.delete({"selected_objects": objs})


# Materials
ring_mat = create_emission_shader(
    (1, 1, 1, 1), 1, "RingMat"
)


# add the sun sphere
sun = create_sphere(12, 0, "Sun")
sun.data.materials.append(
    create_emission_shader(
        (1, 0.66, 0.08, 1), 10, "SunMat"
    )
)

# add other smaller star emissions
# the coordinate values will be hardcoded to fit each background image
star = create_sphere_at_pos(1.5, 103.75, 31.996,0, "Star")
star.data.materials.append(
    create_emission_shader(
        (0.193, 0.658, 1, 1), 100, "StarMat"
    )
)
star2 = create_sphere_at_pos(1, -117.25, -70,0, "Star2")
star2.data.materials.append(
    create_emission_shader(
        (0.193, 0.658, 1, 1), 100, "StarMat2"
    )
)

star2 = create_sphere_at_pos(0.8, -148.19, -42.937, 0, "Star3")
star2.data.materials.append(
    create_emission_shader(
        (0.193, 0.658, 1, 1), 100, "StarMat3"
    )
)

# create the planets
for n in range(N_PLANETS):
    # get a random radius (a float in [1, 5])
    r = 1 + random() * 4
    # get a random distace to the origin point:
    # - an initial offset of 30 to get out of the sun's sphere
    # - a shift depending on the index of the planet
    # - a little "noise" with a random float
    d = 30 + n * 12 + (random() * 4 - 2)
    # instantiate the planet with these parameters and a custom object name
    planet = create_sphere(r, d, "Planet-{:02d}".format(n))
    planet.data.materials.append(
        create_emission_shader(
            (random(), random(), random(), 1),
            2,
            "PlanetMat-{:02d}".format(n)
        )
    )
    
    # create the rotation axis
    ring = create_torus(d, "Radius-{:02d}".format(n))
    ring.data.materials.append(ring_mat)
    
    # set planet as active object
    bpy.context.view_layer.objects.active = planet
    planet.select_set(True)
    # set object origin at world origin
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR", center="MEDIAN")
    
    # setup the planet animation data
    planet.animation_data_create()
    planet.animation_data.action = bpy.data.actions.new(name="RotationAction")
    fcurve = planet.animation_data.action.fcurves.new(
        data_path="rotation_euler", index=2
    )
    k1 = fcurve.keyframe_points.insert(
        frame=START_FRAME,
        value=0
    )
    k1.interpolation = "LINEAR"
    k2 = fcurve.keyframe_points.insert(
        frame=END_FRAME,
        value=(2 + random() * 2) * pi
    )
    k2.interpolation = "LINEAR"


#add keyframes for emission animations on Stars
# get the material
mat = bpy.data.objects["Star"].active_material
# get the nodes
nodes = mat.node_tree.nodes
# get some specific node:
# returns None if the node does not exist
emission = nodes.get("Emission")

for i in range(8): 
    if i%2==0:
        emission.inputs[1].default_value = 800
    else:
        emission.inputs[1].default_value = 10
    # add keyframe to strength at frame 1
    emission.inputs[1].keyframe_insert("default_value", frame=i*90)

mat = bpy.data.objects["Star2"].active_material
# get the nodes
nodes = mat.node_tree.nodes
# get some specific node:
# returns None if the node does not exist
emission = nodes.get("Emission")
for i in range(16): 
    if i%2==0:
        emission.inputs[1].default_value = 50
    else:
        emission.inputs[1].default_value = 500
    # add keyframe to strength at frame 1
    emission.inputs[1].keyframe_insert("default_value", frame=i*45)
    
mat = bpy.data.objects["Star3"].active_material
# get the nodes
nodes = mat.node_tree.nodes
# get some specific node:
# returns None if the node does not exist
emission = nodes.get("Emission")
for i in range(24): 
    if i%2==0:
        emission.inputs[1].default_value = 10
    else:
        emission.inputs[1].default_value = 400
    # add keyframe to strength at frame 1
    emission.inputs[1].keyframe_insert("default_value", frame=i*30)