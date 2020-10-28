from datetime import datetime
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login
from time import time
import jwt
from app import app

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    admin = db.Column(db.Boolean)
    username = db.Column(db.String(64), index=True, unique=True)
    name = db.Column(db.String(64))
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    contributionPoints = db.Column(db.Integer)

    policies = db.relationship('Policy', backref='user', lazy='dynamic')
    comments = db.relationship('Comment', backref = 'user', lazy = True)
    votes = db.relationship('Vote', backref='user', lazy = True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

class Policy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    title = db.Column(db.String(64), unique=True)

    economic_votes = db.Column(db.Integer)
    death_votes = db.Column(db.Integer)
    adherence_votes = db.Column(db.Integer)
    total_votes = db.Column(db.Integer)
    
    citation = db.Column(db.String(200))
    description = db.Column(db.String(250))
    tags = db.Column(db.String(15))
    votes = db.relationship('Vote', backref='policy', lazy=True)
    comments = db.relationship('Comment',backref='policy', lazy = True)
    
    
class Vote(db.Model):
    user_id = db.Column(db.Integer, primary_key=True, db.ForeignKey('user.id'))
    policy_id_1 = db.Column(db.Integer, primary_key=True, db.ForeignKey('policy.id'))
    policy_id_2 = db.Column(db.Integer, primary_key=True, db.ForeignKey('policy.id'))
    
    economic = db.Column(db.Boolean)
    death = db.Column(db.Boolean)
    adherence = db.Column(db.Boolean)
    conflict = db.Column(db.Boolean)
   
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    policy_id = db.Column(db.Integer, db.ForeignKey('policy.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    text = db.Column(db.String(100))
    citation = db.Column(db.String(200))
    
    
    
    
    
