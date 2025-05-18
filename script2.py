import bpy
import math

def limpar_cena():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

def criar_mesa_de_sinuca():
    mesa_largura = 2.0
    mesa_comprimento = 4.0
    mesa_altura_total = 0.8
    mesa_espessura = 0.05
    borda_altura = 0.1
    borda_espessura = 0.2

    # Tampo da mesa
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, mesa_altura_total - mesa_espessura / 2))
    mesa = bpy.context.object
    mesa.scale = (mesa_comprimento, mesa_largura, mesa_espessura)
    mesa.name = "Mesa_Base"
    mat_mesa = bpy.data.materials.new(name="Material_Mesa")
    mat_mesa.diffuse_color = (0.0, 0.3, 0.0, 1.0)
    mesa.data.materials.append(mat_mesa)

    # Bordas
    posicoes_bordas = [
        ((mesa_comprimento / 2 + borda_espessura / 2, 0, mesa_altura_total), (borda_espessura, mesa_largura + 2 * borda_espessura, borda_altura)),
        ((-mesa_comprimento / 2 - borda_espessura / 2, 0, mesa_altura_total), (borda_espessura, mesa_largura + 2 * borda_espessura, borda_altura)),
        ((0, mesa_largura / 2 + borda_espessura / 2, mesa_altura_total), (mesa_comprimento + 2 * borda_espessura, borda_espessura, borda_altura)),
        ((0, -mesa_largura / 2 - borda_espessura / 2, mesa_altura_total), (mesa_comprimento + 2 * borda_espessura, borda_espessura, borda_altura)),
    ]
    for i, (pos, escala) in enumerate(posicoes_bordas):
        bpy.ops.mesh.primitive_cube_add(size=1, location=pos)
        borda = bpy.context.object
        borda.scale = escala
        borda.name = f"Borda_{i}"
        mat_borda = bpy.data.materials.new(name="Material_Borda")
        mat_borda.diffuse_color = (0.4, 0.2, 0.0, 1.0)
        borda.data.materials.append(mat_borda)

def criar_cacapas():
    cacapa_raio = 0.1
    mesa_comprimento = 4.0
    mesa_largura = 2.0
    mesa_altura_total = 0.8
    posicoes_cacapas = [
        (mesa_comprimento / 2, mesa_largura / 2, mesa_altura_total),
        (-mesa_comprimento / 2, mesa_largura / 2, mesa_altura_total),
        (mesa_comprimento / 2, -mesa_largura / 2, mesa_altura_total),
        (-mesa_comprimento / 2, -mesa_largura / 2, mesa_altura_total),
        (0, mesa_largura / 2, mesa_altura_total),
        (0, -mesa_largura / 2, mesa_altura_total),
    ]
    for i, pos in enumerate(posicoes_cacapas):
        bpy.ops.mesh.primitive_cylinder_add(radius=cacapa_raio, depth=0.1, location=pos)
        cacapa = bpy.context.object
        cacapa.name = f"Cacapa_{i}"
        mat_cacapa = bpy.data.materials.new(name="Material_Cacapa")
        mat_cacapa.diffuse_color = (0.0, 0.0, 0.0, 1.0)
        cacapa.data.materials.append(mat_cacapa)

def criar_bolas():
    bola_raio = 0.057
    mesa_altura_total = 0.8
    for i in range(5):
        for j in range(i + 1):
            x = i * bola_raio * 2.0
            y = (j - i / 2) * bola_raio * 2.0
            z = mesa_altura_total + bola_raio
            bpy.ops.mesh.primitive_uv_sphere_add(radius=bola_raio, location=(x - 0.5, y, z))
            bola = bpy.context.object
            bola.name = f"Bola_{i}_{j}"
            mat_bola = bpy.data.materials.new(name=f"Material_Bola_{i}_{j}")
            mat_bola.diffuse_color = (i / 5.0, j / 5.0, 1.0 - i / 5.0, 1.0)
            bola.data.materials.append(mat_bola)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=bola_raio, location=(-1.5, 0, mesa_altura_total + bola_raio))
    bola_branca = bpy.context.object
    bola_branca.name = "Bola_Branca"
    mat_branca = bpy.data.materials.new(name="Material_Bola_Branca")
    mat_branca.diffuse_color = (1.0, 1.0, 1.0, 1.0)
    bola_branca.data.materials.append(mat_branca)

def criar_suportes():
    mesa_comprimento = 4.0
    mesa_largura = 2.0
    mesa_altura_total = 0.8
    mesa_espessura = 0.05
    perna_raio = 0.1
    perna_altura = mesa_altura_total - mesa_espessura / 2
    posicoes_pernas = [
        (mesa_comprimento / 2 - 0.1, mesa_largura / 2 - 0.1, perna_altura / 2),
        (-mesa_comprimento / 2 + 0.1, mesa_largura / 2 - 0.1, perna_altura / 2),
        (mesa_comprimento / 2 - 0.1, -mesa_largura / 2 + 0.1, perna_altura / 2),
        (-mesa_comprimento / 2 + 0.1, -mesa_largura / 2 + 0.1, perna_altura / 2),
    ]
    for i, pos in enumerate(posicoes_pernas):
        bpy.ops.mesh.primitive_cylinder_add(radius=perna_raio, depth=perna_altura, location=pos)
        perna = bpy.context.object
        perna.name = f"Perna_{i}"
        mat_perna = bpy.data.materials.new(name="Material_Perna")
        mat_perna.diffuse_color = (0.2, 0.1, 0.0, 1.0)
        perna.data.materials.append(mat_perna)

# Execução direta
limpar_cena()
criar_mesa_de_sinuca()
criar_cacapas()
criar_bolas()
criar_suportes()