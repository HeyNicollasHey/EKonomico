import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, make_response
from werkzeug.utils import secure_filename
import dao
from os.path import join, dirname, realpath

app = Flask(__name__)
app.secret_key = 'ASsadlkjasdAJS54$5sdSA21'
app.config['UPLOAD_FOLDER'] = join(dirname(realpath(__file__)), 'static/imagens/')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cadastrarusuario', methods=['GET', 'POST'])
def cadastrarUser():
    if request.method == 'GET':
        return render_template('cadastraruser.html')
    elif request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')
        tipo = request.form.get('tipo')
        f = request.files['file']

        filename = secure_filename(f.filename)
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        f.save(path)

        rel_path = os.path.relpath(path, app.config['UPLOAD_FOLDER'])

        if dao.inseriruser(email, nome, senha, tipo, rel_path):
            flash('Usuário cadastrado com sucesso', category='sucess')
        else:
            flash('Usuário já cadastrado. Tente novamente', category='error')
        return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def verificarlogin():
    if request.method == 'GET':
        return render_template('pagelogin.html')
    elif request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        result = dao.verificarlogin(email, senha)

        if len(result) > 0:
            session['email'] = email
            session['tipo'] = result[0][4]
            session['path'] = result[0][5]
            return redirect(url_for('home'))
        else:
            flash('Login ou senha incorretos', category='error')
            return redirect(url_for('index'))

@app.route('/home')
def home():
    email = session.get('email')
    path = session.get('path')
    tipo = session.get('tipo')
    return render_template('home.html', email=email, pathft=path, tipo=tipo)


@app.route('/cadastrarproduto', methods=['GET', 'POST'])
def cadastrarProduto():
    if session.get('tipo') == 'admin':
        if request.method == 'GET':
            return render_template('cadastrarproduto.html')
        elif request.method == 'POST':
            nome = request.form.get('nome')
            validade = request.form.get('validade')
            quantidade = request.form.get('quantidade')
            marca = request.form.get('marca')
            preco = request.form.get('preco')
            f = request.files['file']

            filename = secure_filename(f.filename)
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            f.save(path)

            rel_path = os.path.relpath(path, app.config['UPLOAD_FOLDER'])

            if dao.inserirproduto(nome, preco, validade, quantidade, marca, rel_path):
                flash('Produto cadastrado com sucesso', 'success')
            else:
                flash('Produto já cadastrado. Tente novamente', 'error')

            return redirect(url_for('cadastrarProduto'))
    else:
        flash('Você não tem permissão para acessar esta página.', 'error')
        return redirect(url_for('index'))

@app.route('/atualizarproduto', methods=['GET', 'POST'])
def atualizarProduto():
    if session.get('tipo') == 'admin':
        if request.method == 'GET':
            return render_template('atualizarproduto.html')
        elif request.method == 'POST':
            nomeproduto = request.form.get('nomeProduto')
            nome = request.form.get('nome')
            validade = request.form.get('validade')
            quantidade = request.form.get('quantidade')
            marca = request.form.get('marca')
            preco = request.form.get('preco')
            f = request.files['file']

            filename = secure_filename(f.filename)
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            f.save(path)

            rel_path = os.path.relpath(path, app.config['UPLOAD_FOLDER'])

            if dao.atualizar_produto(nome, preco, validade, quantidade, marca, rel_path, nomeproduto):
                flash('Produto atualizado com sucesso', 'success')
            else:
                flash('Erro ao atualizar produto', 'error')

            return redirect(url_for('atualizarProduto'))
    else:
        flash('Você não tem permissão para acessar esta página.', 'error')
        return redirect(url_for('index'))

@app.route('/excluirproduto', methods=['GET', 'POST'])
def excluir_produto():
    if session.get('tipo') == 'admin':
        if request.method == 'GET':
            return render_template('excluirproduto.html')
        elif request.method == 'POST':
            nome = request.form.get('nome')
            sucesso = dao.excluir_produto(nome)
            if sucesso:
                flash(f'O produto "{nome}" foi excluído com sucesso.')
            else:
                flash(f'Erro ao excluir o produto "{nome}".')
            return redirect(url_for('index'))
    else:
        flash('Você não tem permissão para acessar esta página.', category='error')
        return redirect(url_for('index'))

@app.route('/excluirusuario', methods=['GET', 'POST'])
def excluir_usuario():
    if session.get('tipo') == 'admin':
        if request.method == 'GET':
            return render_template('excluirusuario.html')
        elif request.method == 'POST':
            nome = request.form.get('nome')
            sucesso = dao.excluir_usuario(nome)
            if sucesso:
                flash(f'O usuario "{nome}" foi excluído com sucesso.', category='sucess')
            else:
                flash(f'Erro ao excluir o usuario "{nome}".')
            return redirect(url_for('index'))
    else:
        flash('Você não tem permissão para acessar esta página.', category='error')
        return redirect(url_for('index'))

@app.route('/listarprodutos', methods=['GET', 'POST'])
def listar_produtos():
    produtos = dao.buscar_produtos()
    if produtos is None:
        return 'Erro ao buscar produtos do banco de dados.'

    if request.method == 'POST':
        nome = request.form.get('nome')
        pedido = int(request.form.get('pedido'))
        sucesso = dao.comprar_produto(pedido, nome)
        if sucesso:
            flash(f'O produto "{nome}" foi comprado com sucesso.', category='sucess')
        else:
            flash(f'Erro ao comprar o produto "{nome}".', category='error')
        return redirect(url_for('index'))

    return render_template('listarprodutos.html', produtos=produtos)

@app.route('/comprarproduto/externo', methods=['POST'])
def comprar_produto_externo():
    if session.get('email') is not None:
        nome = request.form.get('nome')
        pedido = int(request.form.get('pedido'))

        sucesso = dao.comprar_produto(pedido, nome)
        if sucesso:
            return jsonify({"mensagem": f'O produto "{nome}" foi comprado com sucesso.'}), 200
        else:
            return jsonify({"mensagem": f'Erro ao comprar o produto "{nome}".'}), 400
    else:
        return jsonify({"mensagem": "Necessário fazer login"}), 401

@app.route('/listarprodutos/validade', methods=['GET'])
def listar_produtos_validade():
    if session.get('email') is not None:
        produtos = dao.buscar_produtos_validade()
        if produtos:
            return jsonify(produtos), 200
        else:
            return jsonify({"mensagem": "Não há produtos próximos da data de validade"}), 404
    else:
        return jsonify({"mensagem": "Necessário fazer login"}), 401

@app.route('/login/externo', methods=['POST'])
def verificarloginexterno():
    email = request.form.get('email')
    senha = request.form.get('senha')
    result = dao.verificarlogin(email, senha)

    if len(result) > 0:
        session['email'] = email
        tipo_usuario = result[0][3]
        session['tipo_usuario'] = tipo_usuario
        cookie = 'email=' + email + '; tipo_login=' + tipo_usuario
        sessionPath = '/login'
        resposta = make_response("Usuario Logado com Sucesso")
        resposta.headers['Set-Cookie'] = cookie
        resposta.headers['X-Session-Path'] = sessionPath
        return resposta
    else:
        return "Email ou Senha Incorretos"

@app.route('/buscarprodutos/externo', methods=['GET'])
def buscar_produtos_ext():
    if session.get('email') is not None:
        produtos = dao.buscar_produtos()
        if produtos is not None:
            return jsonify(produtos)
        else:
            return jsonify({"mensagem": "Erro ao buscar produtos"}), 500
    else:
        return jsonify({"mensagem": "Necessário fazer login"}), 401



@app.route('/logout')
def logout():
    session.pop('email', None)
    session.pop('tipo', None)
    session.pop('path', None)

    res = make_response("Cookie Removido")
    res.set_cookie('email', '', max_age=0)

    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
