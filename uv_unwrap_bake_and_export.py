import os
import sys
import bpy
import argparse

def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()

def import_obj(filepath):
    bpy.ops.import_scene.obj(filepath=filepath)
    return bpy.context.selected_objects[0]

def setup_uv(obj, method):
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')

    if method == 'smart':
        bpy.ops.uv.smart_project()
    elif method == 'lightmap':
        bpy.ops.uv.lightmap_pack()
    elif method == 'unwrap':
        bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0.001)
    elif method == 'cubic':
        bpy.ops.uv.cube_project()
    elif method == 'cylinder':
        bpy.ops.uv.cylinder_project()
    elif method == 'sphere':
        bpy.ops.uv.sphere_project()
    
    bpy.ops.object.mode_set(mode='OBJECT')

def setup_material_nodes(obj, img, uv_map_name):
    bpy.context.view_layer.objects.active = obj
    for mat in obj.data.materials:
        mat.use_nodes = True
        nodes = mat.node_tree.nodes

        # Create and set up the UV Map node for new UV
        new_uv_map_node = nodes.new('ShaderNodeUVMap')
        new_uv_map_node.uv_map = uv_map_name

        # Create and set up the Image Texture node for new image
        new_texture_node = nodes.new('ShaderNodeTexImage')
        new_texture_node.image = img
        new_texture_node.name = 'Bake_texture_node'

        # Link new UV Map node to the new Image Texture node
        mat.node_tree.links.new(new_uv_map_node.outputs['UV'], new_texture_node.inputs['Vector'])

def bake_texture(obj, output_path, method):
    image_name = f"{method}_texture"
    img = bpy.data.images.new(image_name, width=1024, height=1024)

    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.bake_type = 'DIFFUSE'
    bpy.context.scene.render.bake.use_pass_indirect = False
    bpy.context.scene.render.bake.use_pass_direct = False
    bpy.context.scene.render.bake.use_selected_to_active = False
    bpy.context.scene.render.bake.target = 'IMAGE_TEXTURES'

    # Duplicate the UV map and rename it
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='OBJECT')
    new_uv_map = obj.data.uv_layers.new(name=f"UVMap_{method}")
    new_uv_map.active = True

    # Setup the new UV mapping
    setup_uv(obj, method)

    # Setup material nodes
    setup_material_nodes(obj, img, new_uv_map.name)

    bpy.context.view_layer.objects.active = obj

    # Select the new image texture node for baking
    for mat in obj.data.materials:
        mat.node_tree.nodes.active = mat.node_tree.nodes['Bake_texture_node']

    bpy.ops.object.bake(type='DIFFUSE')
    
    texture_filepath = os.path.join(output_path, f"{image_name}.png")
    img.save_render(filepath=texture_filepath)
    return texture_filepath

def export_obj(obj, output_path, method, texture_path):
    filename = f"{method}_uv_{obj.name}.obj"
    output_filepath = os.path.join(output_path, filename)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.export_scene.obj(filepath=output_filepath)
    
    # Update .mtl file to link texture
    mtl_filepath = os.path.splitext(output_filepath)[0] + '.mtl'
    with open(mtl_filepath, 'a') as f:
        f.write(f'\nmap_Kd {os.path.basename(texture_path)}')

def activate_uv_map(obj, uv_map_name):
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='OBJECT')
    uv_layers = obj.data.uv_layers
    uv_layers.active = uv_layers.get(uv_map_name)

def main():
    try:
        dash_index = sys.argv.index("--")
    except ValueError as exc:
        raise ValueError("arguments must be preceded by '--'") from exc
    raw_args = sys.argv[dash_index + 1:]
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_path", required=True, type=str, help="Path to input .obj file")
    parser.add_argument("--output_path", required=True, type=str, help="Directory to save the output .obj files and textures")
    args = parser.parse_args(raw_args)
    methods = ['smart', 'lightmap', 'unwrap', 'cubic', 'cylinder', 'sphere']
    for method in methods:
        clear_scene()
        obj = import_obj(args.input_path)
        texture_path = bake_texture(obj, args.output_path, method)
        activate_uv_map(obj, f"UVMap_{method}")
        export_obj(obj, args.output_path, method, texture_path)
    
        print("UV mapping, texture baking, and export completed for all methods.")

if __name__ == "__main__":
    main()
