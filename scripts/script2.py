import bpy
import math
import os

def limpar_cena():
    # Garante que está no modo de objeto antes de selecionar e deletar
    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    # limpa materiais nao utilizados 
    for material in bpy.data.materials:
        if not material.users:
            bpy.data.materials.remove(material)
    for mesh in bpy.data.meshes:
        if not mesh.users:
            bpy.data.meshes.remove(mesh)
    for collection in bpy.data.collections:  # Limpa colecoes vazias 
        if not collection.objects and not collection.children:
            pass
    for image in bpy.data.images:
        if not image.users: # Remove imagens nao utilizadas
            bpy.data.images.remove(image)
    for texture in bpy.data.textures:
        if not texture.users: # Remove texturas nao utilizadas
            bpy.data.textures.remove(texture)

def criar_objeto_pai(nome, localizacao_global):
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=localizacao_global)
    pai = bpy.context.object
    pai.name = nome
    return pai

def definir_pai(objeto, pai):
    if objeto and pai:
        objeto.parent = pai
        objeto.matrix_parent_inverse = pai.matrix_world.inverted()

def obter_caminho_absoluto(rel_path):
    # Retorna o caminho absoluto a partir do diretório do script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, rel_path)

def carregar_textura_imagem(caminho_textura, colorspace='sRGB'):
    if not os.path.exists(caminho_textura):
        print(f'Arquivo {caminho_textura} não encontrado!')
        return None
    image = bpy.data.images.load(caminho_textura)
    image.colorspace_settings.name = colorspace
    return image

def criar_material_base(nome):
    # Cria material base com nós principais
    material = bpy.data.materials.new(name=nome)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    output = nodes.new('ShaderNodeOutputMaterial')
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    return material, bsdf

def aplicar_material(objeto, texturas=None, cor_base=None, rugosidade=1):
    # Aplica um material ao objeto - configuração básica
    material, bsdf = criar_material_base(f"Material_{objeto.name}")

    if texturas:
        for input_name, (caminho, colorspace) in texturas.items():
            tex_image = carregar_textura_imagem(caminho, colorspace)
            if tex_image:
                tex_node = material.node_tree.nodes.new('ShaderNodeTexImage')
                tex_node.image = tex_image
                if input_name == 'Normal':
                    normal_map = material.node_tree.nodes.new('ShaderNodeNormalMap')
                    material.node_tree.links.new(tex_node.outputs['Color'], normal_map.inputs['Color'])
                    material.node_tree.links.new(normal_map.outputs['Normal'], bsdf.inputs['Normal'])
                else:
                    material.node_tree.links.new(tex_node.outputs['Color'], bsdf.inputs[input_name])

    # Configurações padrão
    if cor_base is not None:
        bsdf.inputs['Base Color'].default_value = cor_base
    if rugosidade is not None:
        bsdf.inputs['Roughness'].default_value = rugosidade

    # Aplicar material ao objeto
    objeto.data.materials.clear()
    objeto.data.materials.append(material)

def aplicar_material_feltro(objeto, texturas, rugosidade=1, deslocamento_escala=0.050, mapping_scale=0.100):
    # Aplica material específico para o feltro com texturas completas
    material, bsdf = criar_material_base(f"Material_Feltro_{objeto.name}")

    # Cria as arvore de nodes e links
    nodes = material.node_tree.nodes
    links = material.node_tree.links

    tex_coord = nodes.new('ShaderNodeTexCoord')
    mapping = nodes.new('ShaderNodeMapping')
    mapping.vector_type = 'TEXTURE'
    
    value_node = nodes.new('ShaderNodeValue')
    value_node.outputs[0].default_value = mapping_scale
    
    links.new(value_node.outputs['Value'], mapping.inputs['Scale'])
    links.new(tex_coord.outputs['UV'], mapping.inputs['Vector'])

    for input_name, (caminho, colorspace) in texturas.items():
        tex_image = carregar_textura_imagem(caminho, colorspace)
        
        if not tex_image:
            continue
        
        tex_node = nodes.new('ShaderNodeTexImage')
        tex_node.image = tex_image
        links.new(mapping.outputs['Vector'], tex_node.inputs['Vector'])

        if input_name == 'Base Color':
            links.new(tex_node.outputs['Color'], bsdf.inputs['Base Color'])
        
        elif input_name == 'Normal':
            normal_map = nodes.new('ShaderNodeNormalMap')
            normal_map.inputs['Strength'].default_value = 1.000
            links.new(tex_node.outputs['Color'], normal_map.inputs['Color'])
            links.new(normal_map.outputs['Normal'], bsdf.inputs['Normal'])
        
        elif input_name == 'Roughness':
            links.new(tex_node.outputs['Color'], bsdf.inputs['Roughness'])
        
        elif input_name == 'Displacement':
            displacement_node = nodes.new('ShaderNodeDisplacement')
            displacement_node.inputs['Scale'].default_value = deslocamento_escala
            links.new(tex_node.outputs['Color'], displacement_node.inputs['Height'])
            output = nodes.get('Material Output')
        
            if output:
                links.new(displacement_node.outputs['Displacement'], output.inputs['Displacement'])

    # Configurações padrão
    bsdf.inputs['Roughness'].default_value = rugosidade

    # Aplicar material ao objeto
    objeto.data.materials.clear()
    objeto.data.materials.append(material)

