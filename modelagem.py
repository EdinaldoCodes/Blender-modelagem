import bpy
import math


# --- Funções Auxiliares ---
def limpar_cena():
    """Limpa todos os objetos da cena atual."""
    if bpy.context.object and bpy.context.object.mode == 'EDIT':
        bpy.ops.object.mode_set(mode='OBJECT')

    if bpy.ops.object.select_all.poll():
        bpy.ops.object.select_all(action='SELECT')
    if bpy.ops.object.delete.poll():
        bpy.ops.object.delete(use_global=False)

    # Limpar materiais não utilizados também (opcional, mas bom para desenvolvimento)
    for material in bpy.data.materials:
        if not material.users:
            bpy.data.materials.remove(material)
    for mesh in bpy.data.meshes:
        if not mesh.users:
            bpy.data.meshes.remove(mesh)
    for collection in bpy.data.collections:  # Limpa coleções vazias se necessário
        if not collection.objects and not collection.children:
            # Cuidado ao remover coleções, especialmente a padrão
            pass


def criar_objeto_pai(nome, localizacao_global):
    """Cria um objeto Empty para servir como pai."""
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=localizacao_global)
    pai = bpy.context.object
    pai.name = nome
    return pai


def definir_pai(objeto, pai):
    """Define o parentesco de um objeto."""
    if objeto and pai:
        objeto.parent = pai
        objeto.matrix_parent_inverse = pai.matrix_world.inverted()


# --- Funções de Criação de Componentes da Mesa ---

