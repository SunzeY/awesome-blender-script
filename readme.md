# Awesome Blender Script [![Awesome](https://awesome.re/badge.svg)](https://awesome.re)
This repo is a collection of code (or link) for awesome blender script for 3D content creation.

#### convert_to_std_obj.py
Many edge-cutting 3D object generation projects only support export `.obj` with **color on vertex**, which may be not compatible for other application.
[convert_to_std_obj.py](convert_to_std_obj.py) can convert this type of `.obj` and export standard `.mtl` and `.png` texture file with `smart uv project` in blender.
this script has been tested on model generated from [TripoSR](https://github.com/VAST-AI-Research/TripoSR), [ThreeStudio](https://github.com/threestudio-project/threestudio) and [OpenLRM](https://github.com/3DTopia/OpenLRM).



#### [blender_script.py](https://github.com/openai/point-e/blob/main/point_e/evals/scripts/blender_script.py)
Created by OpenAI for rendering cricle orbit camera view around centric object.
