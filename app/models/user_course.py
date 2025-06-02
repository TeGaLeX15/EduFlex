from app.database import db

class UserCourse(db.Model):
    __tablename__ = 'user_course'

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), primary_key=True)

    # Связь с пользователем
    user = db.relationship('User', backref=db.backref('user_courses', lazy=True))  # Уникальное имя backref
    # Связь с курсом
    course = db.relationship('Course', backref=db.backref('user_course_rel', lazy=True))  # Уникальное имя backref

    def __repr__(self):
        return f'<UserCourse(user_id={self.user_id}, course_id={self.course_id})>'