import bpy
import math
import os

def limpar_cena():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()


def criar_cacapas():
    cacapa_raio = 0.1
    mesa_comprimento = 4.0
    mesa_largura = 2.0
    mesa_altura_total = 1
    mesa_espessura = 0.05
    borda_altura = 0.1
    posicoes_cacapas = [
        (mesa_comprimento / 2, mesa_largura / 2, mesa_altura_total),
        (-mesa_comprimento / 2, mesa_largura / 2, mesa_altura_total),
        (mesa_comprimento / 2, -mesa_largura / 2, mesa_altura_total),
        (-mesa_comprimento / 2, -mesa_largura / 2, mesa_altura_total),
        (0, mesa_largura / 2, mesa_altura_total),
        (0, -mesa_largura / 2, mesa_altura_total),
    ]
    borda = bpy.data.objects["Borda"]
    mesa = bpy.data.objects["Mesa_Base"]
    for i, pos in enumerate(posicoes_cacapas):
        # Criar cilindro para cortar
        bpy.ops.mesh.primitive_cylinder_add(radius=cacapa_raio, depth=borda_altura + mesa_espessura + 0.01, location=(pos[0], pos[1], pos[2] - mesa_espessura / 2))
        cacapa = bpy.context.object
        cacapa.name = f"Cacapa_{i}"
        
        # Boolean para a borda
        mod_borda = borda.modifiers.new(name=f"Boolean_Cacapa_Borda_{i}", type="BOOLEAN")
        mod_borda.operation = 'DIFFERENCE'
        mod_borda.object = cacapa
        bpy.context.view_layer.objects.active = borda
        bpy.ops.object.modifier_apply(modifier=f"Boolean_Cacapa_Borda_{i}")
        
        # Boolean para o tampo da mesa
        mod_mesa = mesa.modifiers.new(name=f"Boolean_Cacapa_Mesa_{i}", type="BOOLEAN")
        mod_mesa.operation = 'DIFFERENCE'
        mod_mesa.object = cacapa
        bpy.context.view_layer.objects.active = mesa
        bpy.ops.object.modifier_apply(modifier=f"Boolean_Cacapa_Mesa_{i}")
        
        bpy.data.objects.remove(cacapa)

def criar_bolas():
    bola_raio = 0.057
    mesa_altura_total = 1

    # Parâmetros para posicionamento
    base_x = 0.8  # Posição do triângulo na mesa (ajuste conforme necessário)
    base_y = 0.0
    contador_bolas = 1

    # Cria as bolas numeradas (1 a 15) em formato de triângulo
    for i in range(5):  # 5 linhas
        for j in range(i + 1):
            x = base_x + i * bola_raio * 2.0
            y = base_y + (j - i / 2) * bola_raio * 2.0
            z = mesa_altura_total + bola_raio
            bpy.ops.mesh.primitive_uv_sphere_add(radius=bola_raio, location=(x, y, z))
            bola = bpy.context.object
            bola.name = f"ball{contador_bolas}"
            contador_bolas += 1

    
    x_branca = -1.2
    y_branca = 0.0
    z_branca = mesa_altura_total + bola_raio
    bpy.ops.mesh.primitive_uv_sphere_add(radius=bola_raio, location=(x_branca, y_branca, z_branca))
    bola_branca = bpy.context.object
    bola_branca.name = "ballcue"


def aplicar_texturas_bolas(pasta_texturas):
    nomes_bolas = [f"ball{i}" for i in range(1, 16)] + ["ballcue"]
    
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