def criar_base_mesa(comprimento_base, largura_base, altura_base, z_centro_base, nome_objeto, pai):
    """Cria a base (caixa) da mesa de sinuca."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, z_centro_base))
    base = bpy.context.object
    base.name = nome_objeto
    base.scale = (comprimento_base / 2, largura_base / 2, altura_base / 1.1)
    definir_pai(base, pai)
    return base


def criar_superficie_jogo(comprimento_jogo, largura_jogo, z_superficie, nome_objeto, pai):
    """Cria a superfície de jogo (feltro) da mesa de sinuca."""
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, z_superficie))
    feltro = bpy.context.object
    feltro.name = nome_objeto
    feltro.scale = (comprimento_jogo / 1, largura_jogo / 1, 1)
    definir_pai(feltro, pai)
    return feltro


def criar_pernas_mesa(comprimento_total_estrutura, largura_total_estrutura,
                      diametro_perna, altura_perna_real,
                      z_topo_perna,
                      afastamento_x_ratio, afastamento_y_ratio,
                      nome_base_objeto, pai):
    """Cria as pernas da mesa de sinuca."""
    z_centro_perna = z_topo_perna - (altura_perna_real / 2.5)
    raio_perna = diametro_perna / 2
    offset_x = (comprimento_total_estrutura / 2 - raio_perna) * afastamento_x_ratio
    offset_y = (largura_total_estrutura / 2 - raio_perna) * afastamento_y_ratio

    localizacoes_pernas_relativas = [
        (offset_x, offset_y, z_centro_perna),
        (-offset_x, offset_y, z_centro_perna),
        (offset_x, -offset_y, z_centro_perna),
        (-offset_x, -offset_y, z_centro_perna),
    ]

    pernas_criadas = []
    for i, loc_rel in enumerate(localizacoes_pernas_relativas):
        bpy.ops.mesh.primitive_cylinder_add(
            radius=raio_perna,
            depth=altura_perna_real,
            location=loc_rel,
            vertices=16
        )
        perna = bpy.context.object
        perna.name = f"{nome_base_objeto}_{i + 1}"
        definir_pai(perna, pai)
        pernas_criadas.append(perna)
    return pernas_criadas


def criar_bordas_retangulares_mesa(comprimento_area_jogo, largura_area_jogo,
                                   largura_borda, espessura_borda,
                                   distancia_borda_do_feltro,
                                   z_centro_borda, nome_base_objeto, pai):
    """Cria as 4 bordas retangulares (tabelas) da mesa."""
    bordas_criadas = []

    pos_y_centro_borda_longa = largura_area_jogo / 2 + distancia_borda_do_feltro + largura_borda / 2

    loc_tabela_sup = (0, pos_y_centro_borda_longa, z_centro_borda)
    bpy.ops.mesh.primitive_cube_add(location=loc_tabela_sup)
    t_sup = bpy.context.object
    t_sup.name = f"{nome_base_objeto}_Superior"
    t_sup.scale = (comprimento_area_jogo / 2, largura_borda / 2, espessura_borda / 2)
    definir_pai(t_sup, pai)
    bordas_criadas.append(t_sup)

    loc_tabela_inf = (0, -pos_y_centro_borda_longa, z_centro_borda)
    bpy.ops.mesh.primitive_cube_add(location=loc_tabela_inf)
    t_inf = bpy.context.object
    t_inf.name = f"{nome_base_objeto}_Inferior"
    t_inf.scale = (comprimento_area_jogo / 2, largura_borda / 2, espessura_borda / 2)
    definir_pai(t_inf, pai)
    bordas_criadas.append(t_inf)

    pos_x_centro_borda_curta = comprimento_area_jogo / 2 + distancia_borda_do_feltro + largura_borda / 2
    comprimento_y_borda_curta = largura_area_jogo + (2 * distancia_borda_do_feltro) + (2 * largura_borda)

    loc_tabela_dir = (pos_x_centro_borda_curta, 0, z_centro_borda)
    bpy.ops.mesh.primitive_cube_add(location=loc_tabela_dir)
    t_dir = bpy.context.object
    t_dir.name = f"{nome_base_objeto}_Direita"
    t_dir.scale = (largura_borda / 2, comprimento_y_borda_curta / 2, espessura_borda / 2)
    definir_pai(t_dir, pai)
    bordas_criadas.append(t_dir)

    loc_tabela_esq = (-pos_x_centro_borda_curta, 0, z_centro_borda)
    bpy.ops.mesh.primitive_cube_add(location=loc_tabela_esq)
    t_esq = bpy.context.object
    t_esq.name = f"{nome_base_objeto}_Esquerda"
    t_esq.scale = (largura_borda / 2, comprimento_y_borda_curta / 2, espessura_borda / 2)
    definir_pai(t_esq, pai)
    bordas_criadas.append(t_esq)
    return bordas_criadas


def criar_bolsos_mesa(comprimento_jogo, largura_jogo,
                      distancia_borda_do_feltro,  # NOVO PARÂMETRO para posicionar bolsos
                      z_pos_bolso, raio_bolso_visual,
                      nome_base_objeto, pai):
    """Cria os bolsos da mesa de sinuca (apenas visual), coordenados com as tabelas."""

    # Calcula as posições X e Y para as bordas internas das tabelas (onde os bolsos devem estar)
    x_borda_interna_bolso = comprimento_jogo / 2 + distancia_borda_do_feltro
    y_borda_interna_bolso = largura_jogo / 2 + distancia_borda_do_feltro

    localizacoes_bolsos_relativas = [
        (x_borda_interna_bolso, y_borda_interna_bolso, z_pos_bolso),  # Canto superior direito
        (-x_borda_interna_bolso, y_borda_interna_bolso, z_pos_bolso),  # Canto superior esquerdo
        (x_borda_interna_bolso, -y_borda_interna_bolso, z_pos_bolso),  # Canto inferior direito
        (-x_borda_interna_bolso, -y_borda_interna_bolso, z_pos_bolso),  # Canto inferior esquerdo
        (0, y_borda_interna_bolso, z_pos_bolso),  # Meio superior
        (0, -y_borda_interna_bolso, z_pos_bolso),  # Meio inferior
    ]
    bolsos_criados = []
    for i, loc_rel in enumerate(localizacoes_bolsos_relativas):
        bpy.ops.mesh.primitive_cylinder_add(
            radius=raio_bolso_visual,
            depth=0.05,
            location=loc_rel,
            vertices=16
        )
        bolso = bpy.context.object
        bolso.name = f"{nome_base_objeto}_{i + 1}"
        definir_pai(bolso, pai)
        bolsos_criados.append(bolso)
    return bolsos_criados


def adicionar_materiais_mesa(objetos_da_mesa):
    """Adiciona materiais básicos aos objetos da mesa de sinuca."""
    feltro_mat = bpy.data.materials.new(name="FeltroVerde")
    feltro_mat.diffuse_color = (0.1, 0.5, 0.1, 1.0)
    if "feltro" in objetos_da_mesa and objetos_da_mesa["feltro"]:
        objetos_da_mesa["feltro"].data.materials.append(feltro_mat)

    madeira_mat = bpy.data.materials.new(name="MadeiraMarrom")
    madeira_mat.diffuse_color = (0.3, 0.15, 0.05, 1.0)

    componentes_madeira = []
    if "base" in objetos_da_mesa and objetos_da_mesa["base"]:
        componentes_madeira.append(objetos_da_mesa["base"])
    if "pernas" in objetos_da_mesa:
        componentes_madeira.extend(objetos_da_mesa["pernas"])
    if "bordas" in objetos_da_mesa:
        componentes_madeira.extend(objetos_da_mesa["bordas"])

    for obj in componentes_madeira:
        if obj and obj.data:
            if not obj.data.materials:
                obj.data.materials.append(madeira_mat)
            else:
                obj.data.materials[0] = madeira_mat

    bolso_mat = bpy.data.materials.new(name="BolsoPreto")
    bolso_mat.diffuse_color = (0.02, 0.02, 0.02, 1.0)
    if "bolsos" in objetos_da_mesa:
        for bolso_obj in objetos_da_mesa["bolsos"]:
            if bolso_obj and bolso_obj.data:
                if not bolso_obj.data.materials:
                    bolso_obj.data.materials.append(bolso_mat)
                else:
                    bolso_obj.data.materials[0] = bolso_mat


def criar_bolas_sinuca(raio_bola, num_bolas_total, z_centro_bolas, nome_base_objeto, pai):
    """Cria as bolas de sinuca com cores básicas."""
    cores_base = [
        (1.0, 1.0, 1.0, 1.0), (1.0, 1.0, 0.0, 1.0), (0.0, 0.0, 1.0, 1.0),
        (1.0, 0.0, 0.0, 1.0), (0.5, 0.0, 0.5, 1.0), (1.0, 0.4, 0.0, 1.0),
        (0.0, 0.5, 0.0, 1.0), (0.3, 0.1, 0.1, 1.0), (0.05, 0.05, 0.05, 1.0),
    ]
    nomes_cores = ["Branca", "Amarela", "Azul", "Vermelha", "Roxa", "Laranja", "Verde", "Marrom", "Preta"]
    bolas_criadas = []

    bpy.ops.mesh.primitive_uv_sphere_add(radius=raio_bola, location=(0, 0, z_centro_bolas), segments=16, ring_count=8)
    bola_branca = bpy.context.object
    bola_branca.name = f"{nome_base_objeto}_0_Branca"
    mat_branca = bpy.data.materials.new(name="CorBola_Branca")
    mat_branca.diffuse_color = cores_base[0]
    bola_branca.data.materials.append(mat_branca)
    bpy.ops.object.shade_smooth()
    definir_pai(bola_branca, pai)
    bolas_criadas.append(bola_branca)

    for i in range(1, num_bolas_total):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=raio_bola, location=(raio_bola * 2.5 * i, 0, z_centro_bolas),
                                             segments=16, ring_count=8)
        bola = bpy.context.object
        mat_bola = bpy.data.materials.new(name=f"CorBola_{i}")
        nome_cor_atual = ""
        if i <= 8:
            if i == 8:
                mat_bola.diffuse_color = cores_base[8]
                nome_cor_atual = nomes_cores[8]
            else:
                mat_bola.diffuse_color = cores_base[i]
                nome_cor_atual = nomes_cores[i]
        else:
            cor_idx_repetida = i - 8
            mat_bola.diffuse_color = cores_base[cor_idx_repetida]
            nome_cor_atual = f"{nomes_cores[cor_idx_repetida]}_Listrada"

        bola.name = f"{nome_base_objeto}_{i}_{nome_cor_atual}"
        bola.data.materials.append(mat_bola)
        bpy.ops.object.shade_smooth()
        definir_pai(bola, pai)
        bolas_criadas.append(bola)
    return bolas_criadas


def posicionar_bolas_rack(bolas, z_centro_bolas, raio_bola, comprimento_area_jogo):
    """Posiciona as bolas em formato de triângulo na mesa."""
    if not bolas or len(bolas) < 16:
        print("Número insuficiente de bolas para formar o rack.")
        return

    bolas[0].location = (-comprimento_area_jogo / 4, 0, z_centro_bolas)
    apex_x = comprimento_area_jogo / 4
    apex_y = 0
    diametro_bola = raio_bola * 2
    squeeze_factor = 0.995
    dy_entre_bolas = diametro_bola * squeeze_factor
    dx_entre_linhas = diametro_bola * math.sqrt(3) / 2 * squeeze_factor
    ball_rack_idx_original = 1
    num_rows_triangle = 5

    if ball_rack_idx_original < len(bolas):
        bolas[ball_rack_idx_original].location = (apex_x, apex_y, z_centro_bolas)
        ball_rack_idx_original += 1

    for r in range(1, num_rows_triangle):
        num_balls_in_row = r + 1
        current_row_x = apex_x + r * dx_entre_linhas
        start_y_for_row = apex_y - (r / 2.0) * dy_entre_bolas
        for c in range(num_balls_in_row):
            if ball_rack_idx_original >= len(bolas): break
            current_ball_y = start_y_for_row + c * dy_entre_bolas
            bolas[ball_rack_idx_original].location = (current_row_x, current_ball_y, z_centro_bolas)
            bpy.context.view_layer.update()
            ball_rack_idx_original += 1
        if ball_rack_idx_original >= len(bolas): break


# --- Função Principal de Criação da Mesa ---

def criar_mesa_sinuca_completa(
        posicao_mesa_global_xyz=(0, 0, 0.77),
        comprimento_total_estrutura=2.54,
        largura_total_estrutura=1.42,
        altura_base_estrutura=0.15,
        altura_pernas_chao_a_base=0.62,
        diametro_perna=0.1,
        afastamento_pernas_x_ratio=0.85,
        afastamento_pernas_y_ratio=0.85,
        comprimento_area_jogo=2.2352,
        largura_area_jogo=1.1176,
        largura_borda_visual=0.12,
        espessura_borda_visual=0.04,
        distancia_borda_do_feltro=0.0,
        diametro_bolso_canto_visual=0.115,
        raio_bola_padrao=0.028575,
        organizar_bolas_no_rack=True,
        numero_total_de_bolas=16
):
    """Cria a mesa de sinuca completa com todos os componentes e parâmetros ajustáveis."""
    limpar_cena()
    mesa_pai = criar_objeto_pai(
        "MesaSinuca_Raiz",
        (posicao_mesa_global_xyz[0], posicao_mesa_global_xyz[1], 0)
    )
    z_ref_feltro = posicao_mesa_global_xyz[2]
    objetos_criados = {"pernas": [], "bordas": [], "bolsos": [], "bolas": []}

    z_centro_base_mesa = z_ref_feltro - (altura_base_estrutura / 2)
    objetos_criados["base"] = criar_base_mesa(
        comprimento_total_estrutura, largura_total_estrutura, altura_base_estrutura,
        z_centro_base_mesa, "Mesa_BaseEstrutura", mesa_pai
    )
    objetos_criados["feltro"] = criar_superficie_jogo(
        comprimento_area_jogo, largura_area_jogo,
        z_ref_feltro, "Mesa_Feltro", mesa_pai
    )
    z_topo_pernas = z_ref_feltro - altura_base_estrutura
    objetos_criados["pernas"] = criar_pernas_mesa(
        comprimento_total_estrutura, largura_total_estrutura,
        diametro_perna, altura_pernas_chao_a_base,
        z_topo_pernas, afastamento_pernas_x_ratio, afastamento_pernas_y_ratio,
        "Mesa_Perna", mesa_pai
    )
    z_centro_bordas = z_ref_feltro + (espessura_borda_visual / 2)
    objetos_criados["bordas"] = criar_bordas_retangulares_mesa(
        comprimento_area_jogo, largura_area_jogo,
        largura_borda_visual, espessura_borda_visual,
        distancia_borda_do_feltro,
        z_centro_bordas, "Mesa_Borda", mesa_pai
    )
    z_centro_bolsos = z_ref_feltro
    raio_bolso_visual = diametro_bolso_canto_visual / 2
    objetos_criados["bolsos"] = criar_bolsos_mesa(
        comprimento_area_jogo, largura_area_jogo,
        distancia_borda_do_feltro,  # Passando o parâmetro para coordenar os bolsos
        z_centro_bolsos, raio_bolso_visual, "Mesa_Bolso", mesa_pai
    )
    adicionar_materiais_mesa(objetos_criados)
    z_centro_bolas = z_ref_feltro + raio_bola_padrao
    objetos_criados["bolas"] = criar_bolas_sinuca(
        raio_bola_padrao, numero_total_de_bolas,
        z_centro_bolas, "BolaSinuca", mesa_pai
    )
    if organizar_bolas_no_rack:
        posicionar_bolas_rack(
            objetos_criados["bolas"], z_centro_bolas,
            raio_bola_padrao, comprimento_area_jogo
        )
    print(f"Mesa de sinuca criada com raiz em '{mesa_pai.name}'. Feltro a Z={z_ref_feltro:.3f} global.")


# --- Execução Principal ---
if __name__ == "__main__":
    pos_mesa_x = 0.0
    pos_mesa_y = 0.0
    altura_feltro_do_chao = 0.77
    comp_total_estrutura_mesa = 2.54
    larg_total_estrutura_mesa = 1.42
    alt_caixa_base_mesa = 0.20
    alt_pernas = altura_feltro_do_chao - alt_caixa_base_mesa
    diam_perna = 0.12
    afast_pernas_x = 0.4
    afast_pernas_y = 0.4
    comp_area_jogo_feltro = 1.2
    larg_area_jogo_feltro = 0.7

    larg_borda_madeira = 0.10
    alt_borda_madeira = 0.045
    # AJUSTE AQUI para aproximar as tabelas e bolsos:
    dist_borda_feltro = 0.005  # Ex: 0.5 cm de distância. Use 0.0 para encostar.

    diam_bolso_canto = 0.118
    raio_bola = 0.028575

    criar_mesa_sinuca_completa(
        posicao_mesa_global_xyz=(pos_mesa_x, pos_mesa_y, altura_feltro_do_chao),
        comprimento_total_estrutura=comp_total_estrutura_mesa,
        largura_total_estrutura=larg_total_estrutura_mesa,
        altura_base_estrutura=alt_caixa_base_mesa,
        altura_pernas_chao_a_base=alt_pernas,
        diametro_perna=diam_perna,
        afastamento_pernas_x_ratio=afast_pernas_x,
        afastamento_pernas_y_ratio=afast_pernas_y,
        comprimento_area_jogo=comp_area_jogo_feltro,
        largura_area_jogo=larg_area_jogo_feltro,
        largura_borda_visual=larg_borda_madeira,
        espessura_borda_visual=alt_borda_madeira,
        distancia_borda_do_feltro=dist_borda_feltro,
        diametro_bolso_canto_visual=diam_bolso_canto,
        raio_bola_padrao=raio_bola,
        organizar_bolas_no_rack=True,
        numero_total_de_bolas=16
    )
