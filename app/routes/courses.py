import subprocess
from app.models.interest import Interest
from app.models.lesson import Lesson
from app.models.programming_language import ProgrammingLanguage
from app.models.review_vote import ReviewVote
from app.models.user import User
from app.models.platform_review import PlatformReview
from app.models.lesson_progress import LessonProgress
from app.models.user_activity import UserActivity
from flask import Flask, render_template, request, redirect, url_for, session, flash, Blueprint, jsonify, Response, stream_with_context, abort
from flask_login import login_user, logout_user, login_required, current_user
from app.database import db
from app.models import Course, Quiz, Progress, QuizAttempt, Module
import re
import markdown
import ollama
import html
import logging
from datetime import timedelta
from ..data.decorators import role_required
from slugify import slugify

logging.basicConfig(level=logging.DEBUG)  # или INFO в проде
logger = logging.getLogger(__name__)

courses_bp = Blueprint("courses", __name__)

@courses_bp.route('/courses', methods=['GET'])
@login_required
def courses_main():
    search_query = request.args.get('search', '').strip()
    show_all = request.args.get('show_all') == 'on'
    category = request.args.get('category', '').lower()

    # Сопоставление slug категории к id интереса
    category_map = {
        'frontend': 1,
        'backend': 2,
        'uiux': 3,
        'datasci': 4,
        'mobile': 5,
        'ai': 6
    }

    user_interest_ids = [interest.id for interest in current_user.interests]

    base_filter = (Course.status == Course.STATUS_PUBLISHED)

    # Если передана категория и она валидна
    if category and category in category_map:
        category_id = category_map[category]
        # Показываем курсы, относящиеся к выбранной категории
        query = Course.query.join(Course.interests).filter(
            Interest.id == category_id,
            base_filter
        )
        # Если есть поисковый запрос, применяем фильтр
        if search_query:
            query = query.filter(
                (Course.title.ilike(f'%{search_query}%')) |
                (Course.description.ilike(f'%{search_query}%'))
            )
        courses = query.distinct().all()
        no_courses_found = not courses
    else:
        # Если категория не передана, показываем по интересам пользователя или все
        if show_all or not user_interest_ids:
            query = Course.query.filter(base_filter)
            if search_query:
                query = query.filter(
                    (Course.title.ilike(f'%{search_query}%')) |
                    (Course.description.ilike(f'%{search_query}%'))
                )
            courses = query.all()
        else:
            query = Course.query.join(Course.interests).filter(
                Interest.id.in_(user_interest_ids),
                base_filter
            )
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

    # Собираем все ID уроков в курсе
    all_lessons = (
        Lesson.query
        .join(Module)
        .filter(Module.course_id == course.id)
        .order_by(Module.position.asc(), Lesson.position.asc())
        .all()
    )

    # Прогресс по всем урокам
    lesson_ids = [lesson.id for lesson in all_lessons]
    progresses = LessonProgress.query.filter(
        LessonProgress.user_id == current_user.id,
        LessonProgress.lesson_id.in_(lesson_ids)
    ).all()
    progress_dict = {p.lesson_id: {'completed': p.is_completed()} for p in progresses}

    # Логируем для отладки:
    print("progress_dict:", progress_dict)

    try:
        if course not in current_user.courses:
            current_user.courses.append(course)
            db.session.commit()

            activity = UserActivity(
                user_id=current_user.id,
                activity_type='start_course',
                description=f'Пользователь начал изучать курс: "{course.title}"'
            )
            db.session.add(activity)
            db.session.commit()
            flash(f'Вы успешно начали курс "{course.title}"!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Произошла ошибка при начале курса.', 'error')
        print(f"Ошибка при добавлении курса: {e}")

    lesson_id = request.args.get('lesson_id', type=int)
    quizzes = []
    lesson = None

    if lesson_id:
        lesson = Lesson.query.get(lesson_id)
        if not lesson:
            flash('Урок не найден', 'error')
            return redirect(url_for('courses.course_detail', slug=slug))

        # Получаем все уроки курса в порядке модулей и уроков
        all_lessons = (
            Lesson.query
            .join(Module)
            .filter(Module.course_id == course.id)
            .order_by(Module.position.asc(), Lesson.position.asc())
            .all()
        )

        # Проверка: разрешён ли доступ к уроку
        lesson_index = next((i for i, l in enumerate(all_lessons) if l.id == lesson.id), None)
        if lesson_index is not None and lesson_index > 0:
            prev_lesson = all_lessons[lesson_index - 1]
            prev_progress = LessonProgress.query.filter_by(user_id=current_user.id, lesson_id=prev_lesson.id).first()

            prev_has_quiz = Quiz.query.filter_by(lesson_id=prev_lesson.id).count() > 0
            prev_completed = (
                (prev_progress and prev_progress.quiz_passed)
                if prev_has_quiz
                else (prev_progress and prev_progress.theory_viewed)
            )

            if not prev_completed:
                flash('Сначала завершите предыдущий урок, прежде чем переходить к следующему.', 'error')
                return redirect(url_for('courses.course_detail', slug=slug))

        # Markdown преобразование
        if lesson.content:
            lesson.content = markdown.markdown(lesson.content, extensions=['fenced_code', 'codehilite'])

        quizzes = Quiz.query.filter_by(lesson_id=lesson_id).all()

        # Обновляем прогресс урока
        lesson_progress = LessonProgress.query.filter_by(user_id=current_user.id, lesson_id=lesson.id).first()
        if not lesson_progress:
            lesson_progress = LessonProgress(user_id=current_user.id, lesson_id=lesson.id)
            db.session.add(lesson_progress)

        if lesson.content and not lesson_progress.theory_viewed:
            lesson_progress.theory_viewed = True

        if quizzes:
            # Прохождение теста должно фиксироваться отдельно
            pass
        else:
            # Если тестов нет — урок считается завершён после просмотра
            if not lesson_progress.quiz_passed:
                lesson_progress.quiz_passed = True

        db.session.commit()

        return render_template('course_learning.html', course=course, lesson=lesson, quizzes=quizzes, progress_dict=progress_dict)

    # Если урок не выбран — показываем модули курса
    modules = course.modules
    return render_template('course_learning.html', course=course, modules=modules, progress_dict=progress_dict)

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
    logger.debug(f"➡️ Вход в course_quiz: slug={slug}, id={id}, method={request.method}")

    course = Course.query.filter_by(slug=slug).first()
    if not course:
        flash('Курс не найден', 'error')
        return redirect(url_for('courses.courses_main'))

    quiz = Quiz.query.get(id)
    if not quiz or not quiz.lesson or not quiz.lesson.module or quiz.lesson.module.course_id != course.id:
        flash('Квиз не найден', 'error')
        return redirect(url_for('courses.courses_main'))

    # Сессионные ключи
    session_key = f'{slug}_{id}_q_index'
    score_key = f'{slug}_{id}_score'
    attempt_recorded_key = f'{slug}_{id}_attempt_recorded'
    current_attempt_id_key = f'{slug}_{id}_current_attempt_id'

    if request.args.get('restart'):
        logger.info(f"🔄 Рестарт квиза. Очистка сессии")
        session.pop(session_key, None)
        session.pop(score_key, None)
        session.pop(attempt_recorded_key, None)
        session.pop(current_attempt_id_key, None)
        session['restart_quiz'] = True
        return redirect(url_for('courses.course_quiz', slug=slug, id=id))

    referer = request.headers.get('Referer', '')
    if not request.args.get('restart'):
        existing_attempt = QuizAttempt.query.filter_by(user_id=current_user.id, quiz_id=quiz.id).order_by(QuizAttempt.id.desc()).first()
        if existing_attempt and 'lesson' in referer:
            logger.info(f"✅ Есть предыдущая попытка по этому квизу. Перенаправляем на результат.")
            return redirect(url_for('courses.course_result', slug=slug, id=id))

    return quiz_page(course, quiz, session_key, score_key, attempt_recorded_key, current_attempt_id_key)

