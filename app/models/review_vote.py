from app.database import db

class ReviewVote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    review_id = db.Column(db.Integer, db.ForeignKey('platform_review.id'), nullable=False)
    review = db.relationship('PlatformReview', backref='votes')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    vote_type = db.Column(db.String(10), nullable=False)  # 'like' или 'dislike'

    # Проверка на уникальность голосования для пользователя и отзыва
    __table_args__ = (db.UniqueConstraint('review_id', 'user_id', name='unique_vote'),)
