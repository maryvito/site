import sys, os

sys.path.append(os.path.join('.', 'server'))
sys.path.append(os.path.join('.'))

from flask import Flask, render_template, request
from models import Resume, Keywords, db_session
from sqlalchemy import or_
from config_app import OUTPUT_PAGE_CONFIG, SITES_DICT, GENDERS_DICT
from flask_paginate import Pagination, get_page_parameter
from sqlalchemy_pagination import paginate


CITIES_LIST = sorted({item[0] for item in db_session.query(Resume.city)})

SALARY_MAX = max({item[0] for item in db_session.query(Resume.salary) if item[0] is not None})

BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

selected = {
    'salary_from': 0,
    'salary_to': SALARY_MAX,
    'gender': GENDERS_DICT.keys(),
    'site': SITES_DICT.keys(),
    'city': CITIES_LIST,
    'keyword': []
}

APP = Flask(
    __name__,
    template_folder=os.path.join(BASE_PATH, 'templates'),
    static_folder=os.path.join(BASE_PATH, 'static')
)

@APP.route('/', methods=['GET'])
def index(selected=selected):
    page = 1
    if request.args:
        selected['site'] = request.args.getlist('site')
        selected['keyword'] = request.args.getlist('keyword')
        selected['gender'] = request.args.getlist('gender')
        selected['city'] = request.args.getlist('city')
        selected['salary_from'] = request.args.get('salary_from', type=int)
        selected['salary_to'] = request.args.get('salary_to', type=int)
        page = request.args.get('page', type=int)

    resumes = db_session.query(Resume)

    KEYWORDS_LIST = sorted([item[0] for item in db_session.query(Keywords.keyword)])

    if len(selected['site']) == 1:
        for site in selected['site']:
            resumes = db_session.query(Resume).\
                filter(Resume.url.contains(site))

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

    sqlalchemy_pagination = paginate(resumes, 1, page_size=10)

    print(url_params_from_dict(selected))

    flask_pagination = Pagination(
                            page=page,
                            per_page=10,
                            total=resumes.count(),
                            record_name='резюме',
                            bs_version=3,
                            prev_label='<span class="glyphicon glyphicon-chevron-left" aria-hidden="false"></span>',
                            next_label='<span class="glyphicon glyphicon-chevron-right" aria-hidden="false"></span>',
                            display_msg='<b>{start}&ndash;{end}</b> {record_name} из <b>{total}</b> найденных',
                            href='/?page={0}& %s' % url_params_from_dict(selected)
                            )

    print(selected)

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


def url_params_from_dict(selected_params):
    
    url_string = ''

    for key in selected_params:
        if type(selected_params[key]) == type([]):
            for item in selected_params[key]:
                url_string = url_string + key + '=' + str(item) + '&'
        elif type(selected_params[key]) == type({}.keys()):
            for item in list(selected[key]):
                url_string = url_string + key + '=' + str(item) + '&'
        else:
            url_string = url_string + key + '=' + str(selected_params[key]) + '&'
    
    return url_string


if __name__ == '__main__':
    APP.run(debug=True)
