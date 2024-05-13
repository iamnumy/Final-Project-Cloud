from flask import Flask, request, jsonify
from models import db, User, UserRole
from flask_migrate import Migrate
import jwt
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {
    "origins": "*",
    "allow_headers": ["Authorization", "Content-Type"],
    "methods": ["GET", "POST", "OPTIONS"]
}})

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://admin:abcd1234@database-voting.c5gm60ycmd0d.eu-north-1.rds.amazonaws.com/distributed_voting_system'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'd293f2dee0997cfff9fbfbc61589683030dbfd6d44f42bae1d07c013a22a49f5'
db.init_app(app)
migrate = Migrate(app, db)

@app.before_first_request
def create_tables():
    with app.app_context():
        db.create_all()

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    role = data.get('role', 'voter').lower()

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    if role not in [role.value for role in UserRole]:
        return jsonify({'error': 'Invalid role specified'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already exists"}), 400

    new_user = User(username=username, role=UserRole(role), email=email)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": f"User registered successfully as {role}"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data.get('username')).first()
    if user and user.check_password(data.get('password')):
        # Generate JWT token
        token = jwt.encode({'username': user.username}, app.config['SECRET_KEY'], algorithm='HS256')
        return jsonify({"message": "Login successful", "token": token, "userId": user.id}), 200

    return jsonify({"message": "Invalid username or password"}), 401


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001, threaded=True)