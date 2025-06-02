from app.database import db
from flask_login import UserMixin
from app.dependences import bcrypt, login_manager
from app.models.interest import Interest

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    bio = db.Column(db.Text, default='')

    # Связь с интересами
    interests = db.relationship('Interest', secondary='user_interests', backref=db.backref('user_interests_set', lazy='dynamic'))

    # Связь с курсами
    courses = db.relationship('Course', secondary='user_course', backref=db.backref('students', lazy='dynamic'))

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

# User loader для Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))