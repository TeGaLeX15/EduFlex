from app.utils.quotes import get_random_quote
from flask import Flask, render_template, request, redirect, url_for, session, flash, Blueprint
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_restx import Api, Resource
from flask_login import login_user, logout_user, login_required, current_user
from flask_dance.contrib.google import make_google_blueprint, google
from flask_cors import CORS
import os

from app.routes.auth import auth_bp
from app.routes.reviews import reviews_bp
from app.routes.courses import courses_bp
from app.routes.profile import profile_bp
from app.routes.news import news_bp
from app.config import Config
from app.database import db
from app.dependences import bcrypt, login_manager
from app.models.user import User
from app.models.course import Course
from app.models.news import News

def create_app():
    app = Flask(__name__)
    app.secret_key = os.urandom(24)
    app.config.from_object(Config)
    CORS(app)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(courses_bp)
    app.register_blueprint(reviews_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(news_bp)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.route('/')
    def index():
        news_items = News.query.order_by(News.date.desc()).limit(6).all()
        courses = Course.query.limit(3).all()
        selected_quote = get_random_quote()
        
        if current_user.is_authenticated:
            return render_template('index.html', username=current_user.username, news_items=news_items, courses=courses, quote=selected_quote)
        
        return render_template('index.html', news_items=news_items, courses=courses, quote=selected_quote)
    
    with app.app_context():
        db.create_all()

    @app.route('/about')
    def about():
        return render_template('about.html')
    
    @app.route('/settings')
    @login_required
    def settings():
        return render_template('settings.html')

    @app.after_request
    def add_no_cache_headers(response):
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host="127.0.0.1", port=5000)
