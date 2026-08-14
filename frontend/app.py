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

    texto_notificacao = ft.Text(value="", size=14, weight="bold")

    def mostrar_notificacao(mensagem, cor):
        texto_notificacao.value = mensagem
        texto_notificacao.color = cor
        page.update()

    # COMPONENTE BLINDADO: BOTÃO CUSTOMIZADO
    def btn_custom(texto, cor, click, icone=None):
        elementos = []
        if icone:
            elementos.append(ft.Icon(icone, color="white"))
        elementos.append(ft.Text(texto, color="white", weight="bold"))

        return ft.Container(
            content=ft.Row(elementos, alignment=ft.MainAxisAlignment.CENTER),
            bgcolor=cor, padding=10, border_radius=8, ink=True,
            on_click=click, height=40
        )

    # VARIÁVEIS GLOBAIS DE DADOS
    dados_produtos = []
    dados_locais = []
    dados_movimentacoes = []

    # TELA 0: HOME / DASHBOARD (GRÁFICOS NATIVOS SEGUROS)
    kpi_skus = ft.Text("0", size=28, weight="bold")
    kpi_valor = ft.Text("$ 0.00", size=28, weight="bold")
    kpi_locais = ft.Text("0", size=28, weight="bold")
    kpi_ops = ft.Text("0", size=28, weight="bold") 
    
    # Iniciar os containers já com conteúdo para evitar o bug de otimização do Flutter
    container_grafico_linha = ft.Container(content=ft.Text("Aguardando dados...", color="grey"), height=300, padding=15)
    container_grafico_barra = ft.Container(content=ft.Text("Aguardando dados...", color="grey"), height=300, padding=15)

    def criar_card_kpi(titulo, texto_valor, trend_text, trend_color, trend_icon):
        return ft.Card(
            elevation=2,
            content=ft.Container(
                padding=20, bgcolor="#2A2D32", border_radius=10,
                content=ft.Column([
                    ft.Text(titulo, size=14, color="#B0BEC5"), 
                    texto_valor,
                    ft.Row([
                        ft.Icon(trend_icon, color=trend_color, size=16),
                        ft.Text(trend_text, color=trend_color, size=12, weight="bold")
                    ], spacing=2)
                ], spacing=5)
            ), expand=True
        )

    def atualizar_kpis():
        try:
            estoque_real = {}
            for mov in dados_movimentacoes:
                p_id = mov["product_id"]
                qtd = mov["quantity"]
                if mov["movement_type"] == "IN": estoque_real[p_id] = estoque_real.get(p_id, 0) + qtd
                else: estoque_real[p_id] = estoque_real.get(p_id, 0) - qtd

            total_skus = len(dados_produtos)
            total_locais = len(dados_locais)
            total_operacoes = len(dados_movimentacoes)
            
            valor_total = sum(float(p["price"]) * estoque_real.get(p["id"], 0) for p in dados_produtos)
            
            kpi_skus.value = str(total_skus)
            kpi_valor.value = f"$ {valor_total:,.2f}"
            kpi_locais.value = str(total_locais)
            kpi_ops.value = str(total_operacoes) 
            
            # --- CONSTRUÇÃO DE GRÁFICOS USANDO PROPRIEDADES 100% SEGURAS ---
            if total_skus > 0:
                produtos_top = sorted(dados_produtos, key=lambda x: float(x["price"]) * estoque_real.get(x["id"], 0), reverse=True)[:5]
                max_valor_barra = max([float(p["price"]) * estoque_real.get(p["id"], 0) for p in produtos_top]) if produtos_top else 1
                
                # Gráfico de Barras Customizado (Top 5 Valor)
                barras_ui = []
                for p in produtos_top:
                    valor_estocado = float(p["price"]) * estoque_real.get(p["id"], 0)
                    altura = (valor_estocado / max_valor_barra) * 180 if max_valor_barra > 0 else 0 
                    
                    barras_ui.append(
                        ft.Column([
                            ft.Text(f"${valor_estocado/1000:.1f}k", size=11, color="#B0BEC5"),
                            # border_radius com int absoluto para não quebrar
                            ft.Container(width=45, height=altura, bgcolor="#4CAF50", border_radius=5),
                            ft.Text(p["sku"][:5], size=11, weight="bold")
                        ], alignment=ft.MainAxisAlignment.END, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                    )
                container_grafico_barra.content = ft.Row(barras_ui, alignment=ft.MainAxisAlignment.SPACE_EVENLY, vertical_alignment=ft.CrossAxisAlignment.END, expand=True)
                
                # Gráfico de Lista de Ativos (Crescimento)
                linhas_ui = []
                max_preco = max([float(p["price"]) for p in dados_produtos]) if dados_produtos else 1
                for p in dados_produtos[:6]:
                    linhas_ui.append(
                        ft.Column([
                            ft.Row([
                                ft.Icon(ft.Icons.TRENDING_UP, size=16, color="#2196F3"),
                                ft.Text(p["name"], size=13, expand=True),
                                ft.Text(f"$ {float(p['price']):,.2f}", size=13, weight="bold")
                            ]),
                            # ProgressBar envolvida em Container para proteger a propriedade height
                            ft.Container(height=6, content=ft.ProgressBar(value=float(p["price"])/max_preco if max_preco > 0 else 0, color="#2196F3", bgcolor="#37474F"))
                        ], spacing=4)
                    )
                container_grafico_linha.content = ft.Column(linhas_ui, expand=True, spacing=15)
            else:
                container_grafico_barra.content = ft.Text("Sem dados no estoque para plotar.")
                container_grafico_linha.content = ft.Text("Sem dados no estoque para plotar.")
            
            page.update()
            
            # Força o recarregamento direto na memória da página
            if container_grafico_barra.page: container_grafico_barra.update()
            if container_grafico_linha.page: container_grafico_linha.update()
            
        except Exception as e:
            # CHEGA DE FALHAS SILENCIOSAS. Se o gráfico quebrar, ele vai avisar o porquê na tela!
            container_grafico_barra.content = ft.Text(f"Erro Visual: {e}", color="red")
            container_grafico_linha.content = ft.Text(f"Erro Visual: {e}", color="red")
            if container_grafico_barra.page: container_grafico_barra.update()
            if container_grafico_linha.page: container_grafico_linha.update()

    def carregar_tudo_e_atualizar():
        nonlocal dados_produtos, dados_locais, dados_movimentacoes
        try:
            res_p = requests.get(f"{API_BASE_URL}/products/", headers=HEADERS_SEGUROS)
            res_l = requests.get(f"{API_BASE_URL}/locations/", headers=HEADERS_SEGUROS)
            res_m = requests.get(f"{API_BASE_URL}/movements/", headers=HEADERS_SEGUROS) 
            
            if res_p.status_code == 200: dados_produtos = res_p.json()
            if res_l.status_code == 200: dados_locais = res_l.json()
            if res_m.status_code == 200: dados_movimentacoes = res_m.json()
        except Exception as e:
            print(f"Erro na API: {e}")
        
        # Chama a atualização dos KPIs FORA do try..except da API para blindar a lógica
        atualizar_kpis()

    tela_home = ft.Column([
        ft.Text("Executive Dashboard", size=28, weight="bold"),
        ft.Text("Resumo financeiro e operacional do armazém", color="grey"),
        ft.Divider(height=20, color="transparent"),
        ft.Row([
            criar_card_kpi("Total Revenue", kpi_valor, "+ 12.5%", "green", ft.Icons.ARROW_UPWARD),
            criar_card_kpi("Total SKUs", kpi_skus, "+ 3.2%", "green", ft.Icons.ARROW_UPWARD),
            criar_card_kpi("Prateleiras", kpi_locais, "Estável", "grey", ft.Icons.REMOVE),
            criar_card_kpi("Operações", kpi_ops, "- 1.5%", "red", ft.Icons.ARROW_DOWNWARD),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ft.Divider(height=30, color="transparent"),
        ft.Text("Evolução de Ativos & Concentração", size=20, weight="bold"),
        ft.Row([
            ft.Card(content=container_grafico_linha, expand=2),
            ft.Card(content=container_grafico_barra, expand=1),
        ], alignment=ft.MainAxisAlignment.START)
    ], expand=True, scroll=ft.ScrollMode.AUTO) 

    # TELA 1: TERMINAL DE OPERAÇÃO
    campo_produto_op = ft.TextField(label="ID do Produto", width=300)
    campo_local_op = ft.TextField(label="ID da Prateleira", width=300)
    campo_qtd_op = ft.TextField(label="Quantidade", width=300, keyboard_type=ft.KeyboardType.NUMBER)
    campo_tipo_op = ft.Dropdown(label="Tipo de Movimentação", width=300, options=[ft.dropdown.Option("IN", "ENTRADA"), ft.dropdown.Option("OUT", "SAÍDA")])

    def enviar_movimentacao(e):
        mostrar_notificacao("Processando...", "yellow")
        if not campo_produto_op.value or not campo_local_op.value or not campo_qtd_op.value or not campo_tipo_op.value:
            mostrar_notificacao("❌ Preencha todos os campos!", "red")
            return
        payload = {"product_id": int(campo_produto_op.value), "location_id": int(campo_local_op.value), "quantity": int(campo_qtd_op.value), "movement_type": campo_tipo_op.value}
        try:
            resposta = requests.post(f"{API_BASE_URL}/movements/", json=payload, headers=HEADERS_SEGUROS)
            if resposta.status_code == 201:
                mostrar_notificacao("✅ Movimentação registrada!", "green")
                campo_qtd_op.value = ""
                carregar_tudo_e_atualizar() 
            else: mostrar_notificacao(f"❌ Negado: {resposta.json().get('detail')}", "red")
        except Exception: mostrar_notificacao("❌ Falha de Conexão.", "red")
        page.update()

    tela_terminal = ft.Column([
        ft.Text("Terminal da Empilhadeira", size=28, weight="bold", color="blue"),
        ft.Divider(color="transparent", height=20),
        campo_produto_op, campo_local_op, campo_qtd_op, campo_tipo_op,
        btn_custom("Confirmar Movimentação", "blue", enviar_movimentacao, ft.Icons.CHECK_CIRCLE)
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True)

    # TELA 2: GESTÃO DE PRODUTOS
    tabela_produtos = ft.DataTable(columns=[ft.DataColumn(ft.Text("ID")), ft.DataColumn(ft.Text("SKU")), ft.DataColumn(ft.Text("Nome")), ft.DataColumn(ft.Text("Preço")), ft.DataColumn(ft.Text("Ações"))], rows=[])

    def renderizar_produtos(lista):
        tabela_produtos.rows.clear()
        for p in lista:
            tabela_produtos.rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(str(p["id"]))), ft.DataCell(ft.Text(p["sku"])), ft.DataCell(ft.Text(p["name"])), ft.DataCell(ft.Text(f"R$ {p['price']:.2f}")),
                ft.DataCell(ft.IconButton(icon=ft.Icons.DELETE, icon_color="red", on_click=lambda e, s=p["sku"]: confirmar_excluir_produto(s))),
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
            fechar(None); requests.delete(f"{API_BASE_URL}/products/{sku}", headers=HEADERS_SEGUROS)
            carregar_produtos(); mostrar_notificacao(f"✅ SKU {sku} excluído!", "green")
        pop_up = ft.AlertDialog(title=ft.Text("Excluir Produto"), content=ft.Text(f"Deletar '{sku}'?"), actions=[btn_custom("Cancelar", "grey", fechar), btn_custom("Excluir", "red", deletar)])
        page.dialog = pop_up; pop_up.open = True; page.update()

    tela_produtos = ft.Column([
        ft.Text("Estoque de Produtos", size=28, weight="bold", color="blue"),
        ft.Row([campo_pesq_prod, ft.IconButton(icon=ft.Icons.REFRESH, on_click=carregar_produtos)]),
        ft.Column([tabela_produtos], scroll=ft.ScrollMode.AUTO, expand=True)
    ], expand=True)

    # TELA 3: GESTÃO DE PRATELEIRAS
    tabela_locais = ft.DataTable(columns=[ft.DataColumn(ft.Text("ID")), ft.DataColumn(ft.Text("Código")), ft.DataColumn(ft.Text("Descrição")), ft.DataColumn(ft.Text("Ações"))], rows=[])

    def renderizar_locais(lista):
        tabela_locais.rows.clear()
        for l in lista:
            tabela_locais.rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(str(l["id"]))), ft.DataCell(ft.Text(l["code"])), ft.DataCell(ft.Text(l["description"])),
                ft.DataCell(ft.IconButton(icon=ft.Icons.DELETE, icon_color="red", on_click=lambda e, lid=l["id"], cod=l["code"]: confirmar_excluir_local(lid, cod))),
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
            fechar(None); requests.delete(f"{API_BASE_URL}/locations/{lid}", headers=HEADERS_SEGUROS)
            carregar_locais(); mostrar_notificacao(f"✅ Prateleira {cod} excluída!", "green")
        pop_up = ft.AlertDialog(title=ft.Text("Excluir Prateleira"), content=ft.Text(f"Deletar '{cod}'?"), actions=[btn_custom("Cancelar", "grey", fechar), btn_custom("Excluir", "red", deletar)])
        page.dialog = pop_up; pop_up.open = True; page.update()

    tela_prateleiras = ft.Column([
        ft.Text("Mapa de Prateleiras", size=28, weight="bold", color="orange"),
        ft.Row([campo_pesq_locais, ft.IconButton(icon=ft.Icons.REFRESH, on_click=carregar_locais)]),
        ft.Column([tabela_locais], scroll=ft.ScrollMode.AUTO, expand=True)
    ], expand=True)

    # TELA 4: CADASTROS
    c_nome = ft.TextField(label="Nome", width=250); c_sku = ft.TextField(label="SKU", width=250)
    c_desc = ft.TextField(label="Descrição", width=250); c_preco = ft.TextField(label="Preço", width=250)
    
    def salvar_produto(e):
        try:
            req = requests.post(f"{API_BASE_URL}/products/", json={"name": c_nome.value, "sku": c_sku.value, "description": c_desc.value, "price": float(c_preco.value.replace(",","."))}, headers=HEADERS_SEGUROS)
            if req.status_code == 201: 
                mostrar_notificacao("✅ Produto cadastrado!", "green"); carregar_produtos()
        except Exception: mostrar_notificacao("❌ Erro ao salvar produto.", "red")

    c_loc_cod = ft.TextField(label="Código", width=250); c_loc_desc = ft.TextField(label="Descrição", width=250)
    def salvar_prateleira(e):
        try:
            req = requests.post(f"{API_BASE_URL}/locations/", json={"code": c_loc_cod.value, "description": c_loc_desc.value}, headers=HEADERS_SEGUROS)
            if req.status_code == 201:
                mostrar_notificacao("✅ Prateleira cadastrada!", "green"); carregar_locais() 
        except Exception: mostrar_notificacao("❌ Erro ao salvar prateleira.", "red")

    tela_cadastros = ft.Column([
        ft.Text("Central de Cadastros", size=28, weight="bold", color="purple"),
        ft.Row([
            ft.Column([ft.Text("Novo Produto", size=18), c_nome, c_sku, c_desc, c_preco, btn_custom("Salvar Produto", "green", salvar_produto, ft.Icons.SAVE)]),
            ft.VerticalDivider(width=40, color="transparent"),
            ft.Column([ft.Text("Nova Prateleira", size=18), c_loc_cod, c_loc_desc, btn_custom("Salvar Prateleira", "orange", salvar_prateleira, ft.Icons.SAVE)])
        ], alignment=ft.MainAxisAlignment.START)
    ], expand=True)

    # MENU LATERAL CUSTOMIZADO
    telas = [tela_home, tela_terminal, tela_produtos, tela_prateleiras, tela_cadastros]
    area_principal = ft.Container(content=tela_home, expand=True, padding=20)
    botoes_menu = []

    def atualizar_destaque_menu(index_selecionado):
        for i, btn in enumerate(botoes_menu):
            btn.bgcolor = "#37474F" if i == index_selecionado else "transparent"
        page.update()

    def mudar_tela(index):
        area_principal.content = telas[index]
        atualizar_destaque_menu(index)

    def criar_item_menu(icone, texto, index):
        c = ft.Container(
            content=ft.Row([ft.Icon(icone, color="white"), ft.Text(texto, color="white")]),
            padding=15, border_radius=10, ink=True,
            on_click=lambda e, i=index: mudar_tela(i),
            bgcolor="#37474F" if index == 0 else "transparent"
        )
        botoes_menu.append(c)
        return c

    menu_lateral = ft.Container(
        content=ft.Column([
            criar_item_menu(ft.Icons.DASHBOARD, "Dashboard", 0),
            criar_item_menu(ft.Icons.QR_CODE_SCANNER, "Terminal", 1),
            criar_item_menu(ft.Icons.INVENTORY_2, "Produtos", 2),
            criar_item_menu(ft.Icons.VIEW_LIST, "Prateleiras", 3),
            criar_item_menu(ft.Icons.ADD_CIRCLE, "Cadastros", 4),
        ]),
        width=180, bgcolor="#1E1E1E", padding=10
    )

    # INICIALIZAÇÃO E AUTO-REFRESH
    carregar_tudo_e_atualizar()
    filtrar_produtos(None)
    filtrar_locais(None)

    def motor_de_atualizacao():
        while True:
            time.sleep(10) 
            if area_principal.content == tela_home:
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

porta = int(os.environ.get("PORT", 8080))
ft.app(target=main, view=ft.AppView.WEB_BROWSER, host="0.0.0.0", port=porta)