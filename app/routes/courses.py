import subprocess
from app.models.interest import Interest
from app.models.lesson import Lesson
from app.models.review_vote import ReviewVote
from app.models.user import User
from app.models.platform_review import PlatformReview
from app.models.lesson_progress import LessonProgress
from flask import Flask, render_template, request, redirect, url_for, session, flash, Blueprint, jsonify, Response, stream_with_context
from flask_login import login_user, logout_user, login_required, current_user
from app.database import db
from app.models import Course, Quiz, Progress, QuizAttempt
import re
import markdown
import ollama
import html

courses_bp = Blueprint("courses", __name__)

@courses_bp.route('/courses', methods=['GET'])
@login_required
def courses_main():
    search_query = request.args.get('search', '').strip()
    show_all = request.args.get('show_all') == 'on'

    user_interest_ids = [interest.id for interest in current_user.interests]

    if show_all or not user_interest_ids:
        # Показываем все курсы, если выбрана галочка "Показать все" или у пользователя нет интересов
        if search_query:
            courses = Course.query.filter(
                (Course.title.ilike(f'%{search_query}%')) |
                (Course.description.ilike(f'%{search_query}%'))
            ).all()
        else:
            courses = Course.query.all()
    else:
        # Показываем только курсы по интересам
        query = Course.query.join(Course.interests).filter(Interest.id.in_(user_interest_ids))

        if search_query:
            query = query.filter(
                (Course.title.ilike(f'%{search_query}%')) |
                (Course.description.ilike(f'%{search_query}%'))
            )

        courses = query.distinct().all()

    no_courses_found = not courses and not show_all

    return render_template('courses.html', courses=courses, no_courses_found=no_courses_found, show_all=show_all, search_query=search_query)

@courses_bp.route('/course/<slug>', methods=['GET'])
@login_required
def course_detail(slug):
    course = Course.query.filter_by(slug=slug).first()

    if not course:
        flash('Курс не найден', 'error')
        return redirect(url_for('courses.courses_main'))  

    # Извлекаем модули курса
    modules = course.modules  # Все модули этого курса

    return render_template('course.html', course=course, modules=modules)

@courses_bp.route('/course/<slug>/learning', methods=['GET'])
@login_required
def course_learning(slug):
    course = Course.query.filter_by(slug=slug).first()

    if not course:
        flash('Курс не найден', 'error')
        return redirect(url_for('courses.courses_main'))

    if course not in current_user.courses:
        current_user.courses.append(course)
        db.session.commit()
        flash(f'Вы успешно начали курс "{course.title}"!', 'success')

    lesson_id = request.args.get('lesson_id', type=int)

    quizzes = []

    lesson = None
    if lesson_id:
        lesson = Lesson.query.get(lesson_id)
        if not lesson:
            flash('Урок не найден', 'error')
            return redirect(url_for('courses.course_detail', slug=slug))

        # Markdown преобразование
        if lesson.content:
            lesson.content = markdown.markdown(lesson.content, extensions=['fenced_code', 'codehilite'])

        # Получаем квизы по уроку
        quizzes = Quiz.query.filter_by(lesson_id=lesson_id).all()

        # Обновляем прогресс урока
        lesson_progress = LessonProgress.query.filter_by(user_id=current_user.id, lesson_id=lesson.id).first()
        if not lesson_progress:
            lesson_progress = LessonProgress(user_id=current_user.id, lesson_id=lesson.id)
            db.session.add(lesson_progress)

        if lesson.content and not lesson_progress.theory_viewed:
            lesson_progress.theory_viewed = True

        if lesson_progress.completed_tasks is None:
            lesson_progress.completed_tasks = []

        completed_task_ids = [task.id for task in lesson.tasks if task.is_completed]
        lesson_progress.completed_tasks.extend(completed_task_ids)

        if lesson_progress.is_completed(len(lesson.tasks)):
            lesson_progress.mark_completed()

        db.session.commit()

        return render_template('course_learning.html', course=course, lesson=lesson, quizzes=quizzes)

    # Если урок не выбран — показываем модули курса
    modules = course.modules
    return render_template('course_learning.html', course=course, modules=modules)

@courses_bp.route('/course/<slug>/learning/<int:lesson_id>/details', methods=['GET'])
@login_required
def course_learning_detail(slug, lesson_id):
    course = Course.query.filter_by(slug=slug).first()
    lesson = Lesson.query.get(lesson_id)

    # Получаем квизы, привязанные к данному уроку
    quizzes = Quiz.query.filter_by(lesson_id=lesson_id).all()

    return render_template('course_learning.html', course=course, lesson=lesson, quizzes=quizzes)

@courses_bp.route('/course/<slug>/quiz/<int:id>', methods=['GET', 'POST'])
@login_required
def course_quiz(slug, id):
    course = Course.query.filter_by(slug=slug).first()
    if not course:
        flash('Курс не найден', 'error')
        return redirect(url_for('courses.courses_main'))

    quiz = Quiz.query.filter_by(id=id).first()
    if not quiz or not quiz.lesson or not quiz.lesson.module or quiz.lesson.module.course.id != course.id:
        flash('Квиз не найден', 'error')
        return redirect(url_for('courses.courses_main'))

    # Проверяем, есть ли уже попытки прохождения этого теста у пользователя
    progress = Progress.query.filter_by(user_id=current_user.id, course_id=course.id).first()
    has_attempts = False
    if progress:
        attempt = QuizAttempt.query.filter_by(progress_id=progress.id, quiz_id=quiz.id).first()
        has_attempts = attempt is not None

    # Если есть попытки и не запрошен рестарт - перенаправляем на результаты
    if has_attempts and not request.args.get('restart'):
        return redirect(url_for('courses.course_result', slug=slug, id=id))

    session_key = f'{slug}_{id}_q_index'
    score_key = f'{slug}_{id}_score'
    attempt_recorded_key = f'{slug}_{id}_attempt_recorded'

    # Если запрошен рестарт — сбрасываем прогресс в сессии
    if request.args.get('restart'):
        session[session_key] = 0
        session.pop(score_key, None)
        session.pop(attempt_recorded_key, None)

    # Инициализация индекса вопроса, если нет
    if session_key not in session:
        session[session_key] = 0

    questions = quiz.questions  # список вопросов

    # Если вопросов нет — сразу редирект на результат
    if not questions:
        flash('В этом квизе нет вопросов', 'error')
        return redirect(url_for('courses.course_result', slug=slug, id=id))

    # Обработка ответа пользователя
    if request.method == 'POST':
        q_index = session.get(session_key, 0)
        answer = request.form.get('answer')
        correct = questions[q_index].answer

        if answer == correct:
            session[score_key] = session.get(score_key, 0) + 1

        # Переходим к следующему вопросу
        session[session_key] = q_index + 1

        # Если вопросы закончились — записываем результат и идём на страницу результата
        if session[session_key] >= len(questions):
            if not session.get(attempt_recorded_key):
                if not progress:
                    progress = Progress(user_id=current_user.id, course_id=course.id)
                    db.session.add(progress)
                    db.session.commit()
                attempt = QuizAttempt(progress_id=progress.id, quiz_id=quiz.id, score=session.get(score_key, 0))
                db.session.add(attempt)
                db.session.commit()
                session[attempt_recorded_key] = True

            return redirect(url_for('courses.course_result', slug=slug, id=id))

        # Иначе — следующий вопрос
        return redirect(url_for('courses.course_quiz', slug=slug, id=id))

    # Отображение вопроса: если индекс за пределами — показываем результат
    q_index = session.get(session_key, 0)
    if q_index >= len(questions):
        return redirect(url_for('courses.course_result', slug=slug, id=id))

    question = questions[q_index]
    options = [opt.strip() for opt in re.split(r',\s*', question.options)]

    return render_template('quiz.html', quiz=quiz, question=question,
                         options=options,
                         index=q_index, total=len(questions),
                         progress=(q_index / len(questions)) * 100,
                         slug=slug, id=id)

@courses_bp.route('/course/<slug>/quiz/<int:id>/result', methods=['GET'])
@login_required
def course_result(slug, id):
    course = Course.query.filter_by(slug=slug).first()
    if not course:
        flash('Курс не найден', 'error')
        return redirect(url_for('courses.courses_main'))

    quiz = Quiz.query.filter_by(id=id).first()
    if not quiz:
        flash('Квиз не найден', 'error')
        return 'Квиз не найден', 404

    score = session.get(f'{slug}_{id}_score', 0)
    total = len(quiz.questions)

    progress = Progress.query.filter_by(user_id=current_user.id, course_id=course.id).first()

    stats = progress.get_quiz_stats(quiz.id) if progress else {
        "attempts": 0,
        "best_score": 0,
        "last_score": None,
        "last_attempt_date": None
    }

    return render_template('result.html', score=score, total=total, slug=slug, id=id, stats=stats)

@courses_bp.route('/about')
def about():
    student_count = User.query.count()
    course_count = Course.query.count()
    review_count = PlatformReview.query.count()  # Подсчёт отзывов

    platform_reviews = PlatformReview.query.order_by(PlatformReview.created_at.desc()).limit(9).all()

    return render_template(
        'about.html',
        student_count=student_count,
        course_count=course_count,
        review_count=review_count,
        platform_reviews=platform_reviews
    )

@courses_bp.route('/review/<int:review_id>/vote/<vote_type>', methods=['POST'])
@login_required
def vote(review_id, vote_type):
    # Проверяем, что переданный тип голоса корректен
    if vote_type not in ['like', 'dislike']:
        return jsonify({'success': False, 'error': 'Неверный тип голоса.'}), 400

    # Проверяем, есть ли уже голос текущего пользователя
    existing_vote = ReviewVote.query.filter_by(review_id=review_id, user_id=current_user.id).first()

    review = PlatformReview.query.get_or_404(review_id)

    if existing_vote:
        # Если текущий голос отличается от нового, изменяем его
        if existing_vote.vote_type != vote_type:
            # Обновляем количество голосов на отзыве
            if existing_vote.vote_type == 'like':
                review.likes_count -= 1
            elif existing_vote.vote_type == 'dislike':
                review.dislikes_count -= 1
            
            if vote_type == 'like':
                review.likes_count += 1
            elif vote_type == 'dislike':
                review.dislikes_count += 1

            # Обновляем голос
            existing_vote.vote_type = vote_type
            db.session.commit()

            return jsonify({
                'success': True,
                'likes_count': review.likes_count,
                'dislikes_count': review.dislikes_count
            })
        else:
            return jsonify({'success': False, 'error': 'Вы уже проголосовали таким образом.'}), 400
    else:
        # Если голосов не было, создаём новый
        new_vote = ReviewVote(review_id=review_id, user_id=current_user.id, vote_type=vote_type)
        db.session.add(new_vote)

        if vote_type == 'like':
            review.likes_count += 1
        elif vote_type == 'dislike':
            review.dislikes_count += 1

        db.session.commit()

        return jsonify({
            'success': True,
            'likes_count': review.likes_count,
            'dislikes_count': review.dislikes_count
        })

@courses_bp.route('/chat-stream', methods=['POST'])
def chat_ai():
    data = request.get_json()
    message = data.get("message", "").strip()
    context = data.get("context", "").strip()

    if not message:
        return Response("data: Ошибка: пустой вопрос\n\n", mimetype="text/event-stream")

    if not context:  # защита от слишком короткого/пустого урока
        return Response("data: ❗ Ошибка: текст урока отсутствует. ИИ не сможет вам здесь помочь.\n\n", mimetype="text/event-stream")

    messages = [
        {
            "role": "system",
            "content": (
                "Ты — опытный AI-наставник. Твоя задача — помогать ученикам разного уровня разбираться в учебном материале. "
                "Тебе дан текст урока и вопрос от пользователя. Работай по следующим правилам:\n\n"
                
                "1. **Если вопрос по теме урока**:\n"
                "   – Объясни понятным языком, как хороший учитель.\n"
                "   – Не повторяй дословно текст урока — перефразируй, дополняй, приводи аналогии и объясняй суть.\n"
                "   – Добавляй ценную информацию, примеры или подсказки, если это уместно.\n"
                "   – Если вопрос — от новичка, используй простой и дружелюбный тон.\n"
                "   – Если видно, что спрашивает опытный пользователь — допускается использовать профессиональную терминологию.\n\n"

                "2. **Если вопрос не по теме урока**:\n"
                "   – Вежливо сообщи, что вопрос не относится к текущему уроку.\n"
                "   – Предложи задать вопрос по теме.\n\n"

                "3. **Язык ответа**:\n"
                "   – **Всегда отвечай на том языке, на котором был задан вопрос.**\n"
                "   – **Никогда не меняй язык ответа**, даже если текст урока на другом языке.\n\n"

                "4. **Тон общения**:\n"
                "   – Дружелюбный, неформальный, поддерживающий.\n"
                "   – Но при этом профессиональный и полезный."
            )
        },
        {
            "role": "user",
            "content": f"Текст урока:\n{context[:3000]}\n\nВопрос: {message}"
        }
    ]

    def generate():
        try:
            buffer = ""
            for chunk in ollama.chat(model="mistral", messages=messages, stream=True):
                content = chunk.get("message", {}).get("content", "")
                if content:
                    buffer += content
                    if "\n" in buffer:
                        parts = buffer.split("\n")
                        for part in parts[:-1]:
                            yield f"data: {html.escape(part.strip())}\n\n"
                        buffer = parts[-1]
            if buffer.strip():
                yield f"data: {html.escape(buffer.strip())}\n\n"
        except Exception as e:
            yield f"data: [Ошибка сервера] {str(e)}\n\n"

    return Response(stream_with_context(generate()), mimetype="text/event-stream")