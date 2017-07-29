import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from flask import request
from models import Resume, db_session
from server.cv_aggr import url_string_from_dict, filtering_database_query_by_selected_params, APP

test_selected_parameters = {
        'salary_none': '1',
        'salary_from': '0',
        'salary_to': '0',
        'gender': 'male',
        'site': 'hh.ru',
        'city': 'Москва',
        'keyword': 'bash'
            }
test_resumes = db_session.query(Resume)


class DatabaseTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_filtering_database_query_by_selected_params(self):
        self.assertTrue(filtering_database_query_by_selected_params(test_resumes, test_selected_parameters))
        self.assertIsInstance(filtering_database_query_by_selected_params(test_resumes, test_selected_parameters),
                              type(db_session.query(Resume)))


class FlaskTestCase(unittest.TestCase):

    def test_request_path(self):
        with APP.test_request_context('/?page=1&keyword=bash&salary_none=1&salary_from=0&salary_to=0'
                                      '&gender=male&site=hh.ru&city=Москва&keyword=bash'):
            self.assertEqual(request.path, '/')

    def test_request_arguments(self):
        with APP.test_request_context('/?page=1&keyword=bash&salary_none=1&salary_from=0&salary_to=0'
                                      '&gender=male&site=hh.ru&city=Москва&keyword=bash'):
            for key in test_selected_parameters:
                self.assertEqual(request.args[key], test_selected_parameters[key])

    def test_url_from_dict(self):
        self.assertTrue(url_string_from_dict(test_selected_parameters))
        self.assertIsInstance(url_string_from_dict(test_selected_parameters), str)

if __name__ == '__main__':

    unittest.main()
