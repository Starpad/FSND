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

    # done
    def test_get_questions_paginated_200(self):

        response = self.client().get('/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))

    def test_get_request_invalid_page_404(self):

        response = self.client().get('/questions?page=100')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_delete_question_200(self):

        question = Question(question=self.new_question['question'],
                            answer=self.new_question['answer'],
                            category=self.new_question['category'],
                            difficulty=self.new_question['difficulty'])
        question.insert()

        question_id = question.id

        questions_before = Question.query.all()

        response = self.client().delete('/questions/{}'.format(question_id))
        data = json.loads(response.data)

        questions_after = Question.query.all()

        question = Question.query.filter(Question.id == 1).one_or_none()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

        self.assertEqual(data['deleted'], question_id)

        self.assertTrue(len(questions_before) - len(questions_after) == 1)

        self.assertEqual(question, None)

    def test_post_new_question_200(self):

        questions_before = Question.query.all()

        response = self.client().post('/questions', json=self.new_question)
        data = json.loads(response.data)

        questions_after = Question.query.all()

        question = Question.query.filter_by(id=data['created']).one_or_none()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

        self.assertTrue(len(questions_after) - len(questions_before) == 1)

        self.assertIsNotNone(question)

    def test_post_create_question_fail_422(self):

        questions_before = Question.query.all()

        response = self.client().post('/questions', json={})
        data = json.loads(response.data)

        questions_after = Question.query.all()

        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)

        self.assertTrue(len(questions_after) == len(questions_before))

    def test_post_search_questions_200(self):

        response = self.client().post('/questions', json={
            'searchTerm': 'Peanut Butter'
            })

        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

        self.assertEqual(len(data['questions']), 1)

    def test_post_search_questions_fail_404(self):

        response = self.client().post('/questions', json={
            'searchTerm': 'Galactic President Superstar Mcawesomeville'
            })

        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_get_category_of_question_200(self):

        response = self.client().get('/categories/6/questions')

        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

        self.assertEqual(data['current_category'], 'Sports')

    def test_get_category_of_question_fail_400(self):

        response = self.client().get('/categories/3000/questions')

        data = json.loads(response.data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'bad request')

    def test_post_play_quiz_200(self):

        response = self.client().post('/quizzes',
                                      json={'previous_questions': [20, 21],
                                            'quiz_category': {
                                                'type': 'Science', 'id': '1'
                                                }})

        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

        self.assertTrue(data['question'])

        self.assertNotEqual(data['question']['id'], 20)
        self.assertNotEqual(data['question']['id'], 21)

    def test_post_play_quiz_fail_400(self):

        response = self.client().post('/quizzes', json={})

        data = json.loads(response.data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'bad request')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
