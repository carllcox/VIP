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
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    contribution_points = db.Column(db.Integer)
    reputation = db.Column(db.Integer)
    reputation_confidence = db.Column(db.Integer)

    streak_length = db.Column(db.Integer)
    streak_start = db.Column(db.DateTime, default=datetime.utcnow)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    location = db.relationship('Location', backref='user', lazy=True)
    user_report = db.relationship('UserReport', backref='user', lazy=True)
    location_log = db.relationship('LocationLog', backref='user', lazy=True)

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

class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    location_name = db.Column(db.String(100))
    policy_description = db.Column(db.String(200))
    policy_approved = db.Column(db.Boolean)

    location_lat = db.Column(db.Float)
    location_long = db.Column(db.Float)

    current_mask_level = db.Column(db.Integer)
    current_busyness_level = db.Column(db.Integer)
    last_computed = db.Column(db.DateTime, default=datetime.utcnow)

    average_mask_level = db.Column(db.Integer)
    average_busyness_level = db.Column(db.Integer)

    user_report = db.relationship('UserReport', backref='location', lazy=True)
    covid_report = db.relationship('CovidReports', backref='location', lazy=True)
    location_log = db.relationship('LocationLog', backref='location', lazy=True)

# Note: Only approved comments are visible to public via API
# Only site admins approve comments, business owners do NOT
class UserReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'))

    mask_level = db.Column(db.Integer)
    busyness_level = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    policy_followed = db.Column(db.Integer)
    policy_comment = db.Column(db.String(200))
    policy_comment_approved = db.Column(db.Boolean, default=False)

    review_rating = db.Column(db.Integer)
    review_comment = db.Column(db.String(200))
    review_comment_approved = db.Column(db.Boolean, default=False)

# Privacy concern: Limit CovidReport entries to popular locations (>3 visits)
# Note: NO direct API access (Doesn't output anything)
class CovidReports(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'))

    # Exposer or exposed at a sepecific location

    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    estimated_start = db.Column(db.DateTime, default=datetime.utcnow)

# Note: API only recieves info, no output for any endpoints
class LocationLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'))

    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
