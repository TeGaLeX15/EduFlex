from datetime import datetime
from app.database import db

class Progress(db.Model):
    __tablename__ = 'progress'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))
    completed_tasks = db.Column(db.PickleType, default=list)
    completed_lessons = db.Column(db.PickleType, default=list)

    user = db.relationship('User', backref=db.backref('progresses', lazy=True))
    course = db.relationship('Course', backref=db.backref('progresses', lazy=True))

    def __repr__(self):
        return f'<Progress User {self.user_id} Course {self.course_id}>'

    def add_completed_task(self, task_id):
        if self.completed_tasks is None:
            self.completed_tasks = []
        if task_id not in self.completed_tasks:
            self.completed_tasks.append(task_id)

    def add_completed_lesson(self, lesson_id):
        if self.completed_lessons is None:
            self.completed_lessons = []
        if lesson_id not in self.completed_lessons:
            self.completed_lessons.append(lesson_id)