def hex_to_rgba(hex_color, alpha=None, include_alpha=True):
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16) / 255.0
    g = int(hex_color[2:4], 16) / 255.0
    b = int(hex_color[4:6], 16) / 255.0
    a = 1.0
    if include_alpha and alpha is not None:
        a = alpha
        return (r, g, b, a)
    elif include_alpha:
        return (r, g, b, a)
    else:
        return (r, g, b)

def calcular_posicoes_rack(rack_x, bola_raio):
    """Calcula as posições com formação triangular rigorosa"""
    espacamento = bola_raio * 2.2  # Aumentado para evitar conflitos
    posicoes = []
    
    # Gera posições do triângulo (5 fileiras)
    for linha in range(5):
        qtd_bolas = linha + 1
        offset_x = rack_x + (linha * espacamento * 0.866)
        start_y = -(qtd_bolas - 1) * (espacamento / 2)
        for bola in range(qtd_bolas):
            y_pos = start_y + (bola * espacamento)
            posicoes.append((offset_x, y_pos))
    
    return posicoes

def criar_bolas(bola_raio, mesa_comprimento, mesa_altura_total, borda_espessura):
    z = mesa_altura_total + bola_raio
    bolas = []
    pasta_texturas_bolas = obter_caminho_absoluto(os.path.join('..', 'assets', 'Pool Ball Skins'))
    
    # POSIÇÃO DO RACK: lado direito da mesa
    rack_x = mesa_comprimento/2 - borda_espessura - bola_raio * 10
    
    # Configuração do rack triangular
    posicoes = calcular_posicoes_rack(rack_x, bola_raio)
    
    ordem_bolas = [
        1,                  # Linha 1: ponta do triângulo)
        2, 3,               # Linha 2
        4, 8, 5,            # Linha 3: bola 8 no centro
        6, 7, 9, 10,        # Linha 4
        11, 12, 13, 14, 15  # Linha 5: base do triângulo
    ]
    
    # Cria as bolas numeradas (1-15) na formação triangular
    for i, (x, y) in enumerate(posicoes):
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=bola_raio,
            location=(x, y, z),
            calc_uvs=True
        )
        bola = bpy.context.object
        bola.name = f"Ball{ordem_bolas[i]}"
        # Aplica material com textura individual
        caminho_textura_bola = os.path.join(pasta_texturas_bolas, f"Ball{ordem_bolas[i]}.jpg")
        aplicar_material(bola, texturas={'Base Color': (caminho_textura_bola, 'sRGB')}, rugosidade=0.0)
        
        # Aplica suavidade em todas as bolas
        bpy.ops.object.shade_smooth()
        bolas.append(bola)

    # BOLA BRANCA: lado esquerdo da mesa (posição de quebra)
    bola_branca_x = -mesa_comprimento/2 + borda_espessura + bola_raio * 6
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=bola_raio,
        location=(bola_branca_x, 0, z),
        calc_uvs=True
    )
    bola_branca = bpy.context.object
    bola_branca.name = "Ballcue"
    # Corrige aplicação de suavidade
    bpy.context.view_layer.objects.active = bola_branca
    bpy.ops.object.shade_smooth()
    
    # Aplica material com textura da bola branca
    caminho_textura_bola_branca = os.path.join(pasta_texturas_bolas, "Ballcue.jpg")
    aplicar_material(bola_branca, texturas={'Base Color': (caminho_textura_bola_branca, 'sRGB')}, rugosidade=0.0)
    bolas.append(bola_branca)

    return bolas

