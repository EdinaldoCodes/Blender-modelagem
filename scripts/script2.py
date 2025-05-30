import bpy
import math
import os
import random

# Parametros globais
MESA_LARGURA = 2.0
MESA_COMPRIMENTO = 4.0
MESA_ALTURA_TOTAL = 1.1
MESA_ESPESSURA = 0.05
BORDA_ALTURA = 0.1
BORDA_ESPESSURA = 0.25
BASE_ESPESSURA = 0.44 
BASE_SCALE_REDUCTION = 1.2
CACAPA_RAIO = 0.1
BOLA_RAIO = 0.057
PERNA_TAMANHO = 0.35
PERNA_AFASTAMENTO_Y = 0.025
PERNA_AFASTAMENTO_X = 0.025
CAIXA_LARGURA = 1.8
CAIXA_ALTURA = 0.33
CAIXA_PROFUNDIDADE = 0.3
BERCO_ESPESSURA = 0.025
LARGURA_BERCO = 0.13

def limpar_cena():
    # Garante que está no modo de objeto antes de selecionar e deletar
    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode='OBJECT')
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

def obter_caminho_absoluto(rel_path):
    """Retorna o caminho absoluto a partir do diretório do script."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, rel_path)

def carregar_textura_imagem(caminho_textura, colorspace='sRGB'):
    
    # Carrega uma imagem de textura e retorna o objeto image do Blender
    if not os.path.exists(caminho_textura):
        print(f"ERRO: Arquivo {caminho_textura} não encontrado!")
        return None
    return bpy.data.images.load(caminho_textura)

def adicionar_node_textura(material, nome_input, caminho_textura, colorspace='sRGB'):
    # Adiciona um node de textura ao material e conecta ao input especificado do BSDF
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    bsdf = None

    # Encontra o node de BSDF no material 
    for node in nodes:
        if node.type == 'BSDF_PRINCIPLED':
            bsdf = node
            break
        
        # Se o node de BSDF ainda não foi encontrado, cria um novo
        elif not bsdf:
            bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')


    # Cria e conecta o node de textura
    tex_image = carregar_textura_imagem(caminho_textura, colorspace)
    if tex_image:
        tex_node = nodes.new('ShaderNodeTexImage')
        tex_node.image = tex_image

        # Configura o colorspace da textura, caso seja diferente de sRGB
        if colorspace != 'sRGB':
            tex_node.image.colorspace_settings.name = colorspace # altera o colorspace da textura para o colorspace especificado
        links.new(tex_node.outputs['Color'], bsdf.inputs[nome_input])
        return tex_node
    return None

def aplicar_textura_objeto(objeto, texturas, valor_textura=None):
    """
    Aplica texturas PBR em um objeto
    texturas: dict com chaves possíveis: 'Base Color', 'Roughness', 'Normal', etc.
    Exemplo:
      {'Base Color': 'caminho.jpg', 'Roughness': 'rough.jpg', 'Normal': 'normal.png'}
    """
    material = bpy.data.materials.new(name=f"Material_{objeto.name}")
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    material_output = nodes.new(type='ShaderNodeOutputMaterial')
    links.new(bsdf.outputs['BSDF'], material_output.inputs['Surface'])

    # Base Color
    if 'Base Color' in texturas:
        adicionar_node_textura(material, 'Base Color', texturas['Base Color'], 'sRGB')
    # Roughness
    if 'Roughness' in texturas:
        adicionar_node_textura(material, 'Roughness', texturas['Roughness'], 'Non-Color')
    # Se nenhuma textura de normal for fornecida, usa o valor fornecido "valor_textura" para a rugosidade
    if 'Roughness' not in texturas and valor_textura is not None:
        bsdf.inputs['Roughness'].default_value = valor_textura
        
    # Normal Map
    if 'Normal' in texturas:
        tex_image = carregar_textura_imagem(texturas['Normal'], 'Non-Color')
        if tex_image:
            tex_node = nodes.new('ShaderNodeTexImage')
            tex_node.image = tex_image
            tex_node.image.colorspace_settings.name = 'Non-Color'
            normal_map = nodes.new('ShaderNodeNormalMap')
            links.new(tex_node.outputs['Color'], normal_map.inputs['Color'])
            links.new(normal_map.outputs['Normal'], bsdf.inputs['Normal'])

    objeto.data.materials.clear()
    objeto.data.materials.append(material)

def aplicar_material_simples(objeto, cor_base=None, rugosidade=None):
    # Essa função ta sendo usada para o chão 
    # Aplica um material simples ao objeto - sem texturas
    # cor_base: Cor base do material, se fornecida
    # rugosidade: Rugosidade do material, se fornecida
    # Exemplo: aplicar_material_simples(objeto, cor_base=(0.5, 0.5, 0.5, 1.0), rugosidade=0.5)
    # Essa função pode ser expandida para aceitar outras propriedades como opacidade, reflexao.
    material = bpy.data.materials.new(name=f"Material_{objeto.name}")
    material.use_nodes = True
    nodes = material.node_tree.nodes
    nodes.clear()
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    material_output = nodes.new(type='ShaderNodeOutputMaterial')
    links = material.node_tree.links
    links.new(bsdf.outputs['BSDF'], material_output.inputs['Surface'])
    
    if cor_base:
        bsdf.inputs['Base Color'].default_value = cor_base
    if rugosidade:
        bsdf.inputs['Roughness'].default_value = rugosidade
        
    if objeto.data.materials:
        # Se já houver materiais, substitui o primeiro
        objeto.data.materials[0] = material
    else:
        # Caso contrário, adiciona o novo material
        objeto.data.materials.append(material)

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16)/255.0 for i in (0, 2, 4))

def criar_camera():
    # Adiciona a câmera de cima
    bpy.ops.object.camera_add(location=(0, 0, 10), rotation=(0, 0, 0))
    camera_top = bpy.context.object

    # Rotação para olhar para baixo (em radianos: X=90°)
    camera_top.rotation_euler = (math.radians(-2.20389), 0, 0)
    camera_top.name = "Camera_Top"

    # Adiciona a câmera de canto
    bpy.ops.object.camera_add(location=(7, -7, 6))
    camera_corner = bpy.context.object
    
    # Rotação para olhar para o centro da mesa (ajuste conforme necessário)
    camera_corner.rotation_euler = (math.radians(60), 0, math.radians(45))
    camera_corner.name = "Camera_Corner"

def adicionar_luz():
    # Cores em HEX para cada luz 
    cor_hex_luz_grande = "#ECFEFF"  
    cor_hex_luz_pequena = "#B3B2FF"  

    # Convertendo para RGB
    cor_rgb_grande = hex_to_rgb(cor_hex_luz_grande)
    cor_rgb_pequena = hex_to_rgb(cor_hex_luz_pequena)

    # Luz grande (quente)
    bpy.ops.object.light_add(type='AREA', location=(0, 0, 3))
    area_light_grande = bpy.context.object
    area_light_grande.data.energy = 144
    area_light_grande.data.size = 9.33
    area_light_grande.data.color = cor_rgb_grande  

    # Luz pequena (fria)
    bpy.ops.object.light_add(type='AREA', location=(2, 2, 2))
    area_light_pequena = bpy.context.object
    area_light_pequena.data.energy = 55
    area_light_pequena.data.size = 2
    area_light_pequena.data.color = cor_rgb_pequena

def criar_mesa_de_sinuca():
    
    limpar_cena()

    # Feltro - área de jogo
    bpy.ops.mesh.primitive_cube_add(
        size=1, 
        location=(0, 0, MESA_ALTURA_TOTAL - MESA_ESPESSURA / 2),
        calc_uvs=True)
    mesa = bpy.context.object
    mesa.scale = (MESA_COMPRIMENTO, MESA_LARGURA, MESA_ESPESSURA)
    mesa.name = "Feltro"
    
    # Aplica textura à mesa
    aplicar_textura_objeto(mesa, {
        'Base Color': obter_caminho_absoluto(os.path.join('..', 'assets', 'feltro', '3D_1213_C0871_W24.tif.jpg')),
        'Roughness': obter_caminho_absoluto(os.path.join('..', 'assets', 'feltro', 'divina 0106_Roughness.jpg'))
    })

    # Berço 
    berco_escala_x = MESA_COMPRIMENTO
    berco_escala_y = MESA_LARGURA
    berco_escala_z = 0.049
    berco_z = MESA_ALTURA_TOTAL + 0.025
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, berco_z), calc_uvs=True)
    berco = bpy.context.object
    berco.scale = (berco_escala_x, berco_escala_y, berco_escala_z)
    berco.name = "Berco"
    
    # Aplica textura ao berço
    aplicar_textura_objeto(berco, {
        'Base Color': obter_caminho_absoluto(os.path.join('..', 'assets', 'feltro', '3D_1213_C0871_W24.tif.jpg')),
        'Roughness': obter_caminho_absoluto(os.path.join('..','assets', 'feltro', 'divina 0106_Roughness.jpg'))
    })
    
    # Recorte central pra encaixar o feltro 
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, berco_z))
    recorte_berco = bpy.context.object
    recorte_berco.scale = (berco_escala_x - LARGURA_BERCO, berco_escala_y - LARGURA_BERCO, berco_escala_z + 0.001)
    recorte_berco.name = "RecorteBerco"
    bool_berco = berco.modifiers.new(name="RecorteBerco", type='BOOLEAN')
    bool_berco.operation = 'DIFFERENCE'
    bool_berco.object = recorte_berco
    bpy.context.view_layer.objects.active = berco
    bpy.ops.object.modifier_apply(modifier=bool_berco.name)
    bpy.data.objects.remove(recorte_berco)

    # Moldura
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, MESA_ALTURA_TOTAL))
    borda = bpy.context.object
    borda.name = "Borda"
    borda.scale = (MESA_COMPRIMENTO + 2 * BORDA_ESPESSURA, MESA_LARGURA + 2 * BORDA_ESPESSURA, BORDA_ALTURA)
    mat_borda = bpy.data.materials.new(name="Material_Borda")
    mat_borda.diffuse_color = (0.4, 0.2, 0.0, 1.0)
    borda.data.materials.append(mat_borda)
    
    # Modificador Bevel
    bevel = borda.modifiers.new(name="Bevel", type='BEVEL')
    bevel.width = 0.10
    bevel.segments = 5
    bevel.profile = 0.7
    bevel.limit_method = 'ANGLE'
    bevel.affect = 'EDGES'

    # Aplica textura à borda
    aplicar_textura_objeto(borda, {
        'Base Color': obter_caminho_absoluto(os.path.join('..','assets', 'Pool Ball Skins', 'madeira2.jpg'))
    })
    
    # Recorte do centro - para encaixar o feltro
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, MESA_ALTURA_TOTAL))
    corte = bpy.context.object
    corte.scale = (MESA_COMPRIMENTO, MESA_LARGURA, BORDA_ALTURA + 0.01)
    
    mod = borda.modifiers.new(name="Boolean", type="BOOLEAN")
    mod.operation = 'DIFFERENCE'
    mod.object = corte
    bpy.context.view_layer.objects.active = borda
    bpy.ops.object.modifier_apply(modifier="Boolean")
    bpy.data.objects.remove(corte)

    # Base
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, MESA_ALTURA_TOTAL - MESA_ESPESSURA - BASE_ESPESSURA / 2))
    base = bpy.context.object
    
    # ajusta a escala em relação ao tamanho da mesa
    base.scale = (4.4, MESA_LARGURA * BASE_SCALE_REDUCTION, BASE_ESPESSURA) 
    base.name = "Base_Mesa"
    mat_base = bpy.data.materials.new(name="Material_Base")
    mat_base.diffuse_color = (0.2, 0.1, 0.0, 1.0)
    base.data.materials.append(mat_base)
        # Aplica textura à borda
    aplicar_textura_objeto(base, {
        'Base Color': obter_caminho_absoluto(os.path.join('..','assets', 'Pool Ball Skins', 'madeira2.jpg'))
    })
    # Mesa coletora
    caixa_x = 0
    caixa_y = -(MESA_LARGURA/2 + CAIXA_PROFUNDIDADE/2 - 0.01)
    caixa_z = 0.82 # altura da mesa Coletora
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=(caixa_x, caixa_y, caixa_z)
    )
    caixa = bpy.context.object
    caixa.name = "Caixa_Coletora"
    caixa.scale = (CAIXA_LARGURA/2, CAIXA_PROFUNDIDADE/2, CAIXA_ALTURA/2)
    mat_caixa = bpy.data.materials.new(name="Material_Caixa_Coletora")
    mat_caixa.diffuse_color = (0.3, 0.15, 0.05, 1.0)
    caixa.data.materials.append(mat_caixa)

    # Caçapas
    offset = 0.07  # tamanho do cilindro 
    posicoes_cacapas = [
        ( MESA_COMPRIMENTO/2 - offset,  MESA_LARGURA/2 - offset, MESA_ALTURA_TOTAL),  # canto superior direito
        (-MESA_COMPRIMENTO/2 + offset,  MESA_LARGURA/2 - offset, MESA_ALTURA_TOTAL),  # canto superior esquerdo
        ( MESA_COMPRIMENTO/2 - offset, -MESA_LARGURA/2 + offset, MESA_ALTURA_TOTAL),  # canto inferior direito
        (-MESA_COMPRIMENTO/2 + offset, -MESA_LARGURA/2 + offset, MESA_ALTURA_TOTAL),  # canto inferior esquerdo
        (0, MESA_LARGURA/2, MESA_ALTURA_TOTAL),  # meio superior
        (0, -MESA_LARGURA/2, MESA_ALTURA_TOTAL), # meio inferior
    ]
    cacapas = []
    for i, pos in enumerate(posicoes_cacapas):
        # Cria o cilindro para representar a caçapa
        interior_cacapa = bpy.ops.mesh.primitive_cylinder_add(radius=CACAPA_RAIO-0.001, depth=(BORDA_ALTURA - MESA_ESPESSURA + 0.01), location=(pos[0], pos[1], pos[2] - MESA_ESPESSURA))
        mat_interior_cacapa = bpy.data.materials.new(name="Material_Interior_Cacapa")
        mat_interior_cacapa.diffuse_color = (0.0, 0.0, 0.0, 1.0)  # cor escura para o interior
        bpy.context.object.data.materials.append(mat_interior_cacapa)

        # Cria um novo cilindro realizar o recorte
        bpy.ops.mesh.primitive_cylinder_add(radius=CACAPA_RAIO, depth=BORDA_ALTURA + MESA_ESPESSURA + 0.01, location=(pos[0], pos[1], pos[2] - MESA_ESPESSURA / 2))
        cacapa = bpy.context.object
        cacapa.name = f"Cacapa_{i}"
       
        # Boolean para a borda
        mod_borda = borda.modifiers.new(name=f"Boolean_Cacapa_Borda_{i}", type="BOOLEAN")
        mod_borda.operation = 'DIFFERENCE'
        mod_borda.object = cacapa
        bpy.context.view_layer.objects.active = borda # certifica que a borda está ativa
        bpy.ops.object.modifier_apply(modifier=f"Boolean_Cacapa_Borda_{i}")
       
        # Boolean para o tampo
        mod_mesa = mesa.modifiers.new(name=f"Boolean_Cacapa_Mesa_{i}", type="BOOLEAN")
        mod_mesa.operation = 'DIFFERENCE'
        mod_mesa.object = cacapa
        bpy.context.view_layer.objects.active = mesa # certifica que a mesa está ativa
        bpy.ops.object.modifier_apply(modifier=f"Boolean_Cacapa_Mesa_{i}")

        # Boolean para o berço
        mod_berco = berco.modifiers.new(name=f"Boolean_Cacapa_Berco_{i}", type="BOOLEAN")
        mod_berco.operation = 'DIFFERENCE'
        mod_berco.object = cacapa
        bpy.context.view_layer.objects.active = berco # certifica que o berço está ativo
        bpy.ops.object.modifier_apply(modifier=f"Boolean_Cacapa_Berco_{i}")
        bpy.data.objects.remove(cacapa)
        cacapas.append(cacapa)
        #  adiciona ocilindro para o interior da caçapa
        cacapas.append(interior_cacapa)  
        
    # Bolas
    bolas = []

    # Define os limites para as posições das bolas
    min_x = -MESA_COMPRIMENTO/2 + BORDA_ESPESSURA + BOLA_RAIO
    max_x = MESA_COMPRIMENTO/2 - BORDA_ESPESSURA - BOLA_RAIO
    min_y = -MESA_LARGURA/2 + BORDA_ESPESSURA + BOLA_RAIO
    max_y = MESA_LARGURA/2 - BORDA_ESPESSURA - BOLA_RAIO
    z = MESA_ALTURA_TOTAL + BOLA_RAIO
    posicoes_ocupadas = []
    pasta_texturas_bolas = obter_caminho_absoluto(os.path.join('..', 'assets', 'Pool Ball Skins'))
    for i in range(1, 16):
        tentativas = 0
        while tentativas < 20:
            x = random.uniform(min_x, max_x)
            y = random.uniform(min_y, max_y)
            posicao_valida = True
            for pos in posicoes_ocupadas:
                dist = math.sqrt((x - pos[0])**2 + (y - pos[1])**2)
                if dist < BOLA_RAIO * 3.0:
                    posicao_valida = False
                    break
            if posicao_valida:
                posicoes_ocupadas.append((x, y))
                break
            tentativas += 1
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=BOLA_RAIO,
            location=(x, y, z),
            calc_uvs=True
        )
        bola = bpy.context.object
        bola.name = f"Ball{i}"
        bola.rotation_euler.x = random.uniform(0, 2 * math.pi)
        bola.rotation_euler.y = random.uniform(0, 2 * math.pi)
        bola.rotation_euler.z = random.uniform(0, 2 * math.pi)
        bolas.append(bola)
        
        # Aplica textura individual da bola
        caminho_textura_bola = os.path.join(pasta_texturas_bolas, f"Ball{i}.jpg")
        
        aplicar_textura_objeto(bola, 
        {'Base Color': caminho_textura_bola}, 0.0) # o segundo argumento é o valor padrão para a rugosidade, ou seja, deixa mais reflexivo
        
        # Aplica rugosidade em todas as bolas 
        # Não aplica na bola branca 
        for bola in bolas:
            bpy.ops.object.shade_smooth()
        
    # Bola branca 
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=BOLA_RAIO,
        location=(min_x + BOLA_RAIO * 3, 0, z),
        calc_uvs=True
    )
    bola_branca = bpy.context.object
    bola_branca.name = "Ballcue"
    bola_branca.rotation_euler.x = random.uniform(0, 2 * math.pi)
    bola_branca.rotation_euler.y = random.uniform(0, 2 * math.pi)
    bola_branca.rotation_euler.z = random.uniform(0, 2 * math.pi)
    bolas.append(bola_branca)
    caminho_textura_bola_branca = os.path.join(pasta_texturas_bolas, "Ballcue.jpg")
    aplicar_textura_objeto(bola_branca, {'Base Color': caminho_textura_bola_branca})

    # Suportes
    perna_altura = MESA_ALTURA_TOTAL - MESA_ESPESSURA - BASE_ESPESSURA
    posicoes_pernas = [
        (MESA_COMPRIMENTO / 2 + PERNA_AFASTAMENTO_X, MESA_LARGURA / 2 + PERNA_AFASTAMENTO_Y, perna_altura / 2),
        (-MESA_COMPRIMENTO / 2 - PERNA_AFASTAMENTO_X, MESA_LARGURA / 2 + PERNA_AFASTAMENTO_Y, perna_altura / 2),
        (MESA_COMPRIMENTO / 2 + PERNA_AFASTAMENTO_X, -MESA_LARGURA / 2 - PERNA_AFASTAMENTO_Y, perna_altura / 2),
        (-MESA_COMPRIMENTO / 2 - PERNA_AFASTAMENTO_X, -MESA_LARGURA / 2 - PERNA_AFASTAMENTO_Y, perna_altura / 2),
    ]
    pernas = []
    for i, pos in enumerate(posicoes_pernas):
        bpy.ops.mesh.primitive_cube_add(size=1, location=pos, calc_uvs=True)
        perna = bpy.context.object
        perna.scale = (PERNA_TAMANHO, PERNA_TAMANHO, perna_altura)
        perna.name = f"Perna_{i}"
        mat_perna = bpy.data.materials.new(name="Material_Perna")
        mat_perna.diffuse_color = (0.2, 0.1, 0.0, 1.0)
        perna.data.materials.append(mat_perna)
        pernas.append(perna)

         # Aplica textura à mesa
        aplicar_textura_objeto(perna, {
            'Base Color': obter_caminho_absoluto(os.path.join('..','assets', 'Pool Ball Skins', 'madeira2.jpg'))
        })
        
        # Adicionando o chão com um plano
    bpy.ops.mesh.primitive_plane_add(
        size=20,         # Tamanho inicial do plano (ajuste conforme necessário)
        enter_editmode=False, # Desabilita o modo de edição
        align='WORLD', # Alinha ao mundo (geralmente Z=0 para o chão)
        location=(0, 0, 0), # Posição do centro do plano (geralmente Z=0 para o chão)
        scale=(1, 1, 1) # Escala do plano
    )
    chao = bpy.context.object  # Pega o objeto recém-criado
    chao.name = "Chao_Plano"   # Renomeia para organização

    # 2. (Opcional) Adicionar um material simples ao chão
    aplicar_material_simples(chao,
        cor_base=(0.1, 0.1, 0.1, 1),
        rugosidade=0.8
        )
    
    # Agrupando todos os objetos relevantes sob um objeto vazio (Empty) como raiz
    empty = criar_objeto_pai("MesaSinuca_Raiz", (0, 0, 0))
    
    # Lista de objetos para parentear
    objetos_principais = [mesa, borda, base, caixa, berco] + bolas + pernas
    for obj in objetos_principais:
        definir_pai(obj, empty)
    
    # Caçapas não precisam de parente pois são removidas após boolean

if __name__ == "__main__":
    criar_mesa_de_sinuca()
    criar_camera()
    adicionar_luz()
