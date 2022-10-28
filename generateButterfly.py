from bpy import context, data, ops
import bpy

# Cache shortcuts to start and end of scene.
scene = context.scene
frame_start = scene.frame_start
frame_end = scene.frame_end

# Create cube.
# ops.mesh.primitive_cube_add(radius=1.0, location=(0.0, 0.0, 0.0))
# cube = context.active_object

# Create Butterfly
butterfly = bpy.data.objects['Butterfly'] # mesh data input
creation = bpy.data.objects.new('Butterfly.001',butterfly.data) #instance

# add instance to scene
bpy.context.collection.objects.link(creation)
#bpy.context.collection.update() #add to the scene

#copy modifiers
butterfly.select_set(True, view_layer=scene.view_layers[0])
bpy.context.view_layer.objects.active = butterfly
creation.select_set(True, view_layer=scene.view_layers[0])
bpy.ops.object.make_links_data(type='MODIFIERS')
bpy.ops.object.select_all(action='DESELECT')


#location list from hand track program, passing along[TODO]
# handPath = []
handPath = [(332, 500, 0), (555, 395, 0), (512, 252, 0), (303, 188, 0), (245, 192, 0), (384, 189, 0), (461, 259, 0), (418, 468, 0), (560, 357, 0), (536, 214, 0), (488, 248, 0)]

# Loop through locations list.
pathLen = len(handPath)
i_to_percent = 1.0 / (pathLen - 1)
i_range = range(0, pathLen, 1)
for i in i_range:
    # Convert place in locations list to appropriate frame.
    i_percent = i * i_to_percent
    key_frame = int(frame_start * (1.0 - i_percent) + frame_end * i_percent)
    scene.frame_set(key_frame)

    # Update location for that frame.
    butterfly.location = handPath[i]
    butterfly.keyframe_insert(data_path='location')

# Cache shortcut to f-curves.
fcurves = butterfly.animation_data.action.fcurves
for fcurve in fcurves:
    for key_frame in fcurve.keyframe_points:

        # Set interpolation and easing type.
        key_frame.interpolation = 'LINEAR'
        key_frame.easing = 'AUTO'

        # Options: ['FREE', 'VECTOR', 'ALIGNED', 'AUTO', 'AUTO_CLAMPED']
        key_frame.handle_left_type = 'AUTO'
        key_frame.handle_right_type = 'AUTO'


# Return to starting frame.
scene.frame_set(frame_start)