def criar_camera():
    # Adiciona a câmera de cima
    bpy.ops.object.camera_add(location=(0, 0, 10), rotation=(0, 0, 0))
    camera_top = bpy.context.object
    camera_top.name = "Camera_Top"
    # Rotação da câmera top para olhar para baixo (em radianos: X=90°)
    camera_top.rotation_euler = (math.radians(-2.20389), 0, 0)

    # Adiciona a câmera de canto
    bpy.ops.object.camera_add(location=(7, -7, 6))
    camera_canto = bpy.context.object
    camera_canto.name = "Camera_Canto"
    # Rotação da câmera canto para olhar para o centro da mesa 
    camera_canto.rotation_euler = (math.radians(60), 0, math.radians(45))

def adicionar_luz():
    # Define as cores em HEX para cada luz
    cor_luz_grande = hex_to_rgba("#ECFEFFFF", include_alpha=False)
    cor_luz_pequena = hex_to_rgba("#B3B2FF", include_alpha=False)

    # Luz grande (quente)
    bpy.ops.object.light_add(type='AREA', location=(0, 0, 3))
    area_light_grande = bpy.context.object
    area_light_grande.data.energy = 144
    area_light_grande.data.size = 9.33
    area_light_grande.data.color = cor_luz_grande  
    # Luz pequena (fria)
    bpy.ops.object.light_add(type='AREA', location=(2, 2, 2))
    area_light_pequena = bpy.context.object
    area_light_pequena.data.energy = 55
    area_light_pequena.data.size = 2
    area_light_pequena.data.color = cor_luz_pequena

