import sys
import os
sys.path.append(os.path.join('.', 'server'))
sys.path.append(os.path.join('.'))
from flask import Flask, render_template, request
from models import Resume, Keywords, db_session
from sqlalchemy import or_
from config_app import OUTPUT_PAGE_CONFIG, SITES_DICT, GENDERS_DICT
from flask_paginate import Pagination
from sqlalchemy_pagination import paginate

BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# gets sorted list of cities from database
CITIES_LIST = sorted({item[0] for item in db_session.query(Resume.city)})

# gets max salary from database
SALARY_MAX = max({item[0] for item in db_session.query(Resume.salary) if item[0] is not None})

# gets sorted list of keywords from database
KEYWORDS_LIST = sorted([item[0] for item in db_session.query(Keywords.keyword)])

APP = Flask(
    __name__,
    template_folder=os.path.join(BASE_PATH, 'templates'),
    static_folder=os.path.join(BASE_PATH, 'static')
)


@APP.route('/', methods=['GET'])
def index(page=1):
    
    # default values for URL parameters
    selected = {
        'salary_none': 1,
        'salary_from': 0,
        'salary_to': SALARY_MAX,
        'gender': GENDERS_DICT.keys(),
        'site': SITES_DICT.keys(),
        'city': CITIES_LIST,
        'keyword': []
    }

    # values for URL parameters when form submitted
    if request.args:
        selected['site'] = request.args.getlist('site')
        selected['keyword'] = request.args.getlist('keyword')
        selected['gender'] = request.args.getlist('gender')
        selected['city'] = request.args.getlist('city')
        selected['salary_from'] = request.args.get('salary_from', type=int)
        selected['salary_to'] = request.args.get('salary_to', type=int)
        selected['salary_none'] = request.args.get('salary_none')
        page = request.args.get('page', type=int)

    # fetch and filter resumes from database
    resumes = filtering_database_query_by_selected_params(db_session.query(Resume), selected)

    # pagination of database query
    sqlalchemy_pagination = paginate(resumes, page, page_size=10)

    # pagination for rendered template
    flask_pagination = Pagination(
                            page=page,
                            per_page=10,
                            total=resumes.count(),
                            record_name='резюме',
                            bs_version=3,
                            prev_label='<span class="glyphicon glyphicon-chevron-left" aria-hidden="false"></span>',
                            next_label='<span class="glyphicon glyphicon-chevron-right" aria-hidden="false"></span>',
                            display_msg='<b>{start}&ndash;{end}</b> {record_name} из <b>{total}</b> найденных',
                            href='/?page={0}%s' % url_string_from_dict(selected)
                            )

    return render_template(
        'index.html',
        resumes=resumes.all(),
        pagination_items=sqlalchemy_pagination.items,
        selected=selected,
        flask_pagination=flask_pagination,
        KEYWORDS_LIST=KEYWORDS_LIST,
        OUTPUT_PAGE_CONFIG=OUTPUT_PAGE_CONFIG,
        GENDERS_DICT=GENDERS_DICT,
        SITES_DICT=SITES_DICT,
        CITIES_LIST=CITIES_LIST,
        SALARY_MAX=SALARY_MAX
        )


def filtering_database_query_by_selected_params(resumes, selected):

    """
        Gets a database query and dictionary of selected fields (URL parameters)
        and filters the query sequently.

        In: sqlalchemy.orm.query.Query(), dict()
        Out: sqlalchemy.orm.query.Query()

    """

    if len(selected['site']) == 1:
        for site in selected['site']:
            resumes = resumes.\
                filter(Resume.url.contains(site))

    if selected['city']:
        for item in selected['city']:
            resumes = resumes.\
                filter(Resume.city.in_(selected['city']))

    if len(selected['gender']) == 1:
        for gender in selected['gender']:
            resumes = resumes.\
                filter(Resume.gender == gender)

    if selected['keyword']:
        for keyword in selected['keyword']:
            resumes = resumes.\
                filter(Resume.keywords.contains(keyword))

    if selected['salary_from']:
        resumes = resumes.\
                filter(or_(Resume.salary >= selected['salary_from'], Resume.salary == None))

    if selected['salary_to']:
        resumes = resumes.\
                filter(or_(Resume.salary <= selected['salary_to'], Resume.salary == None))

    if not selected['salary_none']:
        resumes = resumes.\
                filter(Resume.salary != None)

    return resumes


def url_string_from_dict(selected_params):
    
    """
        Returns the part of URL string like:
        '&site=hh.ru&site=superjob.ru&site=...&gender=male&gender=female&salary_none=1&...'

        In: dict()
        Out: str()
    """

    url_string = ''

    for key in selected_params:
        if type(selected_params[key]) == type([]):
            for item in selected_params[key]:
                url_string = url_string + '&' + key + '=' + str(item)
        elif type(selected_params[key]) == type({}.keys()):
            for item in list(selected_params[key]):
                url_string = url_string + '&' + key + '=' + str(item)
        elif str(selected_params[key]) != 'None':
            url_string = url_string + '&' + key + '=' + str(selected_params[key])
    
    return url_string


if __name__ == '__main__':
    APP.run(debug=True)
