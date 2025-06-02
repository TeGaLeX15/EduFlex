from app.database import db

class Module(db.Model):
    __tablename__ = 'modules'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))
    title = db.Column(db.String)
    position = db.Column(db.Integer)

    # Связь с уроками
    lessons = db.relationship('Lesson', backref='module', lazy=True)

    def __repr__(self):
        return f'<Module {self.title}>'
