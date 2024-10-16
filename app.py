import os
import requests
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve the OpenAI API key from environment variables
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("API key not found. Please set OPENAI_API_KEY in the .env file.")

# Initialize Flask app
app = Flask(__name__)

# Check if the app is running in a testing environment
if os.getenv("TESTING") == "True":
    # Skip the database setup if we are in a testing environment
    db = None
else:
    # Set up the SQLAlchemy database URI (PostgreSQL connection string)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
    # Initialize SQLAlchemy
    db = SQLAlchemy(app)

    class Question(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        question = db.Column(db.String(256), nullable=False)
        answer = db.Column(db.Text, nullable=False)

    # Create the database tables (only required the first time)
    with app.app_context():
        db.create_all()

@app.route('/ask', methods=['POST'])
def ask():
    # Ensure the request contains JSON data
    if not request.is_json:
        return jsonify({"error": "Invalid request format, JSON expected"}), 400

    # Parse the JSON data
    data = request.get_json()

    # Check for 'question' in the JSON data
    question_text = data.get('question')
    if not question_text:
        return jsonify({"error": "No question provided"}), 400

    # Set up OpenAI API request
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": question_text}
        ]
    }

    try:
        # Make the request to OpenAI API
        response = requests.post(url, headers=headers, json=payload)

        # Check if the response is successful
        if response.status_code == 200:
            response_data = response.json()
            answer_text = response_data['choices'][0]['message']['content'].strip()

            # Save the question and answer to the database if not in testing mode
            if db:
                new_question = Question(question=question_text, answer=answer_text)
                db.session.add(new_question)
                db.session.commit()

            return jsonify({'question': question_text, 'answer': answer_text}), 200
        else:
            # Return error response from OpenAI API
            return jsonify({"error": response.json()}), response.status_code

    except Exception as e:
        # Handle any exceptions
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=False)