def quiz_page(course, quiz, session_key, score_key, attempt_recorded_key, current_attempt_id_key):
    logger.debug(f"➡️ Вход в quiz_page")

    questions = list(quiz.questions)
    if not questions:
        flash('В этом квизе нет вопросов', 'error')
        return redirect(url_for('courses.course_result', slug=course.slug, id=quiz.id))

    # Инициализация сессионных значений, если их нет
    session.setdefault(session_key, 0)
    session.setdefault(score_key, 0)
    session.setdefault(attempt_recorded_key, False)

    q_index = session[session_key]

    # При рестарте просто сбрасываем сессионные переменные
    if session.pop('restart_quiz', False):
        logger.info("🔄 Рестарт квиза, сброс сессии")
        session[session_key] = 0
        session[score_key] = 0
        session[attempt_recorded_key] = False
        session.pop(current_attempt_id_key, None)
        q_index = 0  # Обновляем локальную переменную, чтобы не было конфликтов

    if request.method == 'POST':
        answer = request.form.get('answer')
        correct_answer = questions[q_index].answer

        # Создаём новую попытку при первом ответе (если ещё не создана)
        attempt_id = session.get(current_attempt_id_key)
        if not attempt_id:
            attempt = QuizAttempt(user_id=current_user.id, quiz_id=quiz.id, score=0)
            db.session.add(attempt)
            db.session.commit()
            session[current_attempt_id_key] = attempt.id
            logger.info(f"🆕 Создана новая попытка: id={attempt.id}")

        if answer == correct_answer:
            session[score_key] += 1
            logger.info(f"🎉 Верно. Очки: {session[score_key]}")
        else:
            logger.info("❌ Неверно")

        session[session_key] += 1
        q_index = session[session_key]  # обновляем для проверки дальше

        # Если вопросы закончились, сохраняем результат
        if q_index >= len(questions):
            final_score = session.get(score_key, 0)
            attempt = db.session.get(QuizAttempt, session[current_attempt_id_key])
            if attempt:
                attempt.score = final_score
                db.session.commit()
                logger.info(f"📝 Попытка сохранена в момент завершения POST: id={attempt.id}, score={final_score}")

                # ✅ Обновляем LessonProgress
                try:
                    progress = LessonProgress.query.filter_by(user_id=current_user.id, lesson_id=quiz.lesson.id).first()
                    if not progress:
                        progress = LessonProgress(user_id=current_user.id, lesson_id=quiz.lesson.id)

                    progress.quiz_passed = True

                    if progress.is_completed() and not progress.completed_at:
                        progress.mark_completed()

                    db.session.add(progress)
                    db.session.commit()
                    logger.info(f"📚 LessonProgress обновлён: quiz_passed=True, is_completed={progress.is_completed()}")
                except Exception as e:
                    db.session.rollback()
                    logger.error(f"❌ Ошибка при обновлении LessonProgress: {e}")

                # 📌 Добавляем запись об активности
                try:
                    activity = UserActivity(
                        user_id=current_user.id,
                        activity_type='quiz_completed',
                        description=f'Прошёл квиз: "{quiz.title}" (Урок: "{quiz.lesson.title}") — Балл: {final_score} из {len(questions)}'
                    )
                    db.session.add(activity)
                    db.session.commit()
                    logger.info(f"🟢 Активность записана: {activity.description}")
                except Exception as e:
                    db.session.rollback()
                    logger.error(f"❌ Ошибка при записи активности: {e}")
                    flash(f"Ошибка при сохранении активности: {e}", 'error')

            session[attempt_recorded_key] = True
            return redirect(url_for('courses.course_result', slug=course.slug, id=quiz.id))

        # Иначе переходим к следующему вопросу
        return redirect(url_for('courses.course_quiz', slug=course.slug, id=quiz.id))

    # Если все вопросы пройдены
    if q_index >= len(questions):
        logger.info("🏁 Квиз завершён (GET)")

        if session.get(attempt_recorded_key):
            logger.info("🔁 Попытка уже была записана ранее, просто завершаем")

        else:
            final_score = session.get(score_key, 0)
            try:
                attempt_id = session.get(current_attempt_id_key)
                if attempt_id:
                    attempt = db.session.get(QuizAttempt, attempt_id)
                    if attempt:
                        attempt.score = final_score
                        db.session.commit()
                        logger.info(f"📝 Попытка обновлена (GET): id={attempt.id}, score={final_score}")
                else:
                    logger.warning("⚠️ Не найден ID текущей попытки — создаём заново")
                    attempt = QuizAttempt(user_id=current_user.id, quiz_id=quiz.id, score=final_score)
                    db.session.add(attempt)
                    db.session.commit()
                    logger.info(f"🆕 Попытка создана (GET): id={attempt.id}, score={final_score}")

                # 📌 Добавляем запись об активности
                activity = UserActivity(
                    user_id=current_user.id,
                    activity_type='quiz_completed',
                    description=f'Прошёл квиз: "{quiz.title}" (Урок: "{quiz.lesson.title}") — Балл: {final_score} из {len(questions)}'
                )
                db.session.add(activity)
                db.session.commit()
                logger.info(f"🟢 Активность записана: {activity.description}")

            except Exception as e:
                db.session.rollback()
                logger.error(f"❌ Ошибка при сохранении попытки или активности: {e}")
                flash(f'Ошибка при сохранении попытки: {e}', 'error')

            session[attempt_recorded_key] = True

        # Очистка сессии после завершения
        session.pop(session_key, None)
        session.pop(score_key, None)
        session.pop(current_attempt_id_key, None)

        return redirect(url_for('courses.course_result', slug=course.slug, id=quiz.id))

    # Если тест не завершён — показываем следующий вопрос
    question = questions[q_index]
    options = [opt.strip() for opt in re.split(r',\s*', question.options)]

    return render_template('quiz.html',
                           quiz=quiz,
                           question=question,
                           options=options,
                           index=q_index + 1,
                           total=len(questions),
                           progress=(q_index / len(questions)) * 100,
                           slug=course.slug,
                           id=quiz.id)

@courses_bp.route('/course/<slug>/quiz/<int:id>/result', methods=['GET'])
@login_required
def course_result(slug, id):
    course = Course.query.filter_by(slug=slug).first()
    if not course:
        flash('Курс не найден', 'error')
        return redirect(url_for('courses.courses_main'))

    quiz = Quiz.query.get(id)
    if not quiz:
        flash('Квиз не найден', 'error')
        return 'Квиз не найден', 404

    score = session.get(f'{slug}_{id}_score', 0)
    total = len(quiz.questions)

    last_attempt = QuizAttempt.query.filter_by(user_id=current_user.id, quiz_id=quiz.id).order_by(QuizAttempt.id.desc()).first()

    stats = {
        "attempts": QuizAttempt.query.filter_by(user_id=current_user.id, quiz_id=quiz.id).count(),
        "best_score": db.session.query(db.func.max(QuizAttempt.score)).filter_by(user_id=current_user.id, quiz_id=quiz.id).scalar() or 0,
        "last_score": last_attempt.score if last_attempt else None,
        "last_attempt_date": last_attempt.attempt_date + timedelta(hours=5) if last_attempt else None  # исправлено поле
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
    if vote_type not in ['like', 'dislike']:
        return jsonify({'success': False, 'error': 'Неверный тип голоса.'}), 400

    review = PlatformReview.query.get_or_404(review_id)
    existing_vote = ReviewVote.query.filter_by(review_id=review_id, user_id=current_user.id).first()

    try:
        author_name = review.user.username if review.user else 'Неизвестный пользователь'
        logger.debug(f"📌 Автор отзыва: {author_name}")

        if existing_vote:
            if existing_vote.vote_type != vote_type:
                if existing_vote.vote_type == 'like':
                    review.likes_count -= 1
                elif existing_vote.vote_type == 'dislike':
                    review.dislikes_count -= 1

                if vote_type == 'like':
                    review.likes_count += 1
                elif vote_type == 'dislike':
                    review.dislikes_count += 1

                existing_vote.vote_type = vote_type
                db.session.commit()

                activity = UserActivity(
                    user_id=current_user.id,
                    activity_type='review_vote_changed',
                    description=f'Изменил голос на "{vote_type}" для отзыва пользователя {author_name}: "{review.content}"'
                )
                db.session.add(activity)
                db.session.commit()

                return jsonify({
                    'success': True,
                    'likes_count': review.likes_count,
                    'dislikes_count': review.dislikes_count
                })
            else:
                return jsonify({'success': False, 'error': 'Вы уже проголосовали таким образом.'}), 400
        else:
            new_vote = ReviewVote(review_id=review_id, user_id=current_user.id, vote_type=vote_type)
            db.session.add(new_vote)

            if vote_type == 'like':
                review.likes_count += 1
            elif vote_type == 'dislike':
                review.dislikes_count += 1

            db.session.commit()

            activity = UserActivity(
                user_id=current_user.id,
                activity_type='review_vote',
                description=f'Проголосовал "{vote_type}" за отзыв пользователя {author_name}: "{review.content[:50]}..."'
            )
            db.session.add(activity)
            db.session.commit()

            return jsonify({
                'success': True,
                'likes_count': review.likes_count,
                'dislikes_count': review.dislikes_count
            })

    except Exception as e:
        db.session.rollback()
        logger.error(f'❌ Ошибка при голосовании: {e}')
        return jsonify({'success': False, 'error': 'Ошибка на сервере.'}), 500

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

@courses_bp.route("/course/create/step1", methods=["GET", "POST"])
@login_required
@role_required('teacher')
def course_create_step1():
    languages = ProgrammingLanguage.query.all()
    interests = Interest.query.order_by(Interest.id).all()

    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        interest_id = request.form["interest_id"]

        # Безопасно получить language_id, может быть пустым
        language_id = request.form.get("language_id")
        if not language_id:
            language_id = None
        else:
            language_id = int(language_id)

        slug = slugify(title)

        if Course.query.filter_by(slug=slug).first():
            flash("Курс с таким названием уже существует", "danger")
            return redirect(url_for("courses.course_create_step1"))

        new_course = Course(
            title=title,
            description=description,
            teacher=current_user.username,
            slug=slug,
            language_id=language_id,
            status=Course.STATUS_DRAFT,
            author_id=current_user.id
        )

        db.session.add(new_course)
        db.session.commit()

        activity = UserActivity(
            user_id=current_user.id,
            activity_type='course_created',
            description=f'Вы создали курс: "{new_course.title}"'
        )
        db.session.add(activity)
        db.session.commit()

        interest = Interest.query.get(interest_id)
        if interest:
            new_course.associated_interests.append(interest)
            db.session.commit()

        flash("Шаг 1 завершён. Теперь добавьте модули и уроки.", "success")
        return redirect(url_for("courses.course_create_edit", course_id=new_course.id))

    return render_template("course_create_step1.html", languages=languages, interests=interests)

@courses_bp.route('/course/create/<int:course_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('teacher')
def course_create_edit(course_id):
    course = Course.query.get_or_404(course_id)

    if course.author_id != current_user.id:
        flash("Вы не являетесь автором этого курса и не можете его редактировать.", "danger")
        return redirect(url_for("courses.courses_main"))

    if request.method == 'POST':
        action = request.form.get('action')

        if course.status == Course.STATUS_PUBLISHED:
            course.status = Course.STATUS_DRAFT
            db.session.commit()
            flash("Курс переведён в черновик из-за редактирования.", "warning")

        if action == 'add_module':
            title = request.form.get('module_title')
            position = request.form.get('module_position', type=int) or 0
            if title:
                module = Module(course_id=course.id, title=title, position=position)
                db.session.add(module)
                db.session.commit()
                flash(f"Модуль '{title}' добавлен", "success")

                activity = UserActivity(
                    user_id=current_user.id,
                    activity_type='module_added',
                    description=f"Вы добавили модуль '{title}' в курс '{course.title}'"
                )
                db.session.add(activity)
                db.session.commit()

        elif action == 'edit_module':
            module_id = request.form.get('module_id', type=int)
            title = request.form.get('module_title')
            position = request.form.get('module_position', type=int) or 0

            module = Module.query.get(module_id)
            if module and module.course_id == course.id:
                if title:
                    module.title = title
                    module.position = position
                    db.session.commit()
                    flash(f"Модуль '{title}' обновлён", "success")

                    activity = UserActivity(
                        user_id=current_user.id,
                        activity_type='module_edited',
                        description=f"Вы обновили модуль '{title}' в курсе '{course.title}'"
                    )
                    db.session.add(activity)
                    db.session.commit()
                else:
                    flash("Название модуля не может быть пустым.", "warning")

        elif action == 'delete_module':
            module_id = request.form.get('module_id', type=int)
            module = Module.query.get(module_id)
            if module and module.course_id == course.id:
                Lesson.query.filter_by(module_id=module.id).delete()
                db.session.delete(module)
                db.session.commit()
                flash(f"Модуль '{module.title}' удалён", "success")

                activity = UserActivity(
                    user_id=current_user.id,
                    activity_type='module_deleted',
                    description=f"Вы удалили модуль '{module.title}' из курса '{course.title}'"
                )
                db.session.add(activity)
                db.session.commit()

        elif action == 'add_lesson':
            module_id = request.form.get('module_id', type=int)
            title = request.form.get('lesson_title')
            position = request.form.get('lesson_position', type=int) or 0
            content = request.form.get('lesson_content', '')

            if title and module_id:
                lesson = Lesson(module_id=module_id, title=title, position=position, content=content)
                db.session.add(lesson)
                db.session.commit()
                flash(f"Урок '{title}' добавлен", "success")

                activity = UserActivity(
                    user_id=current_user.id,
                    activity_type='lesson_added',
                    description=f"Вы добавили урок '{title}' в курс '{course.title}'"
                )
                db.session.add(activity)
                db.session.commit()
            else:
                flash("Название урока и модуль обязательны.", "warning")

        elif action == 'edit_lesson':
            lesson_id = request.form.get('lesson_id', type=int)
            title = request.form.get('lesson_title')
            content = request.form.get('lesson_content', '')
            position = request.form.get('lesson_position', type=int) or 0

            lesson = Lesson.query.get(lesson_id)
            if lesson and lesson.module.course_id == course.id:
                if title:
                    lesson.title = title
                    lesson.content = content
                    lesson.position = position
                    db.session.commit()
                    flash(f"Урок '{title}' обновлён", "success")

                    activity = UserActivity(
                        user_id=current_user.id,
                        activity_type='lesson_edited',
                        description=f"Вы обновили урок '{title}' в курсе '{course.title}'"
                    )
                    db.session.add(activity)
                    db.session.commit()
                else:
                    flash("Название урока не может быть пустым.", "warning")

        elif action == 'delete_lesson':
            lesson_id = request.form.get('lesson_id', type=int)
            lesson = Lesson.query.get(lesson_id)
            if lesson and lesson.module.course_id == course.id:
                db.session.delete(lesson)
                db.session.commit()
                flash(f"Урок '{lesson.title}' удалён", "success")

                activity = UserActivity(
                    user_id=current_user.id,
                    activity_type='lesson_deleted',
                    description=f"Вы удалили урок '{lesson.title}' из курса '{course.title}'"
                )
                db.session.add(activity)
                db.session.commit()

        elif action == 'publish_course':
            if course.status != Course.STATUS_PUBLISHED:
                course.status = Course.STATUS_PUBLISHED
                db.session.commit()
                flash("Курс успешно опубликован!", "success")

                activity = UserActivity(
                    user_id=current_user.id,
                    activity_type='course_published',
                    description=f"Вы опубликовали курс '{course.title}'"
                )
                db.session.add(activity)
                db.session.commit()
            else:
                flash("Курс уже опубликован.", "info")

        return redirect(url_for("courses.course_create_edit", course_id=course.id))

    modules = Module.query.filter_by(course_id=course.id).order_by(Module.position).all()
    return render_template('course_create_edit.html', course=course, modules=modules)
