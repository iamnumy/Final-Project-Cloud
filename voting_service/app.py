from flask import Flask, request, jsonify
from models import db, Vote
from flask_cors import CORS

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://admin:abcd1234@database-voting.c5gm60ycmd0d.eu-north-1.rds.amazonaws.com/distributed_voting_system'
db.init_app(app)
CORS(app)
CORS(app, resources={r"/*": {
    "origins": "*",
    "allow_headers": ["Authorization", "Content-Type"],
    "methods": ["GET", "POST", "OPTIONS"]
}})

@app.before_first_request
def create_tables():
    with app.app_context():
        db.create_all()

@app.route('/vote', methods=['POST'])
def cast_vote():
    user_id = request.json.get('user_id')
    candidate_id = request.json.get('candidate_id')

    if not user_id or not candidate_id:
        return jsonify({'error': 'Missing user ID or candidate ID'}), 400

    # Check if user has already voted
    existing_vote = Vote.query.filter_by(user_id=user_id).first()
    if existing_vote:
        return jsonify({'error': 'Vote already casted'}), 409

    # Record the new vote
    new_vote = Vote(user_id=user_id, candidate_id=candidate_id)
    db.session.add(new_vote)
    db.session.commit()

    return jsonify({'message': 'Vote successfully recorded.'}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002, threaded=True)
