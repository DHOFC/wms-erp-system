import flet as ft
import requests
import os 
import threading 
import time

API_BASE_URL = "https://wms-erp-system.onrender.com"
HEADERS_SEGUROS = {"X-API-Key": "wms-secreto-2024"}

def main(page: ft.Page):
    # 1. CONFIGURAÇÕES DA JANELA E TEMA CORPORATIVO
    page.title = "WMS Enterprise - Dashboard"
    page.theme_mode = ft.ThemeMode.DARK
    page.window.width = 1000
    page.window.height = 750
    page.padding = 0 

    texto_notificacao = ft.Text(value="", size=14, weight=ft.FontWeight.BOLD)

    def mostrar_notificacao(mensagem, cor):
        texto_notificacao.value = mensagem
        texto_notificacao.color = cor
        page.update()

    # VARIÁVEIS GLOBAIS DE DADOS
    dados_produtos = []
    dados_locais = []
    dados_movimentacoes = []

    # TELA 0: HOME / DASHBOARD (ESTILO ECHARTS / BUSINESS)
    kpi_skus = ft.Text("0", size=28, weight="bold")
    kpi_valor = ft.Text("$ 0.00", size=28, weight="bold")
    kpi_locais = ft.Text("0", size=28, weight="bold")
    kpi_ops = ft.Text("0", size=28, weight="bold") 
    
    container_grafico_linha = ft.Container(height=300, padding=10)
    container_grafico_barra = ft.Container(height=300, padding=10)

    def criar_card_kpi(titulo, texto_valor, trend_text, trend_color, trend_icon):
        return ft.Card(
            elevation=2,
            content=ft.Container(
                padding=20,
                bgcolor="#2A2D32", # Cor hexadecimal segura (Surface Variant)
                border_radius=10,
                content=ft.Column([
                    ft.Text(titulo, size=14, color="#B0BEC5"), # Cor hexadecimal segura
                    texto_valor,
                    ft.Row([
                        ft.Icon(trend_icon, color=trend_color, size=16),
                        ft.Text(trend_text, color=trend_color, size=12, weight="bold")
                    ], spacing=2)
                ], spacing=5)
            ),
            expand=True
        )

    def atualizar_kpis():
        estoque_real = {}
        for mov in dados_movimentacoes:
            p_id = mov["product_id"]
            qtd = mov["quantity"]
            if mov["movement_type"] == "IN":
                estoque_real[p_id] = estoque_real.get(p_id, 0) + qtd
            else:
                estoque_real[p_id] = estoque_real.get(p_id, 0) - qtd

        total_skus = len(dados_produtos)
        total_locais = len(dados_locais)
        total_operacoes = len(dados_movimentacoes)
        
        valor_total = 0
        for p in dados_produtos:
            qtd_em_estoque = estoque_real.get(p["id"], 0)
            valor_total += float(p["price"]) * qtd_em_estoque
        
        kpi_skus.value = str(total_skus)
        kpi_valor.value = f"$ {valor_total:,.2f}"
        kpi_locais.value = str(total_locais)
        kpi_ops.value = str(total_operacoes) 
        
        if total_skus > 0:
            produtos_top = sorted(dados_produtos, key=lambda x: float(x["price"]) * estoque_real.get(x["id"], 0), reverse=True)[:5]
            
            barras = []
            rotulos_b = []
            for i, p in enumerate(produtos_top):
                valor_estocado = float(p["price"]) * estoque_real.get(p["id"], 0)
                barras.append(ft.BarChartGroup(x=i, bar_rods=[ft.BarChartRod(from_y=0, to_y=valor_estocado, color="green", width=20)]))
                rotulos_b.append(ft.ChartAxisLabel(value=i, label=ft.Text(p["sku"][:5], size=10)))
            
            container_grafico_barra.content = ft.BarChart(
                bar_groups=barras, bottom_axis=ft.ChartAxis(labels=rotulos_b),
                tooltip_bgcolor="#263238", border=ft.border.all(1, "grey"), expand=True
            )
            
            pontos_linha = [ft.LineChartDataPoint(i, float(p["price"])) for i, p in enumerate(dados_produtos[:10])]
            container_grafico_linha.content = ft.LineChart(
                data_series=[ft.LineChartData(data_points=pontos_linha, stroke_width=3, color="blue", curved=True, stroke_cap_round=True)],
                border=ft.border.all(1, "grey"), horizontal_grid_lines=ft.ChartGridLines(color="grey", width=1, dash_pattern=[3, 3]), tooltip_bgcolor="#263238", expand=True
            )
        else:
            container_grafico_barra.content = ft.Text("Sem dados suficientes.")
            container_grafico_linha.content = ft.Text("Sem dados suficientes.")
            
        page.update()

    def carregar_tudo_e_atualizar():
        nonlocal dados_produtos, dados_locais, dados_movimentacoes
        try:
            res_p = requests.get(f"{API_BASE_URL}/products/")
            res_l = requests.get(f"{API_BASE_URL}/locations/")
            res_m = requests.get(f"{API_BASE_URL}/movements/") 
            
            if res_p.status_code == 200: dados_produtos = res_p.json()
            if res_l.status_code == 200: dados_locais = res_l.json()
            if res_m.status_code == 200: dados_movimentacoes = res_m.json()
            
            atualizar_kpis()
        except Exception: pass

    linha_kpis = ft.Row([
        criar_card_kpi("Total Revenue (Valor em Estoque)", kpi_valor, "+ 12.5%", "green", "arrow_upward"),
        criar_card_kpi("Total SKUs (Catálogo)", kpi_skus, "+ 3.2%", "green", "arrow_upward"),
        criar_card_kpi("Capacidade (Prateleiras)", kpi_locais, "Estável", "grey", "remove"),
        criar_card_kpi("Operações Totais", kpi_ops, "- 1.5%", "red", "arrow_downward"),
    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

    tela_home = ft.Column([
        ft.Text("Executive Dashboard", size=28, weight=ft.FontWeight.BOLD),
        ft.Text("Resumo financeiro e operacional do armazém", color="grey"),
        ft.Divider(height=20, color="transparent"),
        
        linha_kpis,
        
        ft.Divider(height=30, color="transparent"),
        
        ft.Text("Evolução de Ativos & Concentração", size=20, weight="bold"),
        ft.Row([
            ft.Card(
                content=ft.Container(
                    content=ft.Column([ft.Text("Crescimento de Catálogo", weight="bold"), container_grafico_linha]), 
                    padding=15
                ), expand=2
            ),
            ft.Card(
                content=ft.Container(
                    content=ft.Column([ft.Text("Top 5 Concentração de Valor", weight="bold"), container_grafico_barra]), 
                    padding=15
                ), expand=1
            ),
        ], alignment=ft.MainAxisAlignment.START)
        
    ], expand=True, scroll=ft.ScrollMode.AUTO) 


    # TELA 1: TERMINAL DE OPERAÇÃO
    campo_produto_op = ft.TextField(label="ID do Produto", width=300)
    campo_local_op = ft.TextField(label="ID da Prateleira", width=300)
    campo_qtd_op = ft.TextField(label="Quantidade", width=300, keyboard_type=ft.KeyboardType.NUMBER)
    campo_tipo_op = ft.Dropdown(
        label="Tipo de Movimentação", width=300,
        options=[ft.dropdown.Option("IN", "ENTRADA"), ft.dropdown.Option("OUT", "SAÍDA")]
    )

    def enviar_movimentacao(e):
        mostrar_notificacao("Processando...", "yellow")
        if not campo_produto_op.value or not campo_local_op.value or not campo_qtd_op.value or not campo_tipo_op.value:
            mostrar_notificacao("❌ Preencha todos os campos!", "red")
            return

        payload = {
            "product_id": int(campo_produto_op.value),
            "location_id": int(campo_local_op.value),
            "quantity": int(campo_qtd_op.value),
            "movement_type": campo_tipo_op.value
        }
        try:
            resposta = requests.post(f"{API_BASE_URL}/movements/", json=payload, headers=HEADERS_SEGUROS)
            if resposta.status_code == 201:
                mostrar_notificacao("✅ Movimentação registrada!", "green")
                campo_qtd_op.value = ""
                carregar_tudo_e_atualizar() 
            else:
                mostrar_notificacao(f"❌ Negado: {resposta.json().get('detail')}", "red")
        except Exception:
            mostrar_notificacao("❌ Falha de Conexão.", "red")
        page.update()

    tela_terminal = ft.Column([
        ft.Text("Terminal da Empilhadeira", size=28, weight=ft.FontWeight.BOLD, color="blue"),
        ft.Divider(color="transparent", height=20),
        campo_produto_op, campo_local_op, campo_qtd_op, campo_tipo_op,
        ft.ElevatedButton("Confirmar Movimentação", icon="check_circle", bgcolor="blue", color="white", on_click=enviar_movimentacao)
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True)

    # TELA 2: GESTÃO DE PRODUTOS
    tabela_produtos = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID")), ft.DataColumn(ft.Text("SKU")),
            ft.DataColumn(ft.Text("Nome do Produto")), ft.DataColumn(ft.Text("Preço")), ft.DataColumn(ft.Text("Ações"))
        ], rows=[]
    )

    def renderizar_produtos(lista):
        tabela_produtos.rows.clear()
        for p in lista:
            tabela_produtos.rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(str(p["id"]))), ft.DataCell(ft.Text(p["sku"])),
                ft.DataCell(ft.Text(p["name"])), ft.DataCell(ft.Text(f"R$ {p['price']:.2f}")),
                ft.DataCell(ft.IconButton(icon="delete", icon_color="red", on_click=lambda e, s=p["sku"]: confirmar_excluir_produto(s))),
            ]))
        page.update()

    def filtrar_produtos(e):
        termo = campo_pesq_prod.value.lower()
        if not termo: renderizar_produtos(dados_produtos)
        else: renderizar_produtos([p for p in dados_produtos if termo in p["name"].lower() or termo in p["sku"].lower()])

    campo_pesq_prod = ft.TextField(label="🔍 Pesquisar Produto...", width=400, on_change=filtrar_produtos)

    def carregar_produtos(e=None):
        carregar_tudo_e_atualizar()
        filtrar_produtos(None)

    def confirmar_excluir_produto(sku):
        def fechar(e): pop_up.open = False; page.update()
        def deletar(e):
            fechar(None)
            requests.delete(f"{API_BASE_URL}/products/{sku}", headers=HEADERS_SEGUROS)
            carregar_produtos()
            mostrar_notificacao(f"✅ SKU {sku} excluído!", "green")
        pop_up = ft.AlertDialog(title=ft.Text("Excluir Produto"), content=ft.Text(f"Deletar '{sku}'?"), actions=[ft.TextButton("Cancelar", on_click=fechar), ft.ElevatedButton("Excluir", bgcolor="red", color="white", on_click=deletar)])
        page.dialog = pop_up; pop_up.open = True; page.update()

    tela_produtos = ft.Column([
        ft.Text("Estoque de Produtos", size=28, weight=ft.FontWeight.BOLD, color="blue"),
        ft.Row([campo_pesq_prod, ft.IconButton(icon="refresh", on_click=carregar_produtos)]),
        ft.Column([tabela_produtos], scroll=ft.ScrollMode.AUTO, expand=True)
    ], expand=True)

    # TELA 3: GESTÃO DE PRATELEIRAS
    tabela_locais = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID")), ft.DataColumn(ft.Text("Código")),
            ft.DataColumn(ft.Text("Descrição")), ft.DataColumn(ft.Text("Ações"))
        ], rows=[]
    )

    def renderizar_locais(lista):
        tabela_locais.rows.clear()
        for l in lista:
            tabela_locais.rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(str(l["id"]))), ft.DataCell(ft.Text(l["code"])), ft.DataCell(ft.Text(l["description"])),
                ft.DataCell(ft.IconButton(icon="delete", icon_color="red", on_click=lambda e, lid=l["id"], cod=l["code"]: confirmar_excluir_local(lid, cod))),
            ]))
        page.update()

    def filtrar_locais(e):
        termo = campo_pesq_locais.value.lower()
        if not termo: renderizar_locais(dados_locais)
        else: renderizar_locais([l for l in dados_locais if termo in l["code"].lower() or termo in l["description"].lower()])

    campo_pesq_locais = ft.TextField(label="🔍 Pesquisar Prateleira...", width=400, on_change=filtrar_locais)

    def carregar_locais(e=None):
        carregar_tudo_e_atualizar()
        filtrar_locais(None)

    def confirmar_excluir_local(lid, cod):
        def fechar(e): pop_up.open = False; page.update()
        def deletar(e):
            fechar(None)
            requests.delete(f"{API_BASE_URL}/locations/{lid}", headers=HEADERS_SEGUROS)
            carregar_locais()
            mostrar_notificacao(f"✅ Prateleira {cod} excluída!", "green")
        pop_up = ft.AlertDialog(title=ft.Text("Excluir Prateleira"), content=ft.Text(f"Deletar '{cod}'?"), actions=[ft.TextButton("Cancelar", on_click=fechar), ft.ElevatedButton("Excluir", bgcolor="red", color="white", on_click=deletar)])
        page.dialog = pop_up; pop_up.open = True; page.update()

    tela_prateleiras = ft.Column([
        ft.Text("Mapa de Prateleiras", size=28, weight=ft.FontWeight.BOLD, color="orange"),
        ft.Row([campo_pesq_locais, ft.IconButton(icon="refresh", on_click=carregar_locais)]),
        ft.Column([tabela_locais], scroll=ft.ScrollMode.AUTO, expand=True)
    ], expand=True)

    # TELA 4: CADASTROS
    c_nome = ft.TextField(label="Nome", width=250); c_sku = ft.TextField(label="SKU", width=250)
    c_desc = ft.TextField(label="Descrição", width=250); c_preco = ft.TextField(label="Preço", width=250)
    
    def salvar_produto(e):
        try:
            req = requests.post(f"{API_BASE_URL}/products/", json={"name": c_nome.value, "sku": c_sku.value, "description": c_desc.value, "price": float(c_preco.value.replace(",","."))}, headers=HEADERS_SEGUROS)
            if req.status_code == 201: 
                mostrar_notificacao("✅ Produto cadastrado!", "green")
                carregar_produtos()
        except Exception: mostrar_notificacao("❌ Erro ao salvar produto.", "red")

    c_loc_cod = ft.TextField(label="Código", width=250); c_loc_desc = ft.TextField(label="Descrição", width=250)
    def salvar_prateleira(e):
        try:
            req = requests.post(f"{API_BASE_URL}/locations/", json={"code": c_loc_cod.value, "description": c_loc_desc.value}, headers=HEADERS_SEGUROS)
            if req.status_code == 201:
                mostrar_notificacao("✅ Prateleira cadastrada!", "green")
                carregar_locais() 
        except Exception: mostrar_notificacao("❌ Erro ao salvar prateleira.", "red")

    tela_cadastros = ft.Column([
        ft.Text("Central de Cadastros", size=28, weight=ft.FontWeight.BOLD, color="purple"),
        ft.Row([
            ft.Column([ft.Text("Novo Produto", size=18), c_nome, c_sku, c_desc, c_preco, ft.ElevatedButton("Salvar", on_click=salvar_produto, bgcolor="green", color="white")]),
            ft.VerticalDivider(width=40, color="transparent"),
            ft.Column([ft.Text("Nova Prateleira", size=18), c_loc_cod, c_loc_desc, ft.ElevatedButton("Salvar", on_click=salvar_prateleira, bgcolor="orange", color="white")])
        ], alignment=ft.MainAxisAlignment.START)
    ], expand=True)

    # A MÁGICA DA NAVEGAÇÃO LATERAL
    telas = [tela_home, tela_terminal, tela_produtos, tela_prateleiras, tela_cadastros]
    
    area_principal = ft.Container(content=tela_home, expand=True, padding=20)

    def mudar_tela(e):
        index = e.control.selected_index
        area_principal.content = telas[index]
        page.update()

    menu_lateral = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=100,
        group_alignment=-0.9, 
        destinations=[
            ft.NavigationRailDestination(icon="dashboard", label="Dashboard"),
            ft.NavigationRailDestination(icon="qr_code_scanner", label="Terminal"),
            ft.NavigationRailDestination(icon="inventory_2", label="Produtos"),
            ft.NavigationRailDestination(icon="view_list", label="Prateleiras"),
            ft.NavigationRailDestination(icon="add_circle", label="Cadastros"),
        ],
        on_change=mudar_tela,
    )

    # INICIALIZAÇÃO E AUTO-REFRESH
    carregar_tudo_e_atualizar()
    filtrar_produtos(None)
    filtrar_locais(None)

    def motor_de_atualizacao():
        while True:
            time.sleep(10) 
            if menu_lateral.selected_index == 0:
                carregar_tudo_e_atualizar()

    threading.Thread(target=motor_de_atualizacao, daemon=True).start()

    page.add(
        ft.Row(
            controls=[
                menu_lateral,
                ft.VerticalDivider(width=1),
                ft.Column([texto_notificacao, area_principal], expand=True)
            ],
            expand=True
        )
    )

# Configuração para rodar na Nuvem como um Site (Web App)
porta = int(os.environ.get("PORT", 8080))
ft.app(target=main, view=ft.AppView.WEB_BROWSER, host="0.0.0.0", port=porta)