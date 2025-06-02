from flask import Blueprint, render_template
from app.models.news import News

news_bp = Blueprint('news', __name__)

# Страница с новостями
@news_bp.route('/news')
def all():
    news_items = News.query.order_by(News.date.desc()).all()
    return render_template('news_all.html', news_items=news_items)

# Страница с деталями новости
@news_bp.route('/news/<int:news_id>')
def detail(news_id):
    news_item = News.query.get_or_404(news_id)
    return render_template('news_detail.html', news_item=news_item)
