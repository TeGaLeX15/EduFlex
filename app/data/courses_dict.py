courses = {
    'Python': {
        'category': 'Python',
        'courses': [
            {
                'title': 'Python для начинающих',
                'description': 'Изучите основы Python с нуля.',
                'teacher': 'Иван Иванов',
                "rating": 4.8,
                "reviews": 1200,
                'slug': 'python-basics-1',
                'tasks': [
                    {
                        'title': 'Task 1',
                        'description': 'Напиши команду, которая выводит Hello World в консоль.',
                        'answer': 'print("Hello World")'
                    }
                ],
                'quizes': [
                    {
                        'title': 'Python Basics',
                        'questions': [
                            {
                                'text': 'What does `len("hello")` return?',
                                'options': ['4', '5', '6', 'error'],
                                'answer': '5'
                            },
                            {
                                'text': 'Which keyword is used to define a function?',
                                'options': ['function', 'define', 'def', 'func'],
                                'answer': 'def'
                            }
                        ]
                    }
                ]
            },
        ]
    },
    'Web-Development': {
        'category': 'Web-Development',
        'courses': [
            {
                'title': 'Веб-разработка',
                'description': 'Создайте современный сайт с HTML, CSS и JS.',
                'teacher': 'Ольга Смирнова',
                "rating": 4.7,
                "reviews": 980,
                'slug': 'web-basics-1',
                'tasks': [
                    {
                        'title': 'Task 1',
                        'description': 'Напиши команду, которая выводит Hello World в консоль.',
                        'answer': 'print("Hello World")'
                    }
                ],
                'quizes': [
                    {
                        'title': 'JavaScript Basics',
                        'questions': [
                            {
                                'text': 'What is the result of `typeof null`?',
                                'options': ['"object"', '"null"', '"undefined"', '"boolean"'],
                                'answer': '"object"'
                            },
                            {
                                'text': 'Which symbol is used for comments in JavaScript?',
                                'options': ['#', '//', '<!-- -->', '**'],
                                'answer': '//'
                            }
                        ]
                    }
                ]
            },
        ]
    },
    'UI/UX': {
        'category': 'UI/UX Design',
        'courses': [
            {
                'title': 'UI/UX Дизайн',
                'description': 'Изучите визуальные и пользовательские интерфейсы.',
                'teacher': 'Анна Козлова',
                "rating": 4.9,
                "reviews": 1100,
                'slug': 'ui-basics-1',
                'tasks': [
                    {
                        'title': 'Создание логотипа',
                        'description': 'Разработайте простой логотип для мобильного приложения в стиле минимализма. Используйте инструменты как Sketch или Figma.',
                        'answer': 'Логотип должен быть простым, с минималистичным подходом, например, с использованием геометрических фигур или текста, без лишних деталей.'
                    }
                ],
                'quizes': [
                    {
                        'title': 'Основы UI/UX дизайна',
                        'questions': [
                            {
                                'text': 'Что означает аббревиатура UI в контексте разработки?',
                                'options': ['User Interface', 'Universal Interface', 'User Interaction', 'Unified Interface'],
                                'answer': 'User Interface'
                            },
                            {
                                'text': 'Какая концепция является основой хорошего UX дизайна?',
                                'options': ['Удобство и эффективность взаимодействия', 'Цветовые схемы', 'Минимальное использование текста', 'Яркие изображения'],
                                'answer': 'Удобство и эффективность взаимодействия'
                            }
                        ]
                    }
                ]
            },
        ]
    }
}
