# Проект Yatube
Yatube - это социальная сеть. Пользователям предоставляется возможность создать учетную запись, публиковать и редактировать записи, подписываться на любимых авторов и комментировать посты.

### Запуск проекта локально

Клонируем репозиторий

```https://github.com/Tomsky11/hw05_final```

В дирректории hw05_final устанавливаем зависимости (предварительно установив и активировав виртуальное окружение)

```pip install -r requirements.txt```

Применяем миграции

```python manage.py migrate```

Собираем статику

```python manage.py collectstatic```

Заполняем БД начальными данными

```python manage.py loaddata dump.json```

Запускаем проект

```python manage.py runserver```


### Задействованные технологии
* Python 3.8.5
* Django 2.2.6