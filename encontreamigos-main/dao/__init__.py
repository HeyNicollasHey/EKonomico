import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta

def conectardb():
    con = psycopg2.connect(
        host='localhost',
        database='encontraramigos',
        user='postgres',
        password='root'
    )

    return con


def verificarlogin(email, senha):
    conexao = conectardb()
    cur = conexao.cursor()
    cur.execute("SELECT * FROM usuarios WHERE email = %s AND senha = %s", (email, senha))
    recset = cur.fetchall()
    conexao.close()

    return recset

def inseriruser(email, nome, senha, tipo, foto_perfil):
    conexao = conectardb()
    cur = conexao.cursor()
    try:
        cur.execute("INSERT INTO usuarios (email, nome, senha, tipo, foto_perfil) VALUES (%s, %s, %s, %s, %s)", (email, nome, senha, tipo, foto_perfil))
        conexao.commit()
        return True
    except Exception as e:
        print(f"Erro ao inserir usuário: {e}")
        conexao.rollback()
        return False
    finally:
        conexao.close()

def inserirproduto(nome, preco, validade, quantidade, marca, path):
    conexao = conectardb()
    cur = conexao.cursor()
    exito = False
    try:
        cur.execute("INSERT INTO produtos (nome, preco, data_validade, quantidade, marca, pathft) VALUES (%s, %s, %s, %s, %s, %s)", (nome, preco, validade, quantidade, marca, path))
    except psycopg2.IntegrityError:
        conexao.rollback()
        exito = False
    else:
        conexao.commit()
        exito = True
    conexao.close()
    return exito

def buscar_produtos():
    conexao = conectardb()
    if not conexao:
        return None

    cur = conexao.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("SELECT nome, preco, data_validade, quantidade, marca, pathft FROM produtos")
        produtos = cur.fetchall()
        return produtos
    except psycopg2.Error as e:
        print(f'Erro ao buscar produtos: {e}')
        return None
    finally:
        conexao.close()

def excluir_produto(nome):
    conexao = conectardb()
    cur = conexao.cursor()
    try:
        cur.execute("DELETE FROM produtos WHERE nome = %s", (nome,))
        conexao.commit()
        return True
    except psycopg2.Error as e:
        print(f'Erro ao excluir produto: {e}')
        conexao.rollback()
        return False
    finally:
        conexao.close()

def excluir_usuario(nome):
    conexao = conectardb()
    cur = conexao.cursor()
    try:
        cur.execute("DELETE FROM usuarios WHERE nome = %s", (nome,))
        conexao.commit()
        return True
    except psycopg2.Error as e:
        print(f'Erro ao excluir usuario: {e}')
        conexao.rollback()
        return False
    finally:
        conexao.close()


def comprar_produto(pedido, nome):
    conexao = conectardb()
    cur = conexao.cursor()
    try:
        # Recuperar a quantidade atual do produto
        cur.execute("SELECT quantidade FROM produtos WHERE nome = %s", (nome,))
        resultado = cur.fetchone()

        if resultado is None:
            print("Produto não encontrado.")
            return False

        quantidade_atual = resultado[0]

        if quantidade_atual < pedido:
            print("Quantidade insuficiente em estoque.")
            return False

        nova_quantidade = quantidade_atual - pedido

        cur.execute("UPDATE produtos SET quantidade = %s WHERE nome = %s", (nova_quantidade, nome))
        conexao.commit()
        return True
    except psycopg2.Error as e:
        print(f'Erro ao atualizar o produto: {e}')
        conexao.rollback()
        return False
    finally:
        conexao.close()

def atualizar_produto(nome, preco, validade, quantidade, marca, path, nomeproduto):
    conexao = conectardb()
    cur = conexao.cursor()
    exito = False
    try:
        cur.execute("UPDATE produtos SET nome = %s, preco = %s, data_validade = %s, quantidade = %s, marca = %s, pathft = %s WHERE nome = %s", (nome, preco, validade, quantidade, marca, path, nomeproduto))
    except psycopg2.Error as e:
        print("Erro ao atualizar o produto:", e)
        conexao.rollback()
    else:
        conexao.commit()
        exito = True
    finally:
        conexao.close()
    return exito

def buscar_produtos_validade():
    conexao = conectardb()
    if not conexao:
        return None

    cur = conexao.cursor(cursor_factory=RealDictCursor)
    try:
        data_atual = datetime.now()
        data_futura = data_atual + timedelta(days=7)
        cur.execute("""
            SELECT nome, preco, data_validade, quantidade, marca, pathft 
            FROM produtos 
            WHERE data_validade BETWEEN %s AND %s 
            ORDER BY data_validade ASC
        """, (data_atual, data_futura))
        produtos = cur.fetchall()
        return produtos
    except psycopg2.Error as e:
        print(f'Erro ao buscar produtos próximos da validade: {e}')
        return None
    finally:
        conexao.close()


def registrar_compra(nome_produto, quantidade, valor_total):
    conexao = conectardb()
    cur = conexao.cursor()
    try:
        data_compra = datetime.now().date()  # Obter apenas a data atual
        cur.execute(
            "INSERT INTO compra (data_compra, nome_produto, valor) VALUES (%s, %s, %s)",
            (data_compra, nome_produto, valor_total)
        )
        conexao.commit()
        return True
    except psycopg2.Error as e:
        print(f'Erro ao registrar compra: {e}')
        conexao.rollback()
        return False
    finally:
        conexao.close()