import sys
import requests
import jwt
import logging
import threading
from sqlalchemy import create_engine, Column, Integer, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

# Database configuration
DB_USERNAME = 'admin'
DB_PASSWORD = 'abcd1234'
DB_HOST = 'database-voting.c5gm60ycmd0d.eu-north-1.rds.amazonaws.com'
DB_PORT = '3306'
DB_NAME = 'distributed_voting_system'

# SQLAlchemy engine and session
engine = create_engine(f"mysql+mysqlconnector://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
Session = sessionmaker(bind=engine)
Base = declarative_base()

# Define the Vote model
class Vote(Base):
    __tablename__ = 'votes'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    candidate_id = Column(Integer)
    timestamp = Column(DateTime, default=datetime.now)

# Create the tables in the database
Base.metadata.create_all(engine)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Configure base URLs for each microservice
BASE_URLS = {
    'authentication': 'http://af91f9614e95a4d1fa79f1c50e42de90-664409630.eu-north-1.elb.amazonaws.com:5001',
    'voting': 'http://af06a410aec994c8680c50f815f52fce-1747989051.eu-north-1.elb.amazonaws.com:5002',
    'results': 'http://a9c63b96d278d459998670531a54374f-1233612994.eu-north-1.elb.amazonaws.com:5003'
}

# Secret key for JWT token
SECRET_KEY = 'd293f2dee0997cfff9fbfbc61589683030dbfd6d44f42bae1d07c013a22a49f5'


def register(username, password, role):
    """Register a new user with a role."""
    url = f"{BASE_URLS['authentication']}/register"
    data = {'username': username, 'password': password, 'role': role}
    response = requests.post(url, json=data)
    return response.json()

def is_voting_period_active():
    now = datetime.now()
    voting_start = datetime(2024, 5, 28, 8, 0)
    voting_end = datetime(2024, 4, 28, 20, 0)
    return voting_start <= now <= voting_end

def login(username, password):
    """Log in a user."""
    url = f"{BASE_URLS['authentication']}/login"
    data = {'username': username, 'password': password}
    response = requests.post(url, json=data)
    return response.json()

def list_candidates():
    """Retrieve a list of candidates."""
    url = f"{BASE_URLS['results']}/candidates"
    response = requests.get(url)
    if response.status_code == 200:
        candidates = response.json()
        print("List of Candidates:")
        for candidate in candidates:
            print(f"ID: {candidate['id']}, Name: {candidate['username']}")
    else:
        print("Failed to retrieve candidates.")

def threaded_vote(user_id, candidate_id, token):
    """Function to handle vote casting in a separate thread."""
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        print({'error': 'Token has expired.'})
        return
    except jwt.InvalidTokenError:
        print({'error': 'Invalid token.'})
        return

    if not is_voting_period_active():
        print("Voting time has ended.")
        return

    if Session().query(Vote).filter_by(user_id=user_id).first():
        print({'error': 'User has already voted.'})
        return

    url = f"{BASE_URLS['voting']}/vote"
    data = {'user_id': user_id, 'candidate_id': candidate_id}
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 200:

        print({'message': 'Vote successfully records.'})
    elif response.status_code == 503:
        print("Voting service is currently unavailable.")
    else:
        print(response.json())


def results():
    url = f"{BASE_URLS['results']}/results"
    response = requests.get(url)
    return response.json()

def get_winner():
    """Retrieve and display the election winner."""
    url = f"{BASE_URLS['results']}/winner"  # Ensure this matches the actual URL and port of your results service
    response = requests.get(url)
    if response.status_code == 200:
        winner_info = response.json()
        print(f"The winner is {winner_info['winner']} with {winner_info['votes']} votes.")
    elif response.status_code == 404:
        print("No votes have been cast yet.")
    else:
        print("Failed to retrieve the winner. Status code:", response.status_code)

def main():
    args = sys.argv[1:]  # Get arguments passed to script
    if not args:
        print("No command provided.")
        return

    command = args[0]

    try:
        if command == 'register' and len(args) == 4:
            username, password, role = args[1], args[2], args[3]
            result = register(username, password, role)
            print(result)
        elif command == 'login' and len(args) == 3:
            username, password = args[1], args[2]
            result = login(username, password)
            print(result)
        elif command == 'vote' and len(args) == 4:
            user_id, candidate_id, token = int(args[1]), int(args[2]), args[3]
            vote_thread = threading.Thread(target=threaded_vote, args=(user_id, candidate_id, token))
            vote_thread.start()
            vote_thread.join()
        elif command == 'results' and len(args) == 1:
            result = results()
            print(result)
        elif command == 'list_candidates' and len(args) == 1:
            list_candidates()
        elif command == 'winner' and len(args) == 1:
            get_winner()
        else:
            print("Invalid command or number of arguments.")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == '__main__':
    main()
