from app.database import db

class Question(db.Model):
    __tablename__ = 'questions'

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text)
    options = db.Column(db.String)  # Храним как строку, потом парсим
    answer = db.Column(db.String)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'))

    def get_options(self):
        return [opt.strip() for opt in self.options.split(',')]

    def __repr__(self):
        return f'<Question {self.text}>'
