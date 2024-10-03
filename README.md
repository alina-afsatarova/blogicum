# Проект «Blogicum»
Социальная сеть для публикации личных дневников.
Сайт, на котором пользователь может создать свою страницу и публиковать на ней сообщения («посты»). 
Для каждого поста нужно указать категорию, а также опционально локацию, с которой связан пост. 
Пользователь может перейти на страницу любой категории и увидеть все посты, которые к ней относятся.
Пользователи смогут заходить на чужие страницы, читать и комментировать чужие посты.
Для своей страницы автор может задать имя и уникальный адрес.


## Технологии
Python, Django 3.2, Django ORM, SQL, SQLite, HTML, CSS, Bootstrap

## Как запустить проект
Клонировать репозиторий и перейти в него в командной строке:
```
git clone https://github.com/alina-afsatarova/blogicum.git
```
```
cd blogicum
```
Cоздать и активировать виртуальное окружение:
```
python3 -m venv env
```
```
source env/bin/activate
```
Установить зависимости из файла requirements.txt:
```
python3 -m pip install --upgrade pip
```
```
pip install -r requirements.txt
```
Выполнить миграции:
```
python3 manage.py migrate
```
Запустить проект:
```
python3 manage.py runserver
```
