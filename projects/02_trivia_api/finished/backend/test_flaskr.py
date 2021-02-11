import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.DB_HOST = os.getenv('DB_HOST', '127.0.0.1:5432')
        self.DB_USER = os.getenv('DB_USER', 'postgres')
        self.DB_PASSWORD = os.getenv('DB_PASSWORD', 'padpw')
        self.DB_NAME = os.getenv('DB_NAME', 'trivia_test')
        self.DB_PATH = "postgres://{}:{}@{}/{}".format(
            self.DB_USER, self.DB_PASSWORD, self.DB_HOST, self.DB_NAME)
        setup_db(self.app, self.DB_PATH)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

        # sample question for the tests
        self.new_question = {
            'question': 'Who joined Neil Armstrong and Buzz Aldrin' +
            'on the Apollo 11 mission?',
            'answer': 'Michael Collins',
            'difficulty': 4,
            'category': '4'
        }

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful
    operation and for expected errors.
    """

    def test_get_categories_200(self):
        # Test categories response and wether there are categories
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])

    def test_get_questions_paginated_200(self):
        # Test questions response and check length of questions
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['questions'])
        self.assertTrue(len(data['questions']))

    def test_get_request_invalid_page_404(self):
        # Test questions response with a to high page number
        res = self.client().get('/questions?page=9999')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_delete_question_200(self):
        # Insert a new question for testing delete function
        question = Question(question=self.new_question['question'],
                            answer=self.new_question['answer'],
                            category=self.new_question['category'],
                            difficulty=self.new_question['difficulty'])
        question.insert()
        question_id = question.id

        # Delete new question and get response
        res = self.client().delete('/questions/{}'.format(question_id))
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], question_id)

    def test_post_new_question_200(self):
        # Test for creating a new question
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)

        # Check for success of creation
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])

    def test_post_create_question_fail_422(self):
        # Test to create a question with a empty json
        res = self.client().post('/questions', json={})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)

    def test_post_search_questions_200(self):
        # test to perform a search on questions
        res = self.client().post('/questions', json={
            'searchTerm': 'Peanut Butter'
            })

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['questions']), 1)

    def test_post_search_questions_fail_422(self):
        # test to perform a search with a invalid searchTerm
        res = self.client().post('/questions', json={
            'searchTerm': 'Not a valid search term'
            })

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable untity')

    def test_get_category_of_question_200(self):
        # test of getting category 6
        res = self.client().get('/categories/6/questions')

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['current_category'], 6)

    def test_get_category_of_question_fail_404(self):
        # test to get questions from category 3000
        res = self.client().get('/categories/3000/questions')

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_post_play_quiz_200(self):
        # test to play the game successful
        res = self.client().post('/quizzes',
                                      json={'previous_questions': [],
                                            'quiz_category': {
                                                'type': 'Science', 'id': '1'
                                                }})

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])

    def test_post_play_quiz_fail_422(self):
        # test if playing the quiz with empty json fails
        res = self.client().post('/quizzes', json={})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable untity')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
