import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

# added a paginate function for questions

def paginate_questions(request, selection):

    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    active_questions = questions[start:end]

    return active_questions


def create_app(test_config=None):

    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    '''
    @TODO: Set up CORS. Allow '*' for origins.
    Delete the sample route after completing the TODOs
    '''

    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

    '''
    @TODO: Use the after_request decorator to set Access-Control-Allow
    '''

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PATCH,POST,DELETE,OPTIONS')
        return response
    '''
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    done
    '''

    @app.route('/categories', methods=['GET'])
    def get_categories():
        categories = Category.query.order_by(Category.id).all()

        # Abort if no categories are returned
        if len(categories) == 0:
            abort(404)
        
        # Format Categories in a dictionary
        active_categories = {}
        for category in categories:
            active_categories[category.id] = category.type

        # return the dictionary of categories and the length
        return jsonify({
            'success': True,
            'categories': active_categories
        })

    '''
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom
     of the screen for three pages.
    Clicking on the page numbers should update the questions.
    '''

    @app.route('/questions', methods=['GET'])
    def get_questions():
        # get questions from database
        questions = Question.query.all()
        paginated_questions = paginate_questions(request,questions)
        count_questions = len(questions)

        # Abort if no questions are returned
        if count_questions == 0:
            abort(404)

        # get categories from database
        categories = Category.query.all() 

        # Format Categories in a dictionary
        active_categories = {}
        for category in categories:
            active_categories[category.id] = category.type
        
        if (len(paginated_questions) == 0):
            abort(404)

        return jsonify({
            'success': True,
            'questions': paginated_questions,
            'total_questions': count_questions,
            'categories': active_categories
        })

    '''
    @TODO:
    Create an endpoint to DELETE question using a question ID.
    TEST: When you click the trash icon next to a question,
    the question will be removed.
    This removal will persist in the database and when you refresh the page.
    '''

    @app.route('/questions/<int:id>', methods=['DELETE'])
    def delete_question(id):
        try:
            question = Question.query.get(id)

            # Abort if no question is returned
            if question is None:
                abort(404)

            # delete question and count remaining questions
            question.delete()
            questions = Question.query.order_by(Question.id).all()
            paginated_questions = paginate_questions(request,questions)
            count_questions = len(questions)

            return jsonify({
                'success': True,
                'deleted': id,
                'question': paginated_questions,
                'total_books': count_questions
            })

        except Exception as e:
            print(e)
            abort(422)

    '''
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear
    at the end of the last page
    of the questions list in the "List" tab.
    '''
    # done in the next step

    '''
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    '''
    # done

    @app.route('/questions', methods=['POST'])
    def post_question():
        body = request.get_json()
        search_term = body.get('searchTerm')

        # if the json from the response is not valid -> abort
        # if search_term is None:
        #     abort(400)

        # if a search term is provided perform a search
        try:
            if search_term:
                # search_questions = Question.query.filter(Question.question.contains(search_term)).all()
                search_questions = Question.query.filter(Question.question.ilike('%{}%'.format(search_term))).all()
                
                # if no questions are found return 404 error
                if (len(search_questions) == 0):
                    abort(404)

                # if there are questions found, return them paginated
                paginated_search_questions = paginate_questions(request, search_questions)

                # get categories and return the result
                #categories = Category.query.order_by(Category.id).all()  

                # Format Categories in a dictionary
                #active_categories = {}
                #for category in categories:
                    #active_categories[category.id] = category.type

                return jsonify({
                    'success': True,
                    'questions': paginated_search_questions,
                    'total_questions': len(paginated_search_questions)#,
                    #'current_categories': active_categories
                })
            # if no search term is provided, add the question
            else:
                new_question = body.get('question', None)
                new_answer = body.get('answer', None)
                new_difficulty = body.get('difficulty', None)
                new_category = body.get('category', None)

                # check if any required input is missing and abort
                if new_question is None:
                    abort(400)
                if new_answer is None:
                    abort(400)
                if new_difficulty is None:
                    abort(400)
                if new_category is None:
                    abort(400)
                
                try:
                    # try to generate a new question
                    question = Question(question = new_question,
                                        answer = new_answer,
                                        category = new_category,
                                        difficulty = new_difficulty)
                    question.insert()

                    # Get all questions
                    questions = Question.query.order_by(Question.id).all()
                    paginated_questions = paginate_questions(request, questions)

                    # return results
                    return jsonify({
                        'success': True,
                        'created': question.id,
                        'question_created': question.question,
                        'questions': paginated_questions,
                        'total_questions': len(questions)
                    })

                except Exception as e:
                    print(e)
                    abort(422)

        except Exception as e:
            print(e)
            abort(422)

    '''
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    '''

    @app.route('/categories/<int:id>/questions', methods=['GET'])
    def get_questions_by_category(id):
        # Get the category from the given id
        category = Category.query.filter(Category.id == id).one_or_none()

        # if no category is found return 404 error
        if category is None:
            abort(404)

        # Get all questions from the given category id
        questions = Question.query.order_by(Question.id).filter(Question.category == id).all()

        # if no questions are found return 404 error
        if questions is None:
            abort(404)

        # if there are questions found, return them paginated
        paginated_questions = paginate_questions(request, questions)

        return jsonify({
            'success': True,
            'questions': paginated_questions,
            'total_questions': len(questions),
            'current_category': category.id
        })

    '''
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    '''

    @app.route('/quizzes', methods=['POST'])
    def get_random_quiz_question():

        try:
            # load response into body and check if body is empty
            body = request.get_json()

            # Get category and previous question from response
            category = body.get('quiz_category', None)
            previous_questions = body.get('previous_questions', None)
            # all_questions = Question.query.all()

            # if body is None:
            #     abort(400)

            if not ('quiz_category' in body and 'previous_questions' in body):
                abort(422)
            

            # if there is a category in the body
            # get questions from that id
            if category['id'] != 0:
                questions = Question.query.filter_by(category = category['id']).all()

            # else select all questions
            else:
                questions = Question.query.all()
            
            # generate a random question
            current_question = random.choice(questions).format()
            # boolean to check if question was already used
            used_check = False

            if current_question['id'] in previous_questions:
                used_check = True
            
            # while used_check = true generate a new random question
            # and if all questions have been played, return end message
            while used_check:
                current_question = random.choice(questions).format()
                if (len(previous_questions) == len(questions)):
                    return jsonify({
                        'success': True,
                        'message': "All questions have been played!"
                    }), 200


            # check if questions was already used
            # # if all questions have been played, return success and message
            # while (current_question['id'] in previous_questions) == False:
            #     current_question = random.choice(questions).format()

            #     if (len(previous_questions) == len(all_questions)):
            #         return jsonify({
            #             'success': True,
            #             'message': "All questions have been played!"
            #         }), 200

                

            return jsonify({
                'success': True,
                'question': current_question
            })

        except Exception as e:
            print(e)
            abort(422)

    '''
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    '''
    # Added 500 as well as it was mentioned in the README file

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

    @app.errorhandler(404)
    def resource_not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable_untity(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable untity"
        }), 422

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "internal server error"
        }), 500

    return app