def criar_mesa_de_sinuca(
    nome_raiz="MesaSinuca_Raiz",
    mesa_largura=2.0,
    mesa_comprimento=4.0,
    mesa_altura_total=1.1,
    mesa_espessura=0.05,
    borda_altura=0.1,
    borda_espessura=0.25,
    base_espessura=0.44,
    base_scale_reduction=1.2,
    cacapa_raio=0.1,
    bola_raio=0.057,
    perna_tamanho=0.35,
    perna_afastamento_y=0.025,
    perna_afastamento_x=0.025,
    caixa_largura=1.8,
    caixa_altura=0.33,
    caixa_profundidade=0.3,
    largura_berco=0.13):

    limpar_cena()
    
    # Chão
    bpy.ops.mesh.primitive_plane_add(
        size=15.0,
        enter_editmode=False,
        align='WORLD',
        location=(0, 0, 0),
        scale=(1, 1, 1)
    )
    chao = bpy.context.object
    chao.name = "Chao_Plano"
    # Adicionar material simples ao chão
    aplicar_material(chao, cor_base=hex_to_rgba("#2A2A2A"), rugosidade=0.5)
    
    # Feltro - área de jogo
    bpy.ops.mesh.primitive_cube_add(
        size=1, 
        location=(0, 0, mesa_altura_total - mesa_espessura / 2),
        calc_uvs=True,
        scale=(mesa_comprimento, mesa_largura, mesa_espessura)
    )
    feltro = bpy.context.object
    feltro.name = "Feltro"
    
    # Aplica material com textura ao feltro
    aplicar_material_feltro(feltro, {
        'Base Color': (obter_caminho_absoluto(os.path.join('..', 'assets', 'feltro_azul', '3D_1213_C0747_W24.tif.jpg')), 'sRGB'),
        'Roughness': (obter_caminho_absoluto(os.path.join('..', 'assets', 'feltro_azul', 'divina 0106_Roughness.jpg')), 'Non-Color'),
        'Normal': (obter_caminho_absoluto(os.path.join('..', 'assets', 'feltro_azul', 'redfelt_Normal.jpg')), 'Non-Color'),
        'Displacement': (obter_caminho_absoluto(os.path.join('..', 'assets', 'feltro_azul', 'redfelt_Displacement.jpg')), 'Non-Color'),
    })

    # Berço 
    berco_escala_x = mesa_comprimento
    berco_escala_y = mesa_largura
    berco_escala_z = 0.049
    berco_z = mesa_altura_total + 0.025
    
    bpy.ops.mesh.primitive_cube_add(
        size=1, 
        location=(0, 0, berco_z),
        scale=(berco_escala_x, berco_escala_y, berco_escala_z),
        calc_uvs=True
    )
    berco = bpy.context.object
    berco.name = "Berco"
        
    # Aplica material com textura azul ao berço
    aplicar_material_feltro(berco, {
        'Base Color': (obter_caminho_absoluto(os.path.join('..', 'assets', 'feltro_azul', '3D_1213_C0747_W24.tif.jpg')), 'sRGB'),
        'Roughness': (obter_caminho_absoluto(os.path.join('..', 'assets', 'feltro_azul', 'divina 0106_Roughness.jpg')), 'Non-Color'),
        'Normal': (obter_caminho_absoluto(os.path.join('..', 'assets', 'feltro_azul', 'redfelt_Normal.jpg')), 'Non-Color'),
        'Displacement': (obter_caminho_absoluto(os.path.join('..', 'assets', 'feltro_azul', 'redfelt_Displacement.jpg')), 'Non-Color'),
    })

    # Recorte central pra encaixar o feltro 
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, berco_z))
    recorte_berco = bpy.context.object
    recorte_berco.scale = (berco_escala_x - largura_berco, berco_escala_y - largura_berco, berco_escala_z + 0.001)
    recorte_berco.name = "RecorteBerco"
    bool_berco = berco.modifiers.new(name="RecorteBerco", type='BOOLEAN')
    bool_berco.operation = 'DIFFERENCE'
    bool_berco.object = recorte_berco
    bpy.context.view_layer.objects.active = berco
    bpy.ops.object.modifier_apply(modifier=bool_berco.name)
    bpy.data.objects.remove(recorte_berco)

    # Moldura
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=(0, 0, mesa_altura_total)
    )
    borda = bpy.context.object
    borda.name = "Borda"
    borda.scale = (mesa_comprimento + 2 * borda_espessura, mesa_largura + 2 * borda_espessura, borda_altura)
    
    # Modificador Bevel
    bevel = borda.modifiers.new(name="Bevel", type='BEVEL')
    bevel.width = 0.10
    bevel.segments = 5
    bevel.profile = 0.7
    bevel.limit_method = 'ANGLE'
    bevel.affect = 'EDGES'

    # Aplica material com base cor branca
    aplicar_material(borda, cor_base=hex_to_rgba("#e7e7e7"))


    # Recorte do centro - para encaixar o feltro
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
    base.scale = (4.4, mesa_largura * base_scale_reduction, base_espessura)
    base.name = "Base_Mesa"
    
    # Aplica material com cor à base
    aplicar_material(base, cor_base=hex_to_rgba("#e7e7e7"))
    
    # Mesa coletora
    caixa_x = 0
    caixa_y = -(mesa_largura/2 + caixa_profundidade/2 - 0.01)
    caixa_z = 0.82
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=(caixa_x, caixa_y, caixa_z)
    )
    caixa = bpy.context.object
    caixa.name = "Caixa_Coletora"
    caixa.scale = (caixa_largura/2, caixa_profundidade/2, caixa_altura/2)
    aplicar_material(caixa, cor_base=hex_to_rgba("#838383"))

    # Caçapas
    offset = 0.07
    posicoes_cacapas = [
        (mesa_comprimento/2 - offset, mesa_largura/2 - offset, mesa_altura_total),
        (-mesa_comprimento/2 + offset, mesa_largura/2 - offset, mesa_altura_total),
        (mesa_comprimento/2 - offset, -mesa_largura/2 + offset, mesa_altura_total),
        (-mesa_comprimento/2 + offset, -mesa_largura/2 + offset, mesa_altura_total),
        (0, mesa_largura/2, mesa_altura_total),
        (0, -mesa_largura/2, mesa_altura_total),
    ]
    cacapas = []
    for i, pos in enumerate(posicoes_cacapas):
        # Cilindro interno da caçapa
        bpy.ops.mesh.primitive_cylinder_add(
            radius=cacapa_raio - 0.001,
            depth=borda_altura - mesa_espessura + 0.01,
            location=(pos[0], pos[1], pos[2] - mesa_espessura)
        )
        interior_cacapa = bpy.context.object
        interior_cacapa.name = f"Interior_Cacapa_{i}"
        aplicar_material(interior_cacapa, cor_base=hex_to_rgba('#000000'))
        cacapas.append(interior_cacapa)

        # Cilindro para recorte (boolean)
        bpy.ops.mesh.primitive_cylinder_add(
            radius=cacapa_raio,
            depth=borda_altura + mesa_espessura + 0.01,
            location=(pos[0], pos[1], pos[2] - mesa_espessura / 2)
        )
        cacapa_recorte = bpy.context.object
        cacapa_recorte.name = f"Cacapa_Recorte_{i}"

        # Boolean para a borda
        mod_borda = borda.modifiers.new(name=f"Boolean_Cacapa_Borda_{i}", type="BOOLEAN")
        mod_borda.operation = 'DIFFERENCE'
        mod_borda.object = cacapa_recorte
        bpy.context.view_layer.objects.active = borda
        bpy.ops.object.modifier_apply(modifier=f"Boolean_Cacapa_Borda_{i}")

        # Boolean para o feltro
        mod_feltro = feltro.modifiers.new(name=f"Boolean_Cacapa_Feltro_{i}", type="BOOLEAN")
        mod_feltro.operation = 'DIFFERENCE'
        mod_feltro.object = cacapa_recorte
        bpy.context.view_layer.objects.active = feltro
        bpy.ops.object.modifier_apply(modifier=f"Boolean_Cacapa_Feltro_{i}")

        # Boolean para o berço
        mod_berco = berco.modifiers.new(name=f"Boolean_Cacapa_Berco_{i}", type="BOOLEAN")
        mod_berco.operation = 'DIFFERENCE'
        mod_berco.object = cacapa_recorte
        bpy.context.view_layer.objects.active = berco
        bpy.ops.object.modifier_apply(modifier=f"Boolean_Cacapa_Berco_{i}")

        # Remove o cilindro de recorte
        bpy.data.objects.remove(cacapa_recorte)

    # Bolas
    bolas = criar_bolas(bola_raio, mesa_comprimento, mesa_altura_total, borda_espessura)

    # Suportes
    perna_altura = mesa_altura_total - mesa_espessura - base_espessura 
    posicoes_pernas = [
        (mesa_comprimento / 2 + perna_afastamento_x, mesa_largura / 2 + perna_afastamento_y, perna_altura / 2),
        (-mesa_comprimento / 2 - perna_afastamento_x, mesa_largura / 2 + perna_afastamento_y, perna_altura / 2),
        (mesa_comprimento / 2 + perna_afastamento_x, -mesa_largura / 2 - perna_afastamento_y, perna_altura / 2),
        (-mesa_comprimento / 2 - perna_afastamento_x, -mesa_largura / 2 - perna_afastamento_y, perna_altura / 2),
    ]
    pernas = []
    for i, pos in enumerate(posicoes_pernas):
        bpy.ops.mesh.primitive_cube_add(size=1, location=pos, calc_uvs=True)
        perna = bpy.context.object
        perna.scale = (perna_tamanho, perna_tamanho, perna_altura)
        perna.name = f"Perna_{i}"
        aplicar_material(perna, cor_base=hex_to_rgba("#e7e7e7"))
        pernas.append(perna)

    # Criar raiz principal e subgrupos
    raiz = criar_objeto_pai(nome_raiz, (0, 0, 0))
    bolas_grupo = criar_objeto_pai("Bolas_Grupo", (0, 0, 0))
    pernas_grupo = criar_objeto_pai("Pernas_Grupo", (0, 0, 0))
    cacapas_grupo = criar_objeto_pai("Cacapas_Grupo", (0, 0, 0))

    # Lista de objetos
    objetos_principais = {
        "Mesa": [feltro, borda, base, caixa, berco],
        "Bolas": bolas,
        "Pernas": pernas,
        "Cacapas": cacapas,
    }

    # Parentear objetos aos subgrupos
    for obj in objetos_principais["Mesa"]:
        definir_pai(obj, raiz)
    for obj in objetos_principais["Bolas"]:
        definir_pai(obj, bolas_grupo)
    for obj in objetos_principais["Pernas"]:
        definir_pai(obj, pernas_grupo)
    for obj in objetos_principais["Cacapas"]:
        definir_pai(obj, cacapas_grupo)
    
    # Parentear subgrupos à raiz
    definir_pai(bolas_grupo, raiz)
    definir_pai(pernas_grupo, raiz)
    definir_pai(cacapas_grupo, raiz)


if __name__ == "__main__":
    criar_mesa_de_sinuca()
    criar_camera()
    adicionar_luz()