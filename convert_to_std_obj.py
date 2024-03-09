
'''
Written by Zeyi Sun @3/9 2024

Script to run within Blender to convert color on vertex .obj into standard .obj with unwrapped uv and .png texture file:
1. unwrap uv with smart uv projection
2. bake image texture and dump to .png texture_diffuse only

Example usage
blender-3.4.1-linux-x64/blender -b -P convert_to_std_obj.py -- --input_path output/chair/0/mesh.obj --output_path converted/chair
'''

import os
import sys
import bpy
import argparse
try:
    dash_index = sys.argv.index("--")
except ValueError as exc:
    raise ValueError("arguments must be preceded by '--'") from exc

raw_args = sys.argv[dash_index + 1 :]
parser = argparse.ArgumentParser()
parser.add_argument("--input_path", required=True, type=str)
parser.add_argument("--output_path", required=True, type=str)
args = parser.parse_args(raw_args)

def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()
    
clear_scene()

# bpy.data.scenes['Scene'].render.engine = 'CYCLES'
# world = bpy.data.worlds['World']
# world.use_nodes = True

bpy.ops.wm.obj_import(filepath=args.input_path, directory=os.path.split(args.input_path)[0], files=[{"name": os.path.split(args.input_path)[1]}])
bpy.context.object.rotation_euler[0] = 0
obj = bpy.context.active_object

# add uv map
bpy.ops.object.editmode_toggle()
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.smart_project()
bpy.ops.object.editmode_toggle()

# vertex color material
mat = bpy.data.materials.new(name="VertexColor")
mat.use_nodes = True
vc = mat.node_tree.nodes.new('ShaderNodeVertexColor')
vc.name = "vc_node"
vc.layer_name = "Color"
bsdf = mat.node_tree.nodes["Principled BSDF"]
mat.node_tree.links.new(vc.outputs[0], bsdf.inputs[0])
obj.data.materials.append(mat)

# bake
image_name = obj.name + '_BakedTexture'
img = bpy.data.images.new(image_name, 1024, 1024)

bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.bake_type = 'DIFFUSE'
bpy.context.scene.render.bake.use_pass_indirect = False
bpy.context.scene.render.bake.use_pass_direct = False
bpy.context.scene.render.bake.use_selected_to_active = False
#bpy.context.scene.render.bake.cage_extrusion = 0.1

image_name = obj.name + '_BakedTexture'
img = bpy.data.images.new(image_name, 1024, 1024)

for mat in obj.data.materials:

    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    texture_node =nodes.new('ShaderNodeTexImage')
    texture_node.name = 'Bake_node'
    texture_node.select = True
    nodes.active = texture_node
    texture_node.image = img
    
bpy.context.view_layer.objects.active = obj
bpy.ops.object.bake(type='DIFFUSE', save_mode='EXTERNAL')

# remove original color on vertex node.
for mat in obj.data.materials:
    vc = mat.node_tree.nodes['vc_node']
    mat.node_tree.nodes.remove(vc)

os.makedirs(args.output_path, exist_ok=True)

img.save_render(filepath=f'{args.output_path}/texture_kd.png')
bpy.ops.export_scene.obj(filepath=f"{args.output_path}/mesh.obj")

with open(f'{args.output_path}/mesh.mtl', 'a') as f:
    f.write('map_Kd texture_kd.png')
