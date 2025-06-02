from app.database import db

class ProgrammingLanguage(db.Model):
    __tablename__ = 'programming_language'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)

    # Изменим backref на уникальное имя
    courses_list = db.relationship('Course', backref='language_association', lazy=True)

    def __repr__(self):
        return f'<ProgrammingLanguage {self.name}>'
