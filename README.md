# Python CV Aggregator

Агрегатор вакансий по ключевому слову "python" с площадок hh.ru (парсинг) и superjob.ru (API + парсинг).

## С чего начать

### Окружение
Информация обо всех необходимых библиотеках содержится в файле requirements.txt
```
$ pip install -r requirements.txt
```

### В проекте используются сторонние библиотеки:
* [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) - парсинг страниц
* [Flask](http://flask.pocoo.org/) - веб-приложение
* [SQLAlchemy](http://www.sqlalchemy.org/) - создание базы данных, обработка данных
* [flask-paginate](https://github.com/lixxu/flask-paginate) - пагинация веб-страниц
* [sqlalchemy-pagination](https://github.com/wizeline/sqlalchemy-pagination) - предварительная пагинация информации из базы данных

