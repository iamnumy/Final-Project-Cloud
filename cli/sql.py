from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://admin:abcd1234@database-voting.c5gm60ycmd0d.eu-north-1.rds.amazonaws.com/distributed_voting_system'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define User model
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    # Add more columns as needed

def fetch_user_by_username(username):
    try:
        user = User.query.filter_by(username=username).first()
        return user
    except Exception as e:
        print("Error fetching user:", e)
        return None

if __name__ == "__main__":
    with app.app_context():
        # Example usage
        username = "ali"
        user = fetch_user_by_username(username)
        if user:
            print(f"User found: {user.username}")
        else:
            print("User not found.")