def criar_suportes():
    mesa_comprimento = 4.0
    mesa_largura = 2.0
    mesa_altura_total = 1
    mesa_espessura = 0.05
    base_espessura = 0.3
    perna_raio = 0.12
    perna_altura = mesa_altura_total - mesa_espessura - base_espessura
    afastamento_y = 0.1  # Aumente este valor para afastar mais as pernas em y
    posicoes_pernas = [
        (mesa_comprimento / 2 - 0.2, mesa_largura / 2 - afastamento_y, perna_altura / 2),
        (-mesa_comprimento / 2 + 0.2, mesa_largura / 2 - afastamento_y, perna_altura / 2),
        (mesa_comprimento / 2 - 0.2, -mesa_largura / 2 + afastamento_y, perna_altura / 2),
        (-mesa_comprimento / 2 + 0.2, -mesa_largura / 2 + afastamento_y, perna_altura / 2),
    ]
    for i, pos in enumerate(posicoes_pernas):
        bpy.ops.mesh.primitive_cylinder_add(radius=perna_raio, depth=perna_altura, location=pos)
        perna = bpy.context.object
        perna.name = f"Perna_{i}"
        mat_perna = bpy.data.materials.new(name="Material_Perna")
        mat_perna.diffuse_color = (0.2, 0.1, 0.0, 1.0)
        perna.data.materials.append(mat_perna)

    borda = bpy.data.objects["Borda"]  

    # Adiciona o modificador Bevel
    mod_bevel = borda.modifiers.new(name="Bevel", type='BEVEL')
    mod_bevel.width = 0.35       # Aumente para arredondamento mais intenso (ex: 0.25 a 0.5)
    mod_bevel.segments = 24      # Mais segmentos = mais suave e arredondado
    mod_bevel.limit_method = 'ANGLE' # Só aplica em ângulos agudos (padrão para cantos)
    mod_bevel.angle_limit = math.radians(30)  # Limite de ângulo para o bevel

    # (Opcional) Aplicar o modificador para tornar o bevel permanente
    bpy.context.view_layer.objects.active = borda
    bpy.ops.object.modifier_apply(modifier=mod_bevel.name)
    # Se ainda não ficar arredondado o suficiente, aumente ainda mais o width ou crie a moldura a partir de uma curva com raio nos cantos.

def criar_caixa_coletora():
    # Parâmetros da mesa
    mesa_largura = 2.0
    mesa_comprimento = 4.0
    mesa_altura_total = 1.0
    mesa_espessura = 0.05
    base_espessura = 0.45
    
    # Parâmetros da caixa coletora
    caixa_largura = 1.0       # Maior na largura
    caixa_altura = 0.25       # Mais alta
    caixa_profundidade = 0.3  # Suficientemente profunda
    
    # Posição: do lado da base, centralizada no eixo X
    caixa_x = 0
    caixa_y = -(mesa_largura/2 + caixa_profundidade/2 - 0.01)
    caixa_z = (mesa_altura_total - mesa_espessura - base_espessura) + caixa_altura/2
    
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=(caixa_x, caixa_y, caixa_z)
    )
    caixa = bpy.context.object
    caixa.name = "Caixa_Coletora"
    caixa.scale = (caixa_largura/2, caixa_profundidade/2, caixa_altura/2)
    
    # Material
    mat_caixa = bpy.data.materials.new(name="Material_Caixa_Coletora")
    mat_caixa.diffuse_color = (0.3, 0.15, 0.05, 1.0)
    caixa.data.materials.append(mat_caixa)

def criar_mesa_de_sinuca():
    mesa_largura = 2.0
    mesa_comprimento = 4.0
    mesa_altura_total = 1
    mesa_espessura = 0.05
    borda_altura = 0.1
    borda_espessura = 0.25
    base_espessura = 0.45
    base_scale_reduction = 1.10  # Fator de redução original

    # Tampo da mesa (feltro)
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
    
    # Criar um cubo interno para cortar o centro
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, mesa_altura_total))
    corte = bpy.context.object
    corte.scale = (mesa_comprimento, mesa_largura, borda_altura + 0.01)
    
    # Aplicar operação booleana para criar a moldura
    mod = borda.modifiers.new(name="Boolean", type="BOOLEAN")
    mod.operation = 'DIFFERENCE'
    mod.object = corte
    bpy.context.view_layer.objects.active = borda
    bpy.ops.object.modifier_apply(modifier="Boolean")
    bpy.data.objects.remove(corte)

    # Base da mesa 
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, mesa_altura_total - mesa_espessura - base_espessura / 2))
    base = bpy.context.object
    base.scale = (4.2, mesa_largura * base_scale_reduction, base_espessura)
    base.name = "Base_Mesa"
    mat_base = bpy.data.materials.new(name="Material_Base")
    mat_base.diffuse_color = (0.2, 0.1, 0.0, 1.0)
    base.data.materials.append(mat_base)
    

limpar_cena()
criar_mesa_de_sinuca()
criar_cacapas()
criar_bolas()
aplicar_texturas_bolas(r'D:\mesadebilhar\Blender-modelagem\assets\Pool Ball Skins')
criar_suportes()
criar_caixa_coletora()