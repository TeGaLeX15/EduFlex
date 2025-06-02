from app.database import db
from app.models.quiz_question import Question
from app.models.lesson import Lesson  # Импорт модели Lesson

class Quiz(db.Model):
    __tablename__ = 'quizzes'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.id'))  # Привязка к уроку

    # Связь с вопросами
    questions = db.relationship('Question', backref='quiz', lazy=True)

    # Связь с уроком
    lesson = db.relationship('Lesson', backref=db.backref('quizzes', lazy=True), foreign_keys=[lesson_id])

    def __repr__(self):
        return f'<Quiz {self.title}>'

    @property
    def course(self):
        """Удобное свойство, чтобы получить курс, к которому относится квиз через урок."""
        if self.lesson and self.lesson.module:
            return self.lesson.module.course
        return None
