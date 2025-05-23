import bpy
import math
import os
import random
import random

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

def caminho_relativo(rel_path):
    """Retorna o caminho absoluto a partir do diretório do script."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, rel_path)

def aplicar_texturas_bolas(pasta_texturas_rel):
    pasta_texturas = caminho_relativo(pasta_texturas_rel)
    nomes_bolas = [f"Ball{i}" for i in range(1, 16)] + ["Ballcue"]
    
    for nome_bola in nomes_bolas:
        obj = bpy.data.objects.get(nome_bola)
        if obj:
            caminho_textura = os.path.join(pasta_texturas, f"{nome_bola}.jpg")
            if os.path.exists(caminho_textura):
                # Cria material com nodes
                mat = bpy.data.materials.new(name=f"Material_{nome_bola}")
                mat.use_nodes = True
                nodes = mat.node_tree.nodes
                links = mat.node_tree.links
                
                # Remove todos os nós existentes
                nodes.clear()

                if not nodes:
                    print("nodes está vazio")

                # Cria nós obrigatórios
                bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
                material_output = nodes.new(type='ShaderNodeOutputMaterial')  # <-- Nó crítico!
                
                # Configura textura
                tex_image = nodes.new('ShaderNodeTexImage')
                tex_image.image = bpy.data.images.load(caminho_textura)
                
                # Conecta os nós
                links.new(bsdf.outputs['BSDF'], material_output.inputs['Surface'])  # <-- Conexão correta
                links.new(tex_image.outputs['Color'], bsdf.inputs['Base Color'])
                
                # Aplica o material
                obj.data.materials.clear()
                obj.data.materials.append(mat)
            else:
                print(f"ERRO: Arquivo {caminho_textura} não encontrado!")

def aplicar_textura_feltro(pasta_textura_rel):
    pasta_textura = caminho_relativo(pasta_textura_rel)
    caminho_base_color = os.path.join(pasta_textura, "3D_1213_C0871_W24.tif.jpg")
    caminho_roughness = os.path.join(pasta_textura, "divina 0106_Roughness.jpg")

    if os.path.exists(caminho_base_color):
        feltro = bpy.data.materials.new(name="Feltro_Material")
        feltro.use_nodes = True
        nodes = feltro.node_tree.nodes
        links = feltro.node_tree.links
        nodes.clear()
        bsdf = nodes.new('ShaderNodeBsdfPrincipled')
        material_output = nodes.new('ShaderNodeOutputMaterial')
        # Base Color
        tex_image = nodes.new('ShaderNodeTexImage')
        tex_image.image = bpy.data.images.load(caminho_base_color)
        links.new(tex_image.outputs['Color'], bsdf.inputs['Base Color'])
        # Roughness (opcional, para um leve efeito)
        if os.path.exists(caminho_roughness):
            tex_roughness = nodes.new('ShaderNodeTexImage')
            tex_roughness.image = bpy.data.images.load(caminho_roughness)
            tex_roughness.image.colorspace_settings.name = 'Non-Color'
            links.new(tex_roughness.outputs['Color'], bsdf.inputs['Roughness'])
        else:
            bsdf.inputs['Roughness'].default_value = 0.5  # valor padrão suave
        links.new(bsdf.outputs['BSDF'], material_output.inputs['Surface'])
        obj = bpy.data.objects.get("Feltro")
        if obj:
            obj.data.materials.clear()
            obj.data.materials.append(feltro)
        else:
            print("ERRO: Objeto 'Feltro' não encontrado!")
    else:
        print(f"ERRO: Arquivo {caminho_base_color} não encontrado!")

def aplicar_textura_moldura(pasta_textura_rel):
    pasta_textura = caminho_relativo(pasta_textura_rel)
    caminho_textura = os.path.join(pasta_textura, "madeira2.jpg")
    if os.path.exists(caminho_textura):
        # Cria material com nodes
        moldura = bpy.data.materials.new(name="Moldura_Material")
        moldura.use_nodes = True
        nodes = moldura.node_tree.nodes
        links = moldura.node_tree.links
        
        # Remove todos os nós existentes para evitar conflitos
        for n in nodes:
            nodes.remove(n)
        # Cria nós obrigatórios
        tex_image = nodes.new('ShaderNodeTexImage')
        tex_image.image = bpy.data.images.load(caminho_textura)
        bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
        material_output = nodes.new(type='ShaderNodeOutputMaterial')
        # Conecta textura -> BSDF -> Output
        links.new(tex_image.outputs['Color'], bsdf.inputs['Base Color'])
        links.new(bsdf.outputs['BSDF'], material_output.inputs['Surface'])
        # Aplica o material ao objeto correto (moldura)
        obj = bpy.context.object
        obj.data.materials.clear()
        obj.data.materials.append(moldura)
    else:
        print(f"ERRO: Arquivo {caminho_textura} não encontrado!")

def criar_mesa_de_sinuca():
    # Parâmetros principais
    mesa_largura = 2.0
    mesa_comprimento = 4.0
    mesa_altura_total = 1
    mesa_espessura = 0.05
    borda_altura = 0.1
    borda_espessura = 0.25
    base_espessura = 0.44
    base_scale_reduction = 1.10
    cacapa_raio = 0.1
    bola_raio = 0.057
    perna_raio = 0.12
    afastamento_y = 0.1
    caixa_largura = 1.0       # Maior na largura
    caixa_altura = 0.33      # Mais alta
    caixa_profundidade = 0.3  # Suficientemente profunda

    limpar_cena()

    # Tampo da mesa
    bpy.ops.mesh.primitive_cube_add(
        size=1, 
        location=(0, 0, mesa_altura_total - mesa_espessura / 2),
        calc_uvs=True)
    mesa = bpy.context.object
    mesa.scale = (mesa_comprimento, mesa_largura, mesa_espessura)
    mesa.name = "Feltro"
    aplicar_textura_feltro(os.path.join('..', 'assets', 'feltro'))
    
    # Moldura
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, mesa_altura_total))
    borda = bpy.context.object
    borda.name = "Borda"
    borda.scale = (mesa_comprimento + 2 * borda_espessura, mesa_largura + 2 * borda_espessura, borda_altura)
    mat_borda = bpy.data.materials.new(name="Material_Borda")
    mat_borda.diffuse_color = (0.4, 0.2, 0.0, 1.0)
    borda.data.materials.append(mat_borda)
    aplicar_textura_moldura(os.path.join('..', 'assets', 'Pool Ball Skins'))
    
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
    base.scale = (4.2, mesa_largura * base_scale_reduction, base_espessura)
    base.name = "Base_Mesa"
    mat_base = bpy.data.materials.new(name="Material_Base")
    mat_base.diffuse_color = (0.2, 0.1, 0.0, 1.0)
    base.data.materials.append(mat_base)

    # Mesa coletora
    # Posição: do lado da base, centralizada no eixo X
    caixa_x = 0
    caixa_y = -(mesa_largura/2 + caixa_profundidade/2 - 0.01)
    caixa_z = 0.68
    
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=(caixa_x, caixa_y, caixa_z)
    )
    caixa = bpy.context.object
    caixa.name = "Caixa_Coletora"
    caixa.scale = (caixa_largura/2, caixa_profundidade/2, caixa_altura/2)
    
    # Material da caixa coletora
    mat_caixa = bpy.data.materials.new(name="Material_Caixa_Coletora")
    mat_caixa.diffuse_color = (0.3, 0.15, 0.05, 1.0)
    caixa.data.materials.append(mat_caixa)

    

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
    for i, pos in enumerate(posicoes_cacapas):
        bpy.ops.mesh.primitive_cylinder_add(radius=cacapa_raio, depth=borda_altura + mesa_espessura + 0.01, location=(pos[0], pos[1], pos[2] - mesa_espessura / 2))
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
    contador_bolas = 1
    bola_raio = 0.057

    # Parâmetros da mesa para cálculo da área jogável
    mesa_comprimento = 4.0
    mesa_largura = 2.0
    mesa_altura_total = 1.0
    borda_espessura = 0.25

    # Limites da área verde (parte jogável)
    min_x = -mesa_comprimento/2 + borda_espessura + bola_raio
    max_x = mesa_comprimento/2 - borda_espessura - bola_raio
    min_y = -mesa_largura/2 + borda_espessura + bola_raio
    max_y = mesa_largura/2 - borda_espessura - bola_raio
    z = mesa_altura_total + bola_raio

    # Criar bolas coloridas aleatoriamente (1-15)
    posicoes_ocupadas = []  # Lista para evitar sobreposição

    for i in range(1, 16):
        # Tentar encontrar posição que não sobreponha outras bolas
        tentativas = 0
        while tentativas < 20:  # Limite de tentativas para evitar loop infinito
            x = random.uniform(min_x, max_x)
            y = random.uniform(min_y, max_y)
            
            # Verificar se a posição está longe o suficiente das outras bolas
            posicao_valida = True
            for pos in posicoes_ocupadas:
                dist = math.sqrt((x - pos[0])**2 + (y - pos[1])**2)
                if dist < bola_raio * 3.0:  # 2.2 = distância mínima entre centros
                    posicao_valida = False
                    break
                    
            if posicao_valida:
                posicoes_ocupadas.append((x, y))
                break
                
            tentativas += 1
        
        # Criar a bola na posição encontrada (ou a última tentativa)
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=bola_raio,
            location=(x, y, z),
            calc_uvs=True
        )
        bola = bpy.context.object
        bola.name = f"Ball{contador_bolas}"
        
        # Adicionar rotação aleatória em todos os eixos
        bola.rotation_euler.x = random.uniform(0, 2 * math.pi)
        bola.rotation_euler.y = random.uniform(0, 2 * math.pi)
        bola.rotation_euler.z = random.uniform(0, 2 * math.pi)
        
        bolas.append(bola)
        contador_bolas += 1


    # Bola branca (cue) - posição mais à esquerda do campo
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=bola_raio,
        location=(min_x + bola_raio * 3, 0, z),  # Posição clássica para início
        calc_uvs=True
    )
    bola_branca = bpy.context.object
    bola_branca.name = "Ballcue"
    
    # Rotação aleatória para a bola branca
    bola_branca.rotation_euler.x = random.uniform(0, 2 * math.pi)
    bola_branca.rotation_euler.y = random.uniform(0, 2 * math.pi)
    bola_branca.rotation_euler.z = random.uniform(0, 2 * math.pi)
    
    bolas.append(bola_branca)

    # Aplicar texturas às bolas
    aplicar_texturas_bolas(os.path.join('..', 'assets', 'Pool Ball Skins'))
    

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

criar_mesa_de_sinuca()  


