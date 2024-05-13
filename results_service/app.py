from flask import Flask, jsonify
from models import db, Vote, User
from sqlalchemy import func
from flask_cors import CORS

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://admin:abcd1234@database-voting.c5gm60ycmd0d.eu-north-1.rds.amazonaws.com:3306/distributed_voting_system'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

CORS(app)

@app.route('/results', methods=['GET'])
def get_results():
    try:
        results = db.session.query(func.count(Vote.id), User.username).join(User, Vote.candidate_id==User.id).group_by(User.username).all()
        result_dict = {username: count for count, username in results}
        return jsonify(result_dict), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/candidates', methods=['GET'])
def get_candidates():
    try:
        candidates = User.query.filter(User.role == 'CANDIDATE').all()
        return jsonify([{'id': user.id, 'username': user.username} for user in candidates]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/winner', methods=['GET'])
def get_winner():
    try:
        results = db.session.query(User.username, func.count(Vote.id)).join(User, Vote.candidate_id == User.id).filter(User.role == 'CANDIDATE').group_by(User.username).all()
        if results:
            winner = max(results, key=lambda item: item[1])  # item[1] is the count of votes
            winner_info = {'winner': winner[0], 'votes': winner[1]}
            return jsonify(winner_info), 200
        else:
            return jsonify({'message': 'No votes have been cast yet.'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5003, threaded=True)
