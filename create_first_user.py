from app import db, app
from app import Usuario  # Certifique-se de usar o nome correto do modelo

# Criação de um usuário administrador
username = "admin"
password = "senha123"  # Defina uma senha de sua escolha

# Criação do usuário administrador
admin_user = Usuario(username=username, password=password, tipo_usuario="Admin")

# Criação do contexto de aplicação para interagir com o banco de dados
with app.app_context():
    # Adiciona o usuário ao banco de dados
    db.session.add(admin_user)
    db.session.commit()

print("Usuário administrador criado com sucesso!")