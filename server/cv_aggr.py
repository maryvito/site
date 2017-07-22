import sys, os

sys.path.append(os.path.join('.', 'server'))
sys.path.append(os.path.join('.'))

from flask import Flask, render_template, request
from models import Resume, Keywords, db_session
from sqlalchemy import or_
from config_app import OUTPUT_PAGE_CONFIG, SITE_DICT, GENDER_DICT
from flask_paginate import Pagination, get_page_parameter
from sqlalchemy_pagination import paginate



CITY_LIST = sorted({item[0] for item in db_session.query(Resume.city)})

SALARY_MAX = max({item[0] for item in db_session.query(Resume.salary) if item[0] is not None})

BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

APP = Flask(
    __name__,
    template_folder=os.path.join(BASE_PATH, 'templates'),
    static_folder=os.path.join(BASE_PATH, 'static')
)

@APP.route('/', methods=['GET'])
def index(selected_page=1,
          selected_salary_from=0,
          selected_salary_to=SALARY_MAX,
          selected_gender_list=GENDER_DICT.keys(),
          selected_site_list=SITE_DICT.keys(),
          selected_city_list=CITY_LIST,
          selected_keyword_list=[]):
    
    print(APP.static_url_path)

    if request.args:
        selected_site_list = request.args.getlist('site')
        selected_keyword_list = request.args.getlist('keyword')
        selected_gender_list = request.args.getlist('gender')
        selected_city_list = request.args.getlist('city')
        selected_salary_from = request.args.get('salary_from', type=int)
        selected_salary_to = request.args.get('salary_to', type=int)
        selected_page = request.args.get('page', type=int)

    resumes = db_session.query(Resume)

    KEYWORDS_LIST = sorted([item[0] for item in db_session.query(Keywords.keyword)])

    if len(selected_site_list) == 1:
        for site in selected_site_list:
            resumes = db_session.query(Resume).\
                filter(Resume.url.contains(site))

    if len(selected_gender_list) == 1:
        for gender in selected_gender_list:
            resumes = resumes.\
                filter(Resume.gender == gender)

    if selected_keyword_list:
        for keyword in selected_keyword_list:
            resumes = resumes.\
                filter(Resume.keywords.contains(keyword))

    if selected_salary_from:
        resumes = resumes.\
                filter(or_(Resume.salary >= selected_salary_from, Resume.salary == None))

    if selected_salary_to:
        resumes = resumes.\
                filter(or_(Resume.salary <= selected_salary_to, Resume.salary == None))

    sqlalchemy_pagination = paginate(resumes, selected_page, page_size=10)

    flask_pagination = Pagination(page=selected_page,
                            per_page=10,
                            total=resumes.count(),
                            record_name='резюме',
                            bs_version=3,
                            prev_label='<span class="glyphicon glyphicon-chevron-left" aria-hidden="false"></span>',
                            next_label='<span class="glyphicon glyphicon-chevron-right" aria-hidden="false"></span>',
                            display_msg='<b>{start}&ndash;{end}</b> {record_name} из <b>{total}</b> найденных')

    return render_template(
        'index.html',
        resumes=resumes.all(),
        pagination_items=sqlalchemy_pagination.items,
        all_keywords_list=KEYWORDS_LIST,
        output_page=OUTPUT_PAGE_CONFIG,
        gender_dict=GENDER_DICT,
        all_sites_dict=SITE_DICT,
        all_cities_list=CITY_LIST,
        selected_city_list=selected_city_list,
        selected_site_list=selected_site_list,
        selected_keyword_list=selected_keyword_list,
        selected_gender_list=selected_gender_list,
        selected_salary_from=selected_salary_from,
        selected_salary_to=selected_salary_to,
        salary_max=SALARY_MAX,
        flask_pagination=flask_pagination
    )

if __name__ == '__main__':
    APP.run(debug=True)
