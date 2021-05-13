import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def get_paginated(page, selection):
    start = (page - 1) * QUESTIONS_PER_PAGE 
    end = page * QUESTIONS_PER_PAGE 
    return selection[start:end]

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    cors = CORS(app)

    '''
    after_request decorator to set Access-Control-Allow
    '''
    @app.after_request
    def after_request_func(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST')
        return response

    '''
    Endpoint to handle GET requests
    for all available categories.
    '''
    @app.route('/categories')
    def get_categories():
        categories = Category.query.all()

        if len(categories) == 0:
            abort(404)

        categories = {category.id:category.type for category in categories}
        return jsonify({
            'message': 'success',
            'status_code': 200,
            'categories': categories,
            'length': len(categories)
        }), 200

    '''
    Endpoint to handle GET requests for questions, 
    including pagination (every 10 questions). 
    This endpoint should return a list of questions, 
    number of total questions, current category, categories. 
    '''
    @app.route('/questions')
    def get_questions():
        page = request.args.get('page', 1, type=int)
        # in case someone using the api enters a page less than 1
        if page < 1:
            abort(422)
        selection = Question.query.all()
        questions = get_paginated(page, selection)
        if len(questions) == 0:
            abort(404)
        questions = [question.format() for question in questions]
        categories = {c.id:c.type for c in Category.query.all()}
        return jsonify({'message': 'success', 'status': 200, 'questions': questions, 'total_questions': len(selection), 'categories': categories,'current_category': None, 'page': page}), 200
            
    '''
    Endpoint to DELETE question using a question ID. 
    '''
    @app.route('/questions/<string:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        question = Question.query.get(question_id)
        if question is None:
            abort(404)
        question.delete()
        return jsonify({'message': 'Deleted question with id ' + question_id, 'status': 200}), 200
    
    '''
    Endpoint to get a specific question.
    '''
    @app.route('/questions/<string:question_id>')
    def get_question(question_id):
        question = Question.query.get(question_id)
        # return information about the question
        return jsonify({'message': 'success', 'status': 200, 'question': question.format()}), 200

    '''
    Endpoint to POST a new question, 
    which will require the question and answer text, 
    category, and difficulty score.
    '''
    @app.route('/questions', methods=['POST'])
    def add_question():
        json_info = request.get_json()
        try:
            question = json_info['question']
            answer = json_info['answer']
            difficulty = json_info['difficulty']
            category = json_info['category']
        except KeyError:
            abort(400)

        question = Question(question, answer, category, difficulty)
        question.insert()
        return jsonify({'message': 'Added question', 'status': 200, 'question_id': question.id}), 200

    '''
    POST endpoint to get questions based on a search term. 
    It should return any questions for whom the search term 
    is a substring of the question. 
    '''
    @app.route('/questions/search', methods=['POST']) 
    def search_questions():
        try:
            search_term = request.get_json()['searchTerm']
        except TypeError:
            abort(400)

        if search_term is None:
            raise abort(400) 
        result = Question.query.filter(Question.question.ilike('%'+search_term+'%')).all()
        result = [question.format() for question in result]
        return jsonify({'message': 'success', 'status': 200, 'questions': result, 'total_questions': len(result), 'current_category': None}), 200

    '''
    GET endpoint to get questions based on category. 
    '''
    @app.route('/categories/<string:category_id>/questions')
    def get_category_questions(category_id):
        page = request.args.get('page', 1, type=int)
        if page < 1:
            abort(400)
        category = Category.query.get(category_id)
        if category is None:
            abort(404)
        # get all questions under the certain category
        selection = Question.query.filter(Question.category == category_id)
        if selection.first() is None:
            abort(404)
        questions = get_paginated(page, selection)
        if len(questions) == 0:
            abort(400)
        questions = [question.format() for question in questions]
        return jsonify({'message': 'success', 'status': 200, 'questions': questions, 'total_questions': len(questions), 'current_category': category.id}),200

    '''
    POST endpoint to get questions to play the quiz. 
    This endpoint should take category and previous question parameters 
    and return a random questions within the given category, 
    if provided, and that is not one of the previous questions. 
    '''
    @app.route('/quizzes', methods=['POST'])
    def quizzes():
        json_info = request.get_json()
        prev_qs = json_info['previous_questions']
        category = json_info['quiz_category']

        # show all
        if category.get('type') == 'click':
            questions = Question.query.all()
        # show a certain category
        else:
            questions = Question.query.filter(Question.category==category.get('id')).all()

        # get questions that are not in the previous_questions
        questions = [question for question in questions if question.id not in prev_qs]
        questions_length = len(questions)
        # stop the game
        if questions_length == 0:
            current_question = False 
        # a random question 
        else:
            current_question = questions[random.randint(0, questions_length-1)].format()
        return jsonify({'message': 'success', 'status': 200, 'question': current_question}), 200

    '''
    Error Handlers 
    '''
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'message': 'Bad request.', 'status': 400}), 400
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'message': 'Information not found.',
            'status': 404
        }), 404
    @app.errorhandler(500)
    def error(error):
        return jsonify({'message': 'Server error.', 'status': 500}),500
    @app.errorhandler(422)
    def semantic_error(error):
        return jsonify({'message': 'Semantic error in request.', 'status': '422'}), 422
    return app
