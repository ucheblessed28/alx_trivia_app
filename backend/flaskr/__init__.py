# from crypt import methods
from hashlib import new
from http.client import ResponseNotReady
import json
import os
from re import T
from tkinter.messagebox import QUESTION
from unicodedata import category
from flask import Flask, current_app, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10
def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page -1) * QUESTIONS_PER_PAGE
    end = start +   QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_question = questions[start:end]
    return current_question

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app)

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add(
            'Access-Control-Allow-Credentials', 'true'
        )
        response.headers.add(
            'Access-Control-Allow-Headers', ' Content-Type, Authorization, true'
        )
        response.headers.add(
            'Access-Control-Allow-Methods', 'GET,POST,OPTIONS,PUT, DELETE'
        )
        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories')
    def get_categories():
        selections = Category.query.all()
        categories = {}
        try:
            for selection in selections:
                categories[selection.id] = selection.type
      

            return jsonify({
                'success': True,
                'categories': categories
            })
        except:
            abort(404)

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.
    

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """

    @app.route('/questions')
    def get_questions():
        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)
        try:
            if len(current_questions) == 0:
                abort(404)
            selections = Category.query.all()
            categories = {}
            for selection in selections:
                categories[selection.id] = selection.type
        

            return jsonify({
                'success': True,
                'questions': current_questions,
                'total_questions': len(Question.query.all()),
                'categories': categories
            })
        except:
            abort(404)


    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try: 
            question = Question.query.filter(Question.id== question_id).one_or_none()
            if question is None:
                abort(404)
            question.delete()
            selection = Question.query.order_by(Question.id).all()
            current_question = paginate_questions(request, selection)

            return jsonify({
                'success': True,
                'total_questions': len(selection)
            })
        except:
            abort(404)


    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route('/questions', methods=['POST'])
    def new_question():
        body = request.get_json()
        question = body.get('question', None)
        answer = body.get('answer', None)
        category = body.get('category', None)
        difficulty = body.get('difficulty', None)
        search_term = body.get('searchTerm', None)

        try: 
            if search_term:
                selection = Question.query.order_by(Question.id).filter(Question.question.ilike('%{}%'.format(search_term)))
                current_questions = paginate_questions(request, selection)

                return jsonify({
                'success': True,
                'questions': current_questions,
                'total_questions': len(selection.all())
                })
            else:
                new_question = Question(
                    question = question, 
                    answer = answer,
                    category = category,
                    difficulty = difficulty
                )
                new_question.insert()

                selection = Question.query.order_by(Question.id).all()
                current_questions = paginate_questions(request, selection)
        
            return jsonify({
                'success': True,
                'created': new_question.id,
                'questions': current_questions,
                'total_questions': len(selection)
            })
        except:
            abort(422)
    
    
    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:category_id>/questions')
    def get_category_based_question(category_id):
        category = Category.query.filter_by(id=category_id).one_or_none()
        try: 
            if category:
                selection = Question.query.filter_by(category=category_id).all()
                current_questions = paginate_questions(request, selection)
        

            return jsonify({
                'success': True,
                'questions': current_questions,
                'total_questions': len(selection)
            })
        except:
            abort(404)

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/quizzes', methods=['POST'])
    def quiz():
        body = request.get_json()
        previousQuestions = body.get('previous_questions')
        quizCategory = body.get('quiz_category')
        category_id = quizCategory['id']

        try:
            if category_id == 0:
                current_questions = Question.query.all()
            else:
                current_questions = Question.query.filter_by(category=category_id).all()
            
            next_question = random.choice(current_questions).format()

            answered = False
            
            if next_question['id'] in previousQuestions:
                answered = True
            
            while answered:
                next_question = random.choice(current_questions).format()
                if(len(previousQuestions) == len(current_questions)):
                    return jsonify({
                        'success': True
                    })

            return jsonify({
                'success':True,
                "question": next_question
            })
        except:
            abort(400)
    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error":400,
            "message": "Bad request sent"
        }), 400


    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error":404,
            "message": "Resource not found"
        }), 404
    
    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error":422,
            "message": "Unprocessable"
        }), 422
    return app

