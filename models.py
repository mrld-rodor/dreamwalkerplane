"""
models.py - Modelos SQLAlchemy para DreamWalker Plane
Mantém compatibilidade com o banco MariaDB existente
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import bleach

# Instância do SQLAlchemy (será inicializada no app.py)
db = SQLAlchemy()


class Relato(db.Model):
    """
    Modelo para os relatos dos usuários
    Tabela: relatos (vamos criar)
    """
    __tablename__ = 'relatos'
    
    id = db.Column(db.Integer, primary_key=True)
    autor = db.Column(db.String(100), nullable=False)
    titulo = db.Column(db.String(200), nullable=False)
    conteudo = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='pendente')  # pendente, aprovado, rejeitado
    data_envio = db.Column(db.DateTime, default=datetime.utcnow)
    data_aprovacao = db.Column(db.DateTime, nullable=True)
    ip_remetente = db.Column(db.String(45), nullable=True)  # IPv4 ou IPv6
    
    def __repr__(self):
        return f'<Relato {self.titulo} - {self.status}>'
    
    def sanitizar_conteudo(self):
        """
        Sanitiza o conteúdo para evitar XSS
        Remove tags HTML perigosas, mantém apenas básicas
        """
        allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'blockquote']
        self.conteudo = bleach.clean(self.conteudo, tags=allowed_tags, strip=True)
        return self.conteudo
    
    def to_dict(self):
        """Converte o relato para dicionário (útil para API)"""
        return {
            'id': self.id,
            'autor': self.autor,
            'titulo': self.titulo,
            'conteudo': self.conteudo,
            'data_envio': self.data_envio.strftime('%d/%m/%Y %H:%M') if self.data_envio else None,
        }


class MensagemContato(db.Model):
    """
    Modelo para armazenar mensagens de contato (opcional)
    Tabela: mensagens_contato (vamos criar)
    """
    __tablename__ = 'mensagens_contato'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    mensagem = db.Column(db.Text, nullable=False)
    data_envio = db.Column(db.DateTime, default=datetime.utcnow)
    respondido = db.Column(db.Boolean, default=False)
    ip_remetente = db.Column(db.String(45), nullable=True)
    
    def __repr__(self):
        return f'<Mensagem de {self.nome} - {self.data_envio}>'