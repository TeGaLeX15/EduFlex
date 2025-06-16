from app.database import db
from datetime import datetime

class LessonProgress(db.Model):
    __tablename__ = 'lesson_progress'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.id'), nullable=False)  # Убедитесь, что таблица 'lesson' существует и имеет столбец 'id'
    theory_viewed = db.Column(db.Boolean, default=False)
    completed_tasks = db.Column(db.PickleType, default=[])  # список ID завершённых задач
    quiz_passed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime)

    user = db.relationship('User', backref=db.backref('lesson_progresses', lazy=True))
    lesson = db.relationship('Lesson', backref=db.backref('progresses', lazy=True))

    def __repr__(self):
        return f'<LessonProgress User {self.user_id} Lesson {self.lesson_id}>'
    
    def is_completed(self):
        if not self.lesson:
            return False
        if not self.theory_viewed:
            return False
        return self.quiz_passed if self.lesson.quiz else True

    def mark_completed(self):
        self.completed_at = datetime.utcnow()

    def add_completed_task(self, task_id):
        # Инициализируем список, если он None
        if self.completed_tasks is None:
            self.completed_tasks = []
        self.completed_tasks.append(task_id)
