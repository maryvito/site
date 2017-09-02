import datetime
import pprint
import sys
sys.path.append('..')

import requests
from bs4 import BeautifulSoup

from config import COOKIES, RU_MONTH_VALUES 
from models import Resume, Keywords, db_session


def get_html(url):
    print(url)
    result = requests.get(url, cookies=COOKIES)
     
    if result.ok:
        return result.text
    else:
        print('Нет соединения с сайтом superjob')


def parse_salary(bs_resume):
    # парсим строку вида "Резюме: Руководитель отдела, Москва, Образование: Высшее, Возраст: 25 лет, по договоренности.
    data_resume = bs_resume.find('meta', property='og:description').get('content').split(',')
    salary = data_resume[-1].strip().strip('.') or None
    if salary != 'по договоренности':
        salary = int(salary.split('руб')[0].replace(' ',''))
    else:
        salary = None
    return salary


def calculate_age(born):
    today = datetime.date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


def parse_personal_info(bs_resume):
    personal_data = bs_resume.find('span', class_ = 'h_font_weight_medium').findNext('div').text.strip().split('\n')[0]
    gender, birth_date = personal_data.split(',')[0],personal_data.split(',')[1]
    
    gender = 'male' if gender == 'Муж.' else 'female'

    try:
        degree = personal_data.split(',')[2].strip()
        has_degree = True if degree == 'высшее образование' else  False
    except IndexError:
        has_degree = None

    day, month, year = birth_date.split('(')[-1].strip(')').split(' ')
    month = RU_MONTH_VALUES[month]
    birth_date = datetime.date(int(year), month, int(day))    
    age = calculate_age(birth_date)   
    return gender, has_degree, age


def parse_city(bs_resume):
    personal_data = bs_resume.find('span', class_ = 'h_font_weight_medium').findNext('div').text.strip().split('\n')
    city = personal_data[1].split(',')[0].strip()
    return city

def get_keywords_from_base():
    keywords_from_base = []
    for key in Keywords.query.all():
        keywords_from_base.append(key.keyword)
    return keywords_from_base


# TODO: оптимизировать подбор навыков
def parse_skills(keywords_from_base, bs_resume):
    professional_skills_tag = bs_resume.find(text='Профессиональные навыки')
    keywords_from_resume = []
    if professional_skills_tag:
        professional_skills = professional_skills_tag.findNext('div').text.lower()
        for keyword in keywords_from_base:
            if keyword.lower() in professional_skills:
                keywords_from_resume.append(keyword.lower())
    return keywords_from_resume


def parse_resume(bs_resume):
    gender, has_degree, birth_date = parse_personal_info(bs_resume)
    return {
        'gender': gender,
        'has_degree': has_degree,
        'age': birth_date,
        'keywords': parse_skills(get_keywords_from_base(), bs_resume),
        'salary': parse_salary(bs_resume),
        'city': parse_city(bs_resume)
    }


def get_urls_and_titles_resumes_from_search_html(html):
    titles_and_urls_resumes = {}
    bs_resumes = BeautifulSoup(html, 'html.parser')
    titles_and_urls_tags = bs_resumes.find_all('a', class_ = 'sj_h3 ResumeListElementNew_profession')
    for title_and_url_tag in titles_and_urls_tags:
        titles_and_urls_resumes[title_and_url_tag.get('title')] = title_and_url_tag.get('href').split('?')[0]
        print('1!!!  ')
        print(titles_and_urls_resumes)
    return titles_and_urls_resumes


def parse_resumes(titles_and_urls_resumes):
    data_resumes_list = []
    for title in titles_and_urls_resumes:
        data_from_resume_dict = {}
        html_resume = get_html(titles_and_urls_resumes[title])
        bs_resume = BeautifulSoup(html_resume,'html.parser')
        data_from_resume_dict = parse_resume(bs_resume)
        data_from_resume_dict['url'] = titles_and_urls_resumes[title]
        data_from_resume_dict['title'] = title
        data_resumes_list.append(data_from_resume_dict)
    return data_resumes_list


def save_data_to_base(data_resumes_list, db_session):
    
    all_urls = []
    for item in Resume.query.all():
        all_urls.append(item.url)

    for item in data_resumes_list:
        if item['url'] not in all_urls:
            all_urls.append(item['url'])
            resume = Resume(item['title'], item['gender'],
                       item['age'], item['has_degree'],
                       item['city'], str(item['keywords']),
                       item['salary'], item['url'])
            db_session.add(resume)
    db_session.commit()


def parse_resumes_from_superjob(db_session):
    url = 'https://www.superjob.ru/resume/search_resume.html?sbmit=1&show_refused=0&t[]=4&order_by[rank]=desc&sbmit=1&order_by[rank]=desc&keywords[0][keys]=python&page={}'
    number_page = 1
    html = ''
    while requests.get(url.format(number_page)).status_code == 200 and number_page < 10:
        html += get_html(url.format(number_page))
        number_page += 1
    
    data_resumes_list = parse_resumes(get_urls_and_titles_resumes_from_search_html(html))
    save_data_to_base(data_resumes_list, db_session)


if __name__ == '__main__':
    parse_resumes_from_superjob(db_session)
