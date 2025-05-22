import bpy
import math

def limpar_cena():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

def criar_objeto_pai(nome, localizacao_global):
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=localizacao_global)
    pai = bpy.context.object
    pai.name = nome
    return pai

def definir_pai(objeto, pai):
    if objeto and pai:
        objeto.parent = pai
        objeto.matrix_parent_inverse = pai.matrix_world.inverted()

def criar_mesa_de_sinuca():
    # Parâmetros principais
    mesa_largura = 2.0
    mesa_comprimento = 4.0
    mesa_altura_total = 1
    mesa_espessura = 0.05
    borda_altura = 0.1
    borda_espessura = 0.25
    base_espessura = 0.3
    base_scale_reduction = 1.10
    cacapa_raio = 0.1
    bola_raio = 0.057
    perna_raio = 0.12
    afastamento_y = 0.1 

    # Tampo da mesa
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, mesa_altura_total - mesa_espessura / 2))
    mesa = bpy.context.object
    mesa.scale = (mesa_comprimento, mesa_largura, mesa_espessura)
    mesa.name = "Mesa_Base"
    mat_mesa = bpy.data.materials.new(name="Material_Mesa")
    mat_mesa.diffuse_color = (0.0, 0.3, 0.0, 1.0)
    mesa.data.materials.append(mat_mesa)

    # Moldura
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, mesa_altura_total))
    borda = bpy.context.object
    borda.name = "Borda"
    borda.scale = (mesa_comprimento + 2 * borda_espessura, mesa_largura + 2 * borda_espessura, borda_altura)
    mat_borda = bpy.data.materials.new(name="Material_Borda")
    mat_borda.diffuse_color = (0.4, 0.2, 0.0, 1.0)
    borda.data.materials.append(mat_borda)
    
    # Recorte do centro
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, mesa_altura_total))
    corte = bpy.context.object
    corte.scale = (mesa_comprimento, mesa_largura, borda_altura + 0.01)
    mod = borda.modifiers.new(name="Boolean", type="BOOLEAN")
    mod.operation = 'DIFFERENCE'
    mod.object = corte
    bpy.context.view_layer.objects.active = borda
    bpy.ops.object.modifier_apply(modifier="Boolean")
    bpy.data.objects.remove(corte)

    # Base
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, mesa_altura_total - mesa_espessura - base_espessura / 2))
    base = bpy.context.object
    base.scale = (4.20099, mesa_largura * base_scale_reduction, base_espessura)
    base.name = "Base_Mesa"
    mat_base = bpy.data.materials.new(name="Material_Base")
    mat_base.diffuse_color = (0.2, 0.1, 0.0, 1.0)
    base.data.materials.append(mat_base)

    # Caçapas
    posicoes_cacapas = [
        (mesa_comprimento / 2, mesa_largura / 2, mesa_altura_total),
        (-mesa_comprimento / 2, mesa_largura / 2, mesa_altura_total),
        (mesa_comprimento / 2, -mesa_largura / 2, mesa_altura_total),
        (-mesa_comprimento / 2, -mesa_largura / 2, mesa_altura_total),
        (0, mesa_largura / 2, mesa_altura_total),
        (0, -mesa_largura / 2, mesa_altura_total),
    ]
    cacapas = []
    # Aplicar escala do tampo antes da booleana para evitar problemas
    bpy.context.view_layer.objects.active = mesa
    bpy.ops.object.transform_apply(scale=True)
    for i, pos in enumerate(posicoes_cacapas):
        # O cilindro atravessa totalmente o tampo
        bpy.ops.mesh.primitive_cylinder_add(
            radius=cacapa_raio,
            depth=mesa_espessura + 0.05,  # Garante que atravessa o tampo
            location=(pos[0], pos[1], mesa_altura_total)
        )
        cacapa = bpy.context.object
        cacapa.name = f"Cacapa_{i}"
       
        # Boolean para a borda
        mod_borda = borda.modifiers.new(name=f"Boolean_Cacapa_Borda_{i}", type="BOOLEAN")
        mod_borda.operation = 'DIFFERENCE'
        mod_borda.object = cacapa
        bpy.context.view_layer.objects.active = borda
        bpy.ops.object.modifier_apply(modifier=f"Boolean_Cacapa_Borda_{i}")
       
        # Boolean para o tampo
        mod_mesa = mesa.modifiers.new(name=f"Boolean_Cacapa_Mesa_{i}", type="BOOLEAN")
        mod_mesa.operation = 'DIFFERENCE'
        mod_mesa.object = cacapa
        bpy.context.view_layer.objects.active = mesa
        bpy.ops.object.modifier_apply(modifier=f"Boolean_Cacapa_Mesa_{i}")
        bpy.data.objects.remove(cacapa)
        cacapas.append(cacapa)

    # Bolas
    bolas = []
    for i in range(5):
        for j in range(i + 1):
            x = i * bola_raio * 2.0
            y = (j - i / 2) * bola_raio * 2.0
            z = mesa_altura_total + bola_raio
            
            # Adicionando as bolas coloridas
            bpy.ops.mesh.primitive_uv_sphere_add(radius=bola_raio, location=(x - 0.5, y, z))
            bola = bpy.context.object
            bola.name = f"Bola_{i}_{j}"
            mat_bola = bpy.data.materials.new(name=f"Material_Bola_{i}_{j}")
            mat_bola.diffuse_color = (i / 5.0, j / 5.0, 1.0 - i / 5.0, 1.0)
            bola.data.materials.append(mat_bola)
            bolas.append(bola)

    # Adicionando a bola branca        
    bpy.ops.mesh.primitive_uv_sphere_add(radius=bola_raio, location=(-1.5, 0, mesa_altura_total + bola_raio))
    bola_branca = bpy.context.object
    bola_branca.name = "Bola_Branca"
    mat_branca = bpy.data.materials.new(name="Material_Bola_Branca")
    mat_branca.diffuse_color = (1.0, 1.0, 1.0, 1.0)
    bola_branca.data.materials.append(mat_branca)
    bolas.append(bola_branca)

    # Suportes
    perna_altura = mesa_altura_total - mesa_espessura - base_espessura
    posicoes_pernas = [
        (mesa_comprimento / 2 - 0.2, mesa_largura / 2 - afastamento_y, perna_altura / 2),
        (-mesa_comprimento / 2 + 0.2, mesa_largura / 2 - afastamento_y, perna_altura / 2),
        (mesa_comprimento / 2 - 0.2, -mesa_largura / 2 + afastamento_y, perna_altura / 2),
        (-mesa_comprimento / 2 + 0.2, -mesa_largura / 2 + afastamento_y, perna_altura / 2),
    ]
    pernas = []
    for i, pos in enumerate(posicoes_pernas):
        bpy.ops.mesh.primitive_cylinder_add(radius=perna_raio, depth=perna_altura, location=pos)
        perna = bpy.context.object
        perna.name = f"Perna_{i}"
        mat_perna = bpy.data.materials.new(name="Material_Perna")
        mat_perna.diffuse_color = (0.2, 0.1, 0.0, 1.0)
        perna.data.materials.append(mat_perna)
        pernas.append(perna)

    # Adicionando Parentesco 
    empty = criar_objeto_pai("MesaSinuca_Raiz", (0, 0, 0))
    definir_pai(mesa, empty)
    definir_pai(borda, empty)
    definir_pai(base, empty)
    for obj in bolas:
        definir_pai(obj, empty)
    for obj in pernas:
        definir_pai(obj, empty)
    # Caçapas não precisam ser parented pois são removidas após boolean

limpar_cena()
criar_mesa_de_sinuca()

