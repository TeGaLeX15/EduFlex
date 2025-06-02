from app.database import db

class Lesson(db.Model):
    __tablename__ = 'lessons'

    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id'))
    title = db.Column(db.String)
    content = db.Column(db.Text)
    position = db.Column(db.Integer)

    # Связь с заданиями
    tasks = db.relationship('Task', backref='lesson_tasks', lazy=True)

    def __repr__(self):
        return f'<Lesson {self.title}>'
