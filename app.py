from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users/win/Desktop/Nova pasta/instance/app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Desabilitar rastreamento de modificações
db = SQLAlchemy(app)

# Modelo de Produto
class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    preco = db.Column(db.Float, nullable=False)

# Modelo de Usuário
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)  # Senha sem hash
    tipo_usuario = db.Column(db.String(50), nullable=False)  # Admin ou Comum

# Página inicial
@app.route("/")
def index():
    return redirect(url_for('login'))

@app.route("/cadastro_produto", methods=["GET", "POST"])
def cadastro_produto():
    if 'user_id' not in session:  # Verifica se o usuário está autenticado
        flash("Por favor, faça login primeiro.", "warning")
        return redirect(url_for('login'))  # Redireciona para login

    if request.method == "POST":
        nome = request.form['nome']
        quantidade = request.form['quantidade']
        preco = request.form['preco']

        # Criar um novo produto
        novo_produto = Produto(nome=nome, quantidade=quantidade, preco=preco)
        db.session.add(novo_produto)
        db.session.commit()

        flash("Produto cadastrado com sucesso!", "success")
        return redirect(url_for('dashboard'))  # Redireciona para o dashboard

    return render_template("cadastro_produto.html")

@app.route("/cadastro_usuario", methods=["GET", "POST"])
def cadastro_usuario():
    if 'user_id' not in session:  # Verifica se o usuário está autenticado
        flash("Por favor, faça login primeiro.", "warning")
        return redirect(url_for('login'))  # Redireciona para login

    # Verificar se o usuário logado é administrador
    usuario_logado = Usuario.query.get(session['user_id'])
    if usuario_logado.tipo_usuario != 'Admin':
        flash("Acesso restrito a administradores.", "danger")
        return redirect(url_for('dashboard'))  # Redireciona para o dashboard se não for admin

    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        tipo_usuario = request.form['tipo_usuario']

        # Verificar se o nome de usuário já existe
        usuario_existente = Usuario.query.filter_by(username=username).first()
        if usuario_existente:
            flash("O nome de usuário já está em uso.", "danger")
        else:
            # Criar um novo usuário
            novo_usuario = Usuario(username=username, password=password, tipo_usuario=tipo_usuario)
            db.session.add(novo_usuario)
            db.session.commit()
            flash(f"Usuário {username} cadastrado com sucesso!", "success")
            return redirect(url_for('dashboard'))  # Redireciona para o dashboard

    return render_template("cadastro_usuario.html")

# Página de login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        
        # Verificar se o nome de usuário foi encontrado
        user = Usuario.query.filter_by(username=username).first()
        
        if user and user.password == password:  # Comparando senha em texto plano
            session['user_id'] = user.id  # Salvar o ID do usuário na sessão
            flash("Login bem-sucedido!", "success")
            print(f"Usuário {username} logado com sucesso!")  # Verificação do login
            print("Redirecionando para o dashboard...")  # Verificação do redirecionamento
            return redirect(url_for('dashboard'))  # Redireciona para o dashboard
        else:
            flash("Usuário ou senha inválidos!", "danger")
            print("Usuário ou senha inválidos!")  # Verificação de falha no login
    
    return render_template("login.html")

# Página de logout
@app.route("/logout")
def logout():
    session.pop('user_id', None)  # Remove o ID do usuário da sessão
    flash("Você foi deslogado com sucesso!", "info")
    return redirect(url_for('login'))  # Redireciona para a página de login

@app.route("/alterar_quantidade/<int:id>", methods=["POST"])
def alterar_quantidade(id):
    if 'user_id' not in session:  # Verifica se o usuário está autenticado
        flash("Por favor, faça login primeiro.", "warning")
        return redirect(url_for('login'))

    produto = Produto.query.get_or_404(id)  # Busca o produto pelo ID

    nova_quantidade = int(request.form['nova_quantidade'])  # Obtém a nova quantidade do formulário

    if nova_quantidade >= 0:  # Garante que a quantidade não seja negativa
        produto.quantidade = nova_quantidade
        db.session.commit()  # Salva as alterações no banco de dados
        flash(f"Quantidade do produto {produto.nome} alterada para {nova_quantidade}.", "success")
    else:
        flash("A quantidade não pode ser negativa.", "danger")

    return redirect(url_for('dashboard'))  # Redireciona de volta para o dashboard

# Página de dashboard
@app.route("/dashboard")
def dashboard():
    if 'user_id' not in session:  # Verifica se o usuário está autenticado
        flash("Por favor, faça login primeiro.", "warning")
        return redirect(url_for('login'))  # Redireciona para login

    # Obter o usuário logado
    usuario_logado = Usuario.query.get(session['user_id'])

    # Passar o usuário logado e a lista de produtos para o template
    produtos = Produto.query.all()
    return render_template("dashboard.html", produtos=produtos, tipo_usuario=usuario_logado.tipo_usuario, usuario_logado=usuario_logado)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Cria todas as tabelas do banco de dados
    app.run(debug=True, host='0.0.0.0', port=5000)