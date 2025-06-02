from app.database import db

# Определяем промежуточные таблицы
user_interests = db.Table('user_interests',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('interest_id', db.Integer, db.ForeignKey('interest.id'), primary_key=True)
)

course_interests = db.Table('course_interests',
    db.Column('course_id', db.Integer, db.ForeignKey('courses.id'), primary_key=True),
    db.Column('interest_id', db.Integer, db.ForeignKey('interest.id'), primary_key=True)
)

class Interest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)  # Например, 'Frontend', 'UI/UX', 'Data Science'

    # Связь с курсами через промежуточную таблицу course_interests
    courses = db.relationship(
        'Course',
        secondary='course_interests',
        backref=db.backref('associated_interests', lazy='dynamic'),  # Уникальное имя для backref
        primaryjoin='Interest.id == course_interests.c.interest_id',
        secondaryjoin='Course.id == course_interests.c.course_id'
    )

    # Связь с пользователями через промежуточную таблицу user_interests
    users = db.relationship(
        'User',
        secondary='user_interests',
        backref=db.backref('user_interests_set', lazy='dynamic'),  # Переименовал backref
        primaryjoin='Interest.id == user_interests.c.interest_id',
        secondaryjoin='User.id == user_interests.c.user_id'
    )

    def __repr__(self):
        return f'<Interest {self.name}>'