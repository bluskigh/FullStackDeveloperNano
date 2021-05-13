# Full Stack Trivia API Backend

## Getting Started

### Installing Dependencies

#### Python 3.7

Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

#### Virtual Environment

We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organized. Instructions for setting up a virtual environment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

#### PIP Dependencies

Once you have your virtual environment setup and running, install dependencies by navigating to the `/backend` directory and running:

```bash
pip install -r requirements.txt
```

This will install all of the required packages we selected within the `requirements.txt` file.

##### Key Dependencies

- [Flask](http://flask.pocoo.org/)  is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we"ll use handle the lightweight sqlite database. You"ll primarily work in app.py and can reference models.py. 

- [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#) is the extension we"ll use to handle cross origin requests from our frontend server. 

##### PostgreSQL installation
- needed in order to run this application 
- windows installation can be followed here: https://www.postgresqltutorial.com/install-postgresql/
```
sudo apt-get update
sudo apt-get install postgresql
```

## Database Setup
Log into the postgres terminal client
```
sudo -u postgres -i
```
1) Create a database called "trivia" in the psql terminal client: 
```
createdb trivia
```
2) Run psql on the created database:
```
psql trivia
```
3) Create a user under the name of trivia_user with a password of 1234: 
```
create user trivia_user with password '1234';
```
4) Exit out of the psql database by typing: "\q", now exit out of the postgres terminal client by typing: "exit"
5) You should be in the terminal now, simply type (to restore the database file): 
```bash
psql trivia < trivia.psql
```
- if you receive an error running the above code try this: 
```
sudo -u postgres psql triva < trivia.psql
```
All set! You can now run the application, though you cannot run the test yet, scroll to the bottom of the README to see information on how to do so.

## Running the server

From within the `backend` directory first ensure you are working using your created virtual environment.

To run the server, execute:

```bash
export FLASK_APP=flaskr
export FLASK_ENV=development
flask run
```

Setting the `FLASK_ENV` variable to `development` will detect file changes and restart the server automatically.

Setting the `FLASK_APP` variable to `flaskr` directs flask to use the `flaskr` directory and the `__init__.py` file to find the application. 

## Tasks

One note before you delve into your tasks: for each endpoint you are expected to define the endpoint and response data. The frontend will be a plentiful resource because it is set up to expect certain endpoints and response data formats already. You should feel free to specify endpoints in your own way; if you do so, make sure to update the frontend or you will get some unexpected behavior. 

1. Use Flask-CORS to enable cross-domain requests and set response headers. 
2. Create an endpoint to handle GET requests for questions, including pagination (every 10 questions). This endpoint should return a list of questions, number of total questions, current category, categories. 
3. Create an endpoint to handle GET requests for all available categories. 
4. Create an endpoint to DELETE question using a question ID. 
5. Create an endpoint to POST a new question, which will require the question and answer text, category, and difficulty score. 
6. Create a POST endpoint to get questions based on category. 
7. Create a POST endpoint to get questions based on a search term. It should return any questions for whom the search term is a substring of the question. 
8. Create a POST endpoint to get questions to play the quiz. This endpoint should take category and previous question parameters and return a random questions within the given category, if provided, and that is not one of the previous questions. 
9. Create error handlers for all expected errors including 400, 404, 422 and 500. 

## Popular request arguments in API
- page
-- page identifies where to start collecting questions from the database. 
-- Each page renders 10 possible questions per request.
-- Example: curl "/questions?page=2" would start counting at the 10nth index in the database, returning questions[10:20]. Since only 10 questions possible can be returned per request.

Endpoints

GET "/categories"
- Fetches a dictionary of categories in which the keys are the ids and the value is the corresponding string of the category
- Request Arguments: None
- Returns: An object with a single key, categories, that contains a object of id: category_string key:value pairs. 
```
{"1" : "Science",
"2" : "Art",
"3" : "Geography",
"4" : "History",
"5" : "Entertainment",
"6" : "Sports"}
```

GET "/questions"
- Request Arguments: page
- Returns: An object with questions(array), total_questions, and categories keys.
Example: "/questions?page=2"
```
{ 
"categories": {"1": 'Programming', ...},
"questions": [
    {"answer": "API", 
    "question": "...Application Programming Interface", 
    "difficulty": 1, 
    "category": "3", 
    "id": 15
    }, ...
], 
"message": "success",
"status": 200
}
```

GET "/categories/<category_id>/questions"
- Queries datbase for the given category_id, and selects all questions that are children of the resulting Category. 
- Request arguments: page, category_id
- Returns: Current category, questions (limited to 10 based on the page argument), total_questions 
Example: curl "/categories/2/questions?page=1"
```
{
    "current_category": 2,
    "questions": [
        {
            "answer": "The Liver",
            "category": "1",
            "difficulty": 4,
            "id": 20,
            "question": "What is the heaviest organ in the human body?"
        } ...
    ],
    "total_questions": 6
}
```

DELETE "/questions/<question_id>"
- Queries the database for a question with the given question_id, attempts to delete it.
- Request arguments: question_id
- Returns: message, status
Example: DELETE "/questions/1"
```
{
    "message": "Deleted question with id 1",
    "status": 200
}
```


POST "/questions"
- Creates a new question and stores it in the database.
- Request arguments: question, answer, difficulty, category 
- Returns: question id, message, status
Example: POST "/questions"
```
{
    "message": "Added question.",
    "status": 200,
    "question_id": question.id 
}
```

POST "/questions/search"
- Queries the database for questions that have the search term in their question.
- Required arguments: searchTerm 
- Returns: An object with multiple keys such as, questions, and total_questions.
Example: curl -H "Content-Type: application/json" -X POST -d '{"searchTerm": "dog"}' localhost:5000/questions/search
```
{
    "questions": [
        {
            "answer": "water",
            "question": "What do dogs love?",
            ...
        },
        {
            "answer": "chew toys",
            "question": "Dogs love the sound of?",
            ...
        },
        ...
    ],
    "total_questions": 5
}
```

POST '/quizzes'
- Gets questions to play for the quiz.
- Required arguments: previous_questions(list), quiz_category(object)
- Returns: Return a new question that is in the same category as the quiz_category, and is not inside the previous_questions list provided when the POST request was made. 

## Testing
make sure you're in the postgres terminal client:
```
sudo -u postgres -i
```
Then run the following commands:
```
dropdb trivia_test
createdb trivia_test
```
Now in the terminal attempt:
```
psql trivia_test < trivia.psql
- OR if you receive an error try:
sudo -u postgres psql trivia_test < trivia.psql
```
Now you should be able to run
```
python test_flaskr.py
```
