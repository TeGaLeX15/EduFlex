from datetime import datetime
from app.database import db

class PlatformReview(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # Оценка (например, от 1 до 5)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Дата создания отзыва

    # Добавляем связь с пользователем
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref='platform_reviews')

    # Добавляем счетчики лайков и дизлайков
    likes_count = db.Column(db.Integer, default=0)
    dislikes_count = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'<PlatformReview {self.id} by User {self.user_id}>'
