from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from sqlalchemy import text  # Import the text function
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Load the database URI from environment variable
db_uri = os.getenv("DATABASE_URL")
if db_uri is None:
    print("DATABASE_URL not found in environment variables")
else:
    print(f"DATABASE_URL is: {db_uri}")

# Set the SQLAlchemy configuration
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
db = SQLAlchemy(app)

try:
    # Test the database connection
    with app.app_context():
        db.session.execute(text('SELECT 1'))  # Use text() to wrap the query
    print("Database connection successful")
except Exception as e:
    print(f"Database connection failed: {str(e)}")
