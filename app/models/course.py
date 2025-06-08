from app.database import db
from app.models.programming_language import ProgrammingLanguage  # Импортируем модель ProgrammingLanguage
from app.models.quiz import Quiz  # Импортируем модель Quiz
from app.models.interest import Interest
from app.models.module import Module  # Импортируйте модель Module
from app.models.lesson import Lesson  # Импортируйте модель Lesson
from app.models.task import Task  # Импортируйте модель Task

class Course(db.Model):
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    description = db.Column(db.Text)
    teacher = db.Column(db.String)
    rating = db.Column(db.Float)
    reviews = db.Column(db.Integer)
    slug = db.Column(db.String, unique=True)
    language_id = db.Column(db.Integer, db.ForeignKey('programming_language.id'))

    language = db.relationship('ProgrammingLanguage', backref='associated_courses')

    enrolled_users = db.relationship('UserCourse', backref='enrolled_course', lazy=True)

    interests = db.relationship(
        'Interest',
        secondary='course_interests',
        backref=db.backref('linked_courses', lazy='dynamic'),
        primaryjoin='Course.id == course_interests.c.course_id',
        secondaryjoin='Interest.id == course_interests.c.interest_id'
    )

    modules = db.relationship('Module', backref='course', lazy=True)

    # Новое — поля для статуса и автора
    STATUS_DRAFT = 'draft'
    STATUS_PUBLISHED = 'published'

    status = db.Column(db.String(20), nullable=False, default=STATUS_DRAFT)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    author = db.relationship('User', backref='authored_courses')

    def __repr__(self):
        return f'<Course {self.title}>'
