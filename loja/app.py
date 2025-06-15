import sqlite3
import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import bcrypt
import datetime
import os
import openpyxl
import matplotlib.pyplot as plt
from io import BytesIO


# Inicialização do banco de dados e criação de usuário padrão
def iniciar_banco():
    conn = sqlite3.connect('loja.db')
    c = conn.cursor()
    # Criação das tabelas
    c.execute('''CREATE TABLE IF NOT EXISTS empresa (
                 id INTEGER PRIMARY KEY,
                 nome TEXT, endereco TEXT, caminho_logo TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS clientes (
                 id INTEGER PRIMARY KEY,
                 nome TEXT, caminho_foto TEXT, limite_credito REAL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS fornecedores (
                 id INTEGER PRIMARY KEY, nome TEXT, contato TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS produtos (
                 id INTEGER PRIMARY KEY, codigo TEXT, nome TEXT, caminho_foto TEXT,
                 codigo_barras TEXT, validade TEXT, grupo TEXT, subgrupo TEXT,
                 estoque INTEGER, estoque_minimo INTEGER, preco REAL, preco_alternativo REAL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS usuarios (
                 id INTEGER PRIMARY KEY, usuario TEXT, senha TEXT, papel TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS formas_pagamento (
                 id INTEGER PRIMARY KEY, nome TEXT, taxa REAL, exibir_fluxo_caixa INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS vendas (
                 id INTEGER PRIMARY KEY, cliente_id INTEGER, usuario_id INTEGER,
                 data TEXT, total REAL, forma_pagamento1_id INTEGER, forma_pagamento2_id INTEGER,
                 valor1 REAL, valor2 REAL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS itens_venda (
                 id INTEGER PRIMARY KEY, venda_id INTEGER, produto_id INTEGER,
                 quantidade INTEGER, preco_unitario REAL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS despesas (
                 id INTEGER PRIMARY KEY, descricao TEXT, valor REAL, data TEXT, observacoes TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS caixa (
                 id INTEGER PRIMARY KEY, data_abertura TEXT, data_fechamento TEXT,
                 saldo_inicial REAL, saldo_final REAL, usuario_id INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS contas_pagar (
                 id INTEGER PRIMARY KEY, fornecedor_id INTEGER, valor REAL, data_vencimento TEXT, pago INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS contas_receber (
                 id INTEGER PRIMARY KEY, cliente_id INTEGER, valor REAL, data_vencimento TEXT, pago INTEGER)''')

    # Criação de usuário padrão (admin/admin123) se não existir
    c.execute("SELECT COUNT(*) FROM usuarios WHERE usuario = ?", ('admin',))
    if c.fetchone()[0] == 0:
        senha = 'admin123'
        hash_senha = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        c.execute("INSERT INTO usuarios (usuario, senha, papel) VALUES (?, ?, ?)",
                  ('admin', hash_senha, 'gerente'))

    conn.commit()
    conn.close()


# Funções de autenticação
def criptografar_senha(senha):
    return bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verificar_senha(senha, hash_senha):
    return bcrypt.checkpw(senha.encode('utf-8'), hash_senha.encode('utf-8'))


