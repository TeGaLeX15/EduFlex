from app.database import db

class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.id'))
    text = db.Column(db.Text)
    position = db.Column(db.Integer)
    is_completed = db.Column(db.Boolean, default=False) 

    # Указываем 'lesson' как backref
    lesson = db.relationship('Lesson', backref=db.backref('task_list', lazy=True))  # Название backref уникально

    def __repr__(self):
        return f'<Task {self.text}>'