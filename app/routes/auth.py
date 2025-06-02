from flask import Blueprint, request, redirect, url_for, flash, render_template
from flask_login import login_user, logout_user, login_required, current_user
from app.database import db
from app.models.user import User
from app.models.interest import Interest
from flask import session, abort

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/onboarding")
def onboarding():
    if not session.get('show_onboarding'):
        abort(404)
    session.pop('show_onboarding')
    return render_template("onboarding.html")

@auth_bp.route('/onboarding/save_interest', methods=['POST'])
@login_required
def save_interests():
    try:
        # Получаем данные интересов из JSON
        interest_names = request.json.get('interests', [])

        if not interest_names:
            return {'status': 'error', 'message': 'No interests selected'}

        print(f"Selected interests: {interest_names}")

        # Ищем все интересы по их названиям
        interests = Interest.query.filter(Interest.name.in_(interest_names)).all()

        if not interests:
            return {'status': 'error', 'message': 'Selected interests not found'}

        print(f"Found interests: {[interest.name for interest in interests]}")

        # Добавляем найденные интересы, если их ещё нет у пользователя
        for interest in interests:
            if interest not in current_user.interests:
                current_user.interests.append(interest)

        # Сохраняем изменения в базе данных
        db.session.commit()

        return {'status': 'ok'}
    except Exception as e:
        print(f"Error occurred: {e}")
        db.session.rollback()  # Откатываем изменения в случае ошибки
        return {'status': 'error', 'message': str(e)}

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        if User.query.filter_by(username=username).first():
            flash("Этот username уже зарегистрирован!", "danger")
            return redirect(url_for("auth.register"))

        if User.query.filter_by(email=email).first():
            flash("Этот email уже зарегистрирован!", "danger")
            return redirect(url_for("auth.register"))

        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash("Регистрация успешна! Теперь войдите в систему.", "success")
        login_user(new_user)
        session['show_onboarding'] = True
        return redirect(url_for('auth.onboarding'))

    return render_template("register.html")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash("Вход выполнен!", "success")
            return redirect(url_for("index"))
        else:
            flash("Неверное имя пользователя или пароль!", "danger")

    return render_template("login.html")

@auth_bp.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    session.clear()
    logout_user()
    flash("Вы вышли из системы.", "info")
    return redirect(url_for("auth.login"))

@auth_bp.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    if request.method == "POST":
        current_password = request.form.get("current_password")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")

        if not current_user.check_password(current_password):
            flash("Текущий пароль неверен.", "danger")
            return redirect(url_for("auth.change_password"))

        if new_password != confirm_password:
            flash("Новые пароли не совпадают.", "danger")
            return redirect(url_for("auth.change_password"))

        current_user.set_password(new_password)
        db.session.commit()

        flash("Пароль успешно изменён!", "success")
        return redirect(url_for("auth.change_password"))

    return render_template("change_password.html")

@auth_bp.route("/delete_account", methods=["POST"])
@login_required
def delete_account():
    user = current_user

    db.session.delete(user)
    db.session.commit()

    logout_user()
    flash("Ваш аккаунт был удален.", "info")
    return redirect(url_for("index"))