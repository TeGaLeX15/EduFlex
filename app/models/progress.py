from datetime import datetime
from app.database import db

class Progress(db.Model):
    __tablename__ = 'progress'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # Внешний ключ на таблицу 'user'
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))  # Внешний ключ на таблицу 'course'
    quiz_score = db.Column(db.Integer, default=0)
    completed_tasks = db.Column(db.PickleType, default=list)
    completed_lessons = db.Column(db.PickleType, default=list)

    # Связь с пользователем и курсом
    user = db.relationship('User', backref=db.backref('progresses', lazy=True))
    course = db.relationship('Course', backref=db.backref('progresses', lazy=True))
    quiz_attempts = db.relationship('QuizAttempt', backref='progress', lazy=True)

    def __repr__(self):
        return f'<Progress User {self.user_id} Course {self.course_id}>'

    # Метод для добавления завершённых задач
    def add_completed_task(self, task_id):
        if self.completed_tasks is None:
            self.completed_tasks = []
        if task_id not in self.completed_tasks:
            self.completed_tasks.append(task_id)
    
    # Метод для добавления завершённых уроков
    def add_completed_lesson(self, lesson_id):
        if self.completed_lessons is None:
            self.completed_lessons = []
        if lesson_id not in self.completed_lessons:
            self.completed_lessons.append(lesson_id)

    def get_quiz_stats(self, quiz_id):
        attempts = [a for a in self.quiz_attempts if a.quiz_id == quiz_id]
        if not attempts:
            return {
                "attempts": 0,
                "best_score": 0,
                "last_score": None,
                "last_attempt_date": None
            }
        return {
            "attempts": len(attempts),
            "best_score": max(a.score for a in attempts),
            "last_score": attempts[-1].score,
            "last_attempt_date": attempts[-1].attempt_date
        }
