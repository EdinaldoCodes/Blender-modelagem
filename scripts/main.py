import bpy
import sys
import os
import math
# Importação dos scripts e funções
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scripts'))
from script import criar_mesa_branca, criar_camera, limpar_cena, aplicar_material,hex_to_rgba, obter_caminho_absoluto
from script2 import criar_mesa_classica
from script3 import criar_mesa_escura


def criar_chao():
    bpy.ops.mesh.primitive_plane_add(
        size=15.0,
        enter_editmode=False,
        align='WORLD',
        location=(0, 0, 0),
        scale=(1, 1, 1)
    )
    chao = bpy.context.object
    chao.name = "Chao_Plano"
    
    # Adicionar material ao chao
    aplicar_material(chao, cor_base=hex_to_rgba("#929292"))

def adicionar_luz():
    # Define as cores em HEX para cada luz
    cor_luz_grande = hex_to_rgba("#ECFEFFFF", include_alpha=False)
    cor_luz_grande2  = hex_to_rgba("#ECFEFFFF", include_alpha=False)
    cor_luz_pequena = hex_to_rgba("#B3B2FF", include_alpha=False)

    # Luz grande (quente)
    bpy.ops.object.light_add(type='AREA', location=(0, 0, 2))
    area_light_grande = bpy.context.object
    area_light_grande.data.energy = 144
    area_light_grande.data.size = 9.33
    area_light_grande.data.color = cor_luz_grande

    # Luz grande 2 (quente)
    bpy.ops.object.light_add(type='AREA', location=(0, -4, 2))
    area_light_grande = bpy.context.object
    area_light_grande.data.energy = 144
    area_light_grande.data.size = 9.33
    area_light_grande.data.color = cor_luz_grande

    # Luz grande 3 (quente)
    bpy.ops.object.light_add(type='AREA', location=(0, 4, 2))
    area_light_grande = bpy.context.object
    area_light_grande.data.energy = 144
    area_light_grande.data.size = 9.33
    area_light_grande.data.color = cor_luz_grande

def criar_camera():
    # Adiciona a câmera de cima
    bpy.ops.object.camera_add(location=(0, 0, 10), rotation=(0, 0, 0))
    camera_top = bpy.context.object
    camera_top.name = "Camera_Top"
    camera_top.rotation_euler = (math.radians(-2.20389), 0, 0)
    bpy.context.view_layer.update()

    # Adiciona a câmera de topo com nova localização
    bpy.ops.object.camera_add(location=(-12.932, 0.063, 11.079))
    camera_top2 = bpy.context.object
    camera_top2.name = "Camera_Top2"
    camera_top2.rotation_euler = (math.radians(50.720), math.radians(0.000), math.radians(-90.340))
    bpy.context.view_layer.update()
    
    # Adiciona a câmera de canto
    bpy.ops.object.camera_add(location=(5.276, 11.570,4.480))
    camera_canto = bpy.context.object
    camera_canto.name = "Camera_Canto"
    camera_canto.rotation_euler = (math.radians(71.323), -0, math.radians(150.339))
    bpy.context.view_layer.update()

if __name__ == "__main__":
    limpar_cena()
    criar_chao()
    criar_mesa_classica(location=(0, 4, 0))
    criar_mesa_escura(location=(0, 0, 0))
    criar_mesa_branca(location=(0, -4, 0))
    criar_camera()
    adicionar_luz()

    