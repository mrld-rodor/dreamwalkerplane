"""
models.py - DreamWalker Plane
Modelos SQLAlchemy para o banco de dados
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import bleach
from sqlalchemy.dialects.postgresql import JSONB

# Instância do SQLAlchemy
db = SQLAlchemy()


class Contador(db.Model):
    """Contador de visitas (banco)"""
    __tablename__ = 'contador_visitas'
    id = db.Column(db.Integer, primary_key=True, default=1)
    visitantes = db.Column(db.Integer, default=0)
    downloads = db.Column(db.Integer, default=0)
    visitas = db.Column(JSONB, default=list)  # Lista de dicionários

    def to_dict(self):
        return {
            'visitantes': self.visitantes,
            'downloads': self.downloads,
            'visitas': self.visitas or []
        }


class Relato(db.Model):
    """
    Modelo para os relatos dos usuários (posts do blog)
    Tabela: relatos
    """
    __tablename__ = 'relatos'
    
    id = db.Column(db.Integer, primary_key=True)
    autor = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=True)
    titulo = db.Column(db.String(200), nullable=False)
    conteudo = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='pendente')  # pendente, aprovado, rejeitado
    data_envio = db.Column(db.DateTime, default=datetime.utcnow)
    data_aprovacao = db.Column(db.DateTime, nullable=True)
    ip_remetente = db.Column(db.String(45), nullable=True)
    visualizacoes = db.Column(db.Integer, default=0)  # Contador de visualizações
    
    # Relacionamento com comentários
    comentarios = db.relationship('Comentario', backref='relato', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Relato {self.titulo} - {self.status}>'
    
    def sanitizar_conteudo(self):
        """Sanitiza o conteúdo para evitar XSS"""
        allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'blockquote']
        self.conteudo = bleach.clean(self.conteudo, tags=allowed_tags, strip=True)
        return self.conteudo
    
    def to_dict(self):
        """Converte o relato para dicionário"""
        return {
            'id': self.id,
            'autor': self.autor,
            'email': self.email,
            'titulo': self.titulo,
            'conteudo': self.conteudo,
            'data_envio': self.data_envio.strftime('%d/%m/%Y %H:%M') if self.data_envio else None,
            'visualizacoes': self.visualizacoes
        }


class Comentario(db.Model):
    """
    Modelo para comentários dos posts
    Tabela: comentarios
    """
    __tablename__ = 'comentarios'
    
    id = db.Column(db.Integer, primary_key=True)
    relato_id = db.Column(db.Integer, db.ForeignKey('relatos.id'), nullable=False)
    autor = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=True)
    conteudo = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='pendente')  # pendente, aprovado, rejeitado
    data_envio = db.Column(db.DateTime, default=datetime.utcnow)
    ip_remetente = db.Column(db.String(45), nullable=True)
    
    def __repr__(self):
        return f'<Comentario de {self.autor} no post {self.relato_id}>'


class MensagemContato(db.Model):
    """
    Modelo para armazenar mensagens de contato (opcional)
    Tabela: mensagens_contato
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