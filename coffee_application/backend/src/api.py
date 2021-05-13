import os
from flask import Flask, request, jsonify, abort, redirect
from sqlalchemy import exc
import json
from flask_cors import CORS
from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth, check_permissions

app = Flask(__name__)
setup_db(app)
CORS(app)

# db_drop_and_create_all()

# ROUTES

'''
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks')
def get_drinks():
    drinks = [drink.short() for drink in Drink.query.all()]
    return jsonify({"success": True, "drinks": drinks}), 200

'''
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail')
@requires_auth(permission='get:drinks-detail')
def get_drinks_detail(payload):
    drinks = [drink.long() for drink in Drink.query.all()]
    return jsonify({"success": True, "drinks": drinks}), 200

'''
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth(permission='post:drinks')
def create_drink(payload):
    payload = None
    data = request.get_json()
    title = data.get('title')
    recipe = data.get('recipe')
    try:
        drink = Drink(title=title, recipe=json.dumps(recipe))
        drink.insert()
        return jsonify({"success": True, "drinks": drink.long()}), 200
    except Exception as e:
        abort(500)

'''
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth(permission='patch:drinks')
def update_drink(payload, drink_id):
    drink = Drink.query.get(drink_id)
    if drink is None:
        abort(404)
    data = request.get_json()
    if data.get('title') is not None:
        drink.title = data.get('title')
    if data.get('recipe') is not None:
        drink.recipe = data.get('recipe')
    return jsonify({"success": True, "drinks": [drink.long()]}), 200

'''
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth(permission='delete:drinks')
def delete_drink(payload, drink_id):
    drink = Drink.query.get(drink_id)
    if drink is None:
        abort(404)
    drink.delete()
    return jsonify({"success": True, "delete": drink_id}), 200

# Error Handling
'''
Example error handling for unprocessable entity
'''

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
    error handler should conform to general task above
'''
@app.errorhandler(404)
def not_found(error):
    return jsonify({"success": False, "error": 404, "message": "resource not found"}), 404


'''
    error handler should conform to general task above(AuthError)
'''
@app.errorhandler(AuthError)
def auth_error(auth_error):
    return jsonify({"success": False, "error": auth_error.status_code, "message": auth_error.error}), auth_error.status_code
