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
        # You can change the owner and password to be custom based on your machine
        self.database_name = "trivia_test"
        self.database_owner = "trivia_user"
        self.database_password = "1234"
        self.database_path = "postgresql://{}:{}@{}/{}".format(self.database_owner, self.database_password, 'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_get_valid_page_category(self):
        result = self.client().get('/categories?page=1')
        data = json.loads(result.data)
        self.assertEqual(result.status_code, 200)
        self.assertTrue(data['categories'])
    
    """
    /questions Test
    """
    def test_get_questions(self):
        result = self.client().get('/questions?page=2') 
        data = json.loads(result.data)
        self.assertEqual(result.status_code, 200)
        self.assertTrue(data.get('total_questions'))
    def test_negative_page_get_questions(self):
        result = self.client().get('/questions?page=-2')
        self.assertEqual(result.status_code, 422)
    def test_invalid_page_questions(self):
        result = self.client().get('/questions?page=1000')
        data = json.loads(result.data)
        self.assertEqual(result.status_code, 404)
    def test_creating_question(self):
        result = self.client().post('/questions', json={'question': 'What does API stand for?', 'answer': 'Application Programming Interface', 'difficulty': 1, 'category': 6})
        self.assertEqual(result.status_code, 200)
        data = json.loads(result.data)
        result = Question.query.get(data.get('question_id'))
        self.assertTrue(result)
        # delete question
        self.client().delete('/questions/'+str(data.get('question_id')))
    def test_creating_invalid_question(self):
        result = self.client().post('/questions', json={'question': 'What does TCP stand for?'})
        self.assertEqual(result.status_code, 400)

    """
    DELETE /questions/<question_id>
    """
    # worked when question with id of 5 existed. 
    def test_delete_question(self):
        result = self.client().delete('/questions/14')
        data = json.loads(result.data)
        self.assertEqual(result.status_code, 200)
    def test_delete_invalid_question(self):
        result = self.client().delete('/questions/1000')
        data = json.loads(result.data)
        self.assertEqual(result.status_code, 404)

    """
    POST /questions/search
    """
    def test_search_without_term(self):
        result = self.client().post('/questions/search')
        self.assertEqual(result.status_code, 400)
    def test_search_with_term(self):
        result = self.client().post('/questions/search', json={'searchTerm': 'an'})
        self.assertEqual(result.status_code, 200)
        data = json.loads(result.data) 
        self.assertTrue(data.get('total_questions'))

    """
    GET /categories/<category_id>/questions
    """
    def test_questions_by_category(self):
        result = self.client().get('/categories/1/questions')
        self.assertEqual(result.status_code, 200)
    def test_questions_by_category_nonexistent(self):
        result = self.client().get('/categories/1000/questions')
        self.assertEqual(result.status_code, 404)
    def test_questions_by_negative_page(self):
        result = self.client().get('/categories/1/questions?page=-12')
        self.assertEqual(result.status_code, 400)

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