# Classe principal do sistema
class SistemaLoja:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Gerenciamento de Loja")
        self.root.configure(bg='#1E90FF')  # Fundo azul
        self.root.geometry("400x600")  # Tamanho mínimo para garantir visibilidade
        self.usuario_atual = None
        iniciar_banco()
        self.tela_login()

    def limpar_tela(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def tela_login(self):
        self.limpar_tela()
        self.root.configure(bg='#1E90FF')
        tk.Label(self.root, text="Usuário", bg='#1E90FF', fg='white').pack(pady=5)
        usuario_entry = tk.Entry(self.root)
        usuario_entry.pack(pady=5)
        tk.Label(self.root, text="Senha", bg='#1E90FF', fg='white').pack(pady=5)
        senha_entry = tk.Entry(self.root, show="*")
        senha_entry.pack(pady=5)
        tk.Button(self.root, text="Entrar", command=lambda: self.login(
            usuario_entry.get(), senha_entry.get()), bg='#32CD32', fg='white').pack(pady=10)

    def login(self, usuario, senha):
        conn = sqlite3.connect('loja.db')
        c = conn.cursor()
        c.execute("SELECT id, usuario, senha, papel FROM usuarios WHERE usuario=?", (usuario,))
        usuario_data = c.fetchone()
        conn.close()
        if usuario_data and verificar_senha(senha, usuario_data[2]):
            self.usuario_atual = {'id': usuario_data[0], 'usuario': usuario_data[1], 'papel': usuario_data[3]}
            self.menu_principal()
        else:
            messagebox.showerror("Erro", "Credenciais inválidas")

    def menu_principal(self):
        self.limpar_tela()
        self.root.configure(bg='#1E90FF')
        tk.Label(self.root, text=f"Bem-vindo, {self.usuario_atual['usuario']}", bg='#1E90FF', fg='white',
                 font=('Arial', 14)).pack(pady=10)

        # Dicionário de opções com cores e comandos
        opcoes = {
            "Perfil": {"command": self.tela_login, "color": "#FF4500", "icon": "👤"},
            "Endereços": {"command": self.cadastrar_empresa, "color": "#FFA500", "icon": "📍"},
            "Cartões": {"command": self.cadastrar_cliente, "color": "#3CB371", "icon": "💳"},
            "Compras": {"command": self.realizar_venda, "color": "#4682B4", "icon": "🛒"},
            "Lojas": {"command": self.cadastrar_produto, "color": "#FFD700", "icon": "🏬"},
            "Indicar": {"command": self.importar_produtos_excel, "color": "#9ACD32", "icon": "👥"}
        }

        # Layout em grade (2 colunas, 3 linhas)
        row = 0
        col = 0
        for texto, dados in opcoes.items():
            if self.usuario_atual['papel'] == 'gerente' or texto not in ["Endereços"]:
                btn = tk.Button(self.root, text=f"{dados['icon']} {texto}", command=dados['command'],
                                bg=dados['color'], fg='white', font=('Arial', 12), width=15, height=2)
                btn.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
                col += 1
                if col > 1:
                    col = 0
                    row += 1

        # Configurar redimensionamento da grade
        for i in range(2):
            self.root.grid_columnconfigure(i, weight=1)
        for i in range(3):
            self.root.grid_rowconfigure(i, weight=1)

        # Adicionar banner Multiplus
        tk.Label(self.root, text="Ganhe 60 pontos por transação\nmultiplus", bg='#1E90FF', fg='white',
                 font=('Arial', 10)).pack(side=tk.BOTTOM, pady=10)

    def cadastrar_empresa(self):
        self.limpar_tela()
        tk.Label(self.root, text="Nome da Empresa").pack()
        nome_entry = tk.Entry(self.root)
        nome_entry.pack()
        tk.Label(self.root, text="Endereço").pack()
        endereco_entry = tk.Entry(self.root)
        endereco_entry.pack()
        tk.Button(self.root, text="Selecionar Logo", command=lambda: self.carregar_imagem("logo_empresa")).pack()
        tk.Button(self.root, text="Salvar", command=lambda: self.salvar_empresa(
            nome_entry.get(), endereco_entry.get())).pack()
        tk.Button(self.root, text="Voltar", command=self.menu_principal).pack()

    def carregar_imagem(self, alvo):
        caminho_arquivo = filedialog.askopenfilename(filetypes=[("Arquivos de imagem", "*.png *.jpg *.jpeg")])
        if caminho_arquivo:
            setattr(self, f"caminho_{alvo}", caminho_arquivo)
            messagebox.showinfo("Sucesso", "Imagem selecionada")

    def salvar_empresa(self, nome, endereco):
        if not hasattr(self, 'caminho_logo_empresa'):
            messagebox.showerror("Erro", "Selecione um logo")
            return
        conn = sqlite3.connect('loja.db')
        c = conn.cursor()
        c.execute("INSERT INTO empresa (nome, endereco, caminho_logo) VALUES (?, ?, ?)",
                  (nome, endereco, self.caminho_logo_empresa))
        conn.commit()
        conn.close()
        messagebox.showinfo("Sucesso", "Empresa cadastrada")
        self.menu_principal()

    def cadastrar_cliente(self):
        self.limpar_tela()
        tk.Label(self.root, text="Nome do Cliente").pack()
        nome_entry = tk.Entry(self.root)
        nome_entry.pack()
        tk.Label(self.root, text="Limite de Crédito").pack()
        limite_entry = tk.Entry(self.root)
        limite_entry.pack()
        tk.Button(self.root, text="Selecionar Foto", command=lambda: self.carregar_imagem("foto_cliente")).pack()
        tk.Button(self.root, text="Salvar", command=lambda: self.salvar_cliente(
            nome_entry.get(), limite_entry.get())).pack()
        tk.Button(self.root, text="Voltar", command=self.menu_principal).pack()

    def salvar_cliente(self, nome, limite_credito):
        if not hasattr(self, 'caminho_foto_cliente'):
            messagebox.showerror("Erro", "Selecione uma foto")
            return
        try:
            limite_credito = float(limite_credito)
        except ValueError:
            messagebox.showerror("Erro", "Limite de crédito inválido")
            return
        conn = sqlite3.connect('loja.db')
        c = conn.cursor()
        c.execute("INSERT INTO clientes (nome, caminho_foto, limite_credito) VALUES (?, ?, ?)",
                  (nome, self.caminho_foto_cliente, limite_credito))
        conn.commit()
        conn.close()
        messagebox.showinfo("Sucesso", "Cliente cadastrado")
        self.menu_principal()

    def cadastrar_produto(self):
        self.limpar_tela()
        tk.Label(self.root, text="Código do Produto").pack()
        codigo_entry = tk.Entry(self.root)
        codigo_entry.pack()
        tk.Label(self.root, text="Nome").pack()
        nome_entry = tk.Entry(self.root)
        nome_entry.pack()
        tk.Label(self.root, text="Código de Barras").pack()
        cod_barras_entry = tk.Entry(self.root)
        cod_barras_entry.pack()
        tk.Label(self.root, text="Validade (AAAA-MM-DD)").pack()
        validade_entry = tk.Entry(self.root)
        validade_entry.pack()
        tk.Label(self.root, text="Grupo").pack()
        grupo_entry = tk.Entry(self.root)
        grupo_entry.pack()
        tk.Label(self.root, text="Subgrupo").pack()
        subgrupo_entry = tk.Entry(self.root)
        subgrupo_entry.pack()
        tk.Label(self.root, text="Estoque").pack()
        estoque_entry = tk.Entry(self.root)
        estoque_entry.pack()
        tk.Label(self.root, text="Estoque Mínimo").pack()
        estoque_min_entry = tk.Entry(self.root)
        estoque_min_entry.pack()
        tk.Label(self.root, text="Preço").pack()
        preco_entry = tk.Entry(self.root)
        preco_entry.pack()
        tk.Label(self.root, text="Preço Alternativo").pack()
        preco_alt_entry = tk.Entry(self.root)
        preco_alt_entry.pack()
        tk.Button(self.root, text="Selecionar Foto", command=lambda: self.carregar_imagem("foto_produto")).pack()
        tk.Button(self.root, text="Salvar", command=lambda: self.salvar_produto(
            codigo_entry.get(), nome_entry.get(), cod_barras_entry.get(), validade_entry.get(),
            grupo_entry.get(), subgrupo_entry.get(), estoque_entry.get(),
            estoque_min_entry.get(), preco_entry.get(), preco_alt_entry.get())).pack()
        tk.Button(self.root, text="Voltar", command=self.menu_principal).pack()

    def salvar_produto(self, codigo, nome, cod_barras, validade, grupo, subgrupo, estoque, estoque_min, preco,
                       preco_alt):
        if not hasattr(self, 'caminho_foto_produto'):
            messagebox.showerror("Erro", "Selecione uma foto")
            return
        try:
            estoque = int(estoque)
            estoque_min = int(estoque_min)
            preco = float(preco)
            preco_alt = float(preco_alt)
        except ValueError:
            messagebox.showerror("Erro", "Entrada numérica inválida")
            return
        conn = sqlite3.connect('loja.db')
        c = conn.cursor()
        c.execute(
            "INSERT INTO produtos (codigo, nome, caminho_foto, codigo_barras, validade, grupo, subgrupo, estoque, estoque_min, preco, preco_alternativo) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (codigo, nome, self.caminho_foto_produto, cod_barras, validade, grupo, subgrupo, estoque, estoque_min,
             preco, preco_alt))
        conn.commit()
        conn.close()
        messagebox.showinfo("Sucesso", "Produto cadastrado")
        self.menu_principal()

    def abrir_caixa(self):
        self.limpar_tela()
        tk.Label(self.root, text="Saldo Inicial").pack()
        saldo_entry = tk.Entry(self.root)
        saldo_entry.pack()
        tk.Button(self.root, text="Abrir", command=lambda: self.salvar_caixa(saldo_entry.get())).pack()
        tk.Button(self.root, text="Voltar", command=self.menu_principal).pack()

    def salvar_caixa(self, saldo_inicial):
        try:
            saldo_inicial = float(saldo_inicial)
        except ValueError:
            messagebox.showerror("Erro", "Valor de saldo inválido")
            return
        conn = sqlite3.connect('loja.db')
        c = conn.cursor()
        c.execute("INSERT INTO caixa (data_abertura, saldo_inicial, usuario_id) VALUES (?, ?, ?)",
                  (datetime.datetime.now().isoformat(), saldo_inicial, self.usuario_atual['id']))
        conn.commit()
        conn.close()
        messagebox.showinfo("Sucesso", "Caixa aberto")
        self.menu_principal()

    def realizar_venda(self):
        self.limpar_tela()
        tk.Label(self.root, text="ID do Cliente").pack()
        cliente_id_entry = tk.Entry(self.root)
        cliente_id_entry.pack()
        tk.Label(self.root, text="Código do Produto").pack()
        codigo_produto_entry = tk.Entry(self.root)
        codigo_produto_entry.pack()
        tk.Label(self.root, text="Quantidade").pack()
        quantidade_entry = tk.Entry(self.root)
        quantidade_entry.pack()
        tk.Label(self.root, text="ID Forma de Pagamento 1").pack()
        forma1_entry = tk.Entry(self.root)
        forma1_entry.pack()
        tk.Label(self.root, text="Valor 1").pack()
        valor1_entry = tk.Entry(self.root)
        valor1_entry.pack()
        tk.Label(self.root, text="ID Forma de Pagamento 2 (opcional)").pack()
        forma2_entry = tk.Entry(self.root)
        forma2_entry.pack()
        tk.Label(self.root, text="Valor 2 (opcional)").pack()
        valor2_entry = tk.Entry(self.root)
        valor2_entry.pack()
        tk.Label(self.root, text="Usar Preço Alternativo? (sim/não)").pack()
        preco_alt_entry = tk.Entry(self.root)
        preco_alt_entry.pack()
        tk.Button(self.root, text="Processar Venda", command=lambda: self.processar_venda(
            cliente_id_entry.get(), codigo_produto_entry.get(), quantidade_entry.get(),
            forma1_entry.get(), valor1_entry.get(), forma2_entry.get(), valor2_entry.get(),
            preco_alt_entry.get())).pack()
        tk.Button(self.root, text="Voltar", command=self.menu_principal).pack()

    def processar_venda(self, cliente_id, codigo_produto, quantidade, forma1_id, valor1, forma2_id, valor2, preco_alt):
        try:
            cliente_id = int(cliente_id)
            quantidade = int(quantidade)
            forma1_id = int(forma1_id) if forma1_id else None
            valor1 = float(valor1) if valor1 else 0
            forma2_id = int(forma2_id) if forma2_id else None
            valor2 = float(valor2) if valor2 else 0
        except ValueError:
            messagebox.showerror("Erro", "Entrada inválida")
            return

        conn = sqlite3.connect('loja.db')
        c = conn.cursor()
        c.execute("SELECT limite_credito FROM clientes WHERE id=?", (cliente_id,))
        cliente = c.fetchone()
        if not cliente:
            messagebox.showerror("Erro", "Cliente não encontrado")
            conn.close()
            return

        c.execute("SELECT id, estoque, preco, preco_alternativo FROM produtos WHERE codigo=?", (codigo_produto,))
        produto = c.fetchone()
        if not produto:
            messagebox.showerror("Erro", "Produto não encontrado")
            conn.close()
            return
        produto_id, estoque, preco, preco_alternativo = produto

        if estoque < quantidade:
            messagebox.showerror("Erro", "Estoque insuficiente")
            conn.close()
            return

        preco_unitario = preco_alternativo if preco_alt.lower() == 'sim' else preco
        total = quantidade * preco_unitario
        if forma1_id and valor1 < total and not forma2_id:
            messagebox.showerror("Erro", "Valor de pagamento insuficiente")
            conn.close()
            return
        if forma1_id and forma2_id and (valor1 + valor2) < total:
            messagebox.showerror("Erro", "Valor total de pagamento insuficiente")
            conn.close()
            return

        # Verificar limite de crédito para vendas a prazo
        if forma1_id and c.execute("SELECT nome FROM formas_pagamento WHERE id=? AND nome LIKE '%crédito%'",
                                   (forma1_id,)).fetchone():
            c.execute("SELECT SUM(valor) FROM contas_receber WHERE cliente_id=? AND pago=0", (cliente_id,))
            divida_atual = c.fetchone()[0] or 0
            if divida_atual + total > cliente[0]:
                messagebox.showerror("Erro", "Limite de crédito excedido")
                conn.close()
                return

        # Registrar venda
        c.execute(
            "INSERT INTO vendas (cliente_id, usuario_id, data, total, forma_pagamento1_id, forma_pagamento2_id, valor1, valor2) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (cliente_id, self.usuario_atual['id'], datetime.datetime.now().isoformat(), total, forma1_id, forma2_id,
             valor1, valor2))
        venda_id = c.lastrowid
        c.execute("INSERT INTO itens_venda (venda_id, produto_id, quantidade, preco_unitario) VALUES (?, ?, ?, ?)",
                  (venda_id, produto_id, quantidade, preco_unitario))
        c.execute("UPDATE produtos SET estoque = estoque - ? WHERE id=?", (quantidade, produto_id))

        # Registrar contas a receber para vendas a prazo
        if forma1_id and c.execute("SELECT nome FROM formas_pagamento WHERE id=? AND nome LIKE '%crédito%'",
                                   (forma1_id,)).fetchone():
            c.execute("INSERT INTO contas_receber (cliente_id, valor, data_vencimento, pago) VALUES (?, ?, ?, 0)",
                      (cliente_id, total, (datetime.datetime.now() + datetime.timedelta(days=30)).isoformat()))

        conn.commit()
        conn.close()
        self.gerar_nota_venda(venda_id)
        messagebox.showinfo("Sucesso", "Venda processada")
        self.menu_principal()

    def gerar_nota_venda(self, venda_id):
        conn = sqlite3.connect('loja.db')
        c = conn.cursor()
        c.execute("SELECT e.nome, e.caminho_logo, v.total, v.data, c.nome FROM vendas v "
                  "JOIN clientes c ON v.cliente_id=c.id JOIN empresa e ON 1=1 WHERE v.id=?", (venda_id,))
        nome_empresa, caminho_logo, total, data, nome_cliente = c.fetchone()
        c.execute("SELECT p.nome, iv.quantidade, iv.preco_unitario FROM itens_venda iv "
                  "JOIN produtos p ON iv.produto_id=p.id WHERE iv.venda_id=?", (venda_id,))
        itens = c.fetchall()
        conn.close()

        caminho_pdf = f"venda_{venda_id}.pdf"
        c = canvas.Canvas(caminho_pdf, pagesize=A4)
        c.drawString(100, 800, nome_empresa)
        if caminho_logo:
            c.drawImage(caminho_logo, 50, 750, width=100, height=50)
        c.drawString(100, 720, f"Cliente: {nome_cliente}")
        c.drawString(100, 700, f"Data: {data}")
        y = 680
        for item in itens:
            c.drawString(100, y, f"{item[0]} x {item[1]} @ {item[2]:.2f}")
            y -= 20
        c.drawString(100, y, f"Total: {total:.2f}")
        c.save()
        messagebox.showinfo("Sucesso", f"Nota de venda salva como {caminho_pdf}")

    def relatorio_vendas(self):
        self.limpar_tela()
        tk.Label(self.root, text="Relatório de Vendas").pack()
        conn = sqlite3.connect('loja.db')
        c = conn.cursor()
        c.execute("SELECT v.id, v.data, v.total, c.nome FROM vendas v JOIN clientes c ON v.cliente_id=c.id")
        vendas = c.fetchall()
        conn.close()
        for venda in vendas:
            tk.Label(self.root,
                     text=f"ID: {venda[0]}, Data: {venda[1]}, Total: {venda[2]:.2f}, Cliente: {venda[3]}").pack()
        tk.Button(self.root, text="Voltar", command=self.menu_principal).pack()

    def importar_produtos_excel(self):
        caminho_arquivo = filedialog.askopenfilename(filetypes=[("Arquivos Excel", "*.xlsx *.xls")])
        if not caminho_arquivo:
            return
        wb = openpyxl.load_workbook(caminho_arquivo)
        planilha = wb.active
        conn = sqlite3.connect('loja.db')
        c = conn.cursor()
        for linha in planilha.iter_rows(min_row=2, values_only=True):
            codigo, nome, cod_barras, validade, grupo, subgrupo, estoque, estoque_min, preco, preco_alt = linha[:10]
            c.execute(
                "INSERT INTO produtos (codigo, nome, caminho_foto, codigo_barras, validade, grupo, subgrupo, estoque, estoque_min, preco, preco_alternativo) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (codigo, nome, '', cod_barras, validade, grupo, subgrupo, estoque, estoque_min, preco, preco_alt))
        conn.commit()
        conn.close()
        messagebox.showinfo("Sucesso", "Produtos importados")
        self.menu_principal()


if __name__ == "__main__":
    root = tk.Tk()
    app = SistemaLoja(root)
    root.mainloop()