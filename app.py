from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
from models import get_db_connection
from services.token_factory import TokenFactory
from services.bonus_observer import bonus_observer
import datetime

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your-secret-key'

jwt = JWTManager(app)
# init_db()

@app.route('/auth/register', methods=['POST'])
def register():
    data = request.json
    name = data.get('name')
    password = data.get('password')

    if not name or not password:
        return jsonify({'error': 'Name and password are required'}), 400

    hashed_password = generate_password_hash(password)

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE name = ?', (name,)).fetchone()

    if user:
        conn.close()
        return jsonify({'error': 'User already exists'}), 409

    conn.execute(
        'INSERT INTO users (name, password) VALUES (?, ?)',
        (name, hashed_password)
    )
    conn.commit()
    conn.close()

    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/auth/login', methods=['POST'])
def login():
    data = request.json
    name = data.get('name')
    password = data.get('password')
    print(name, password)

    if not name or not password:
        return jsonify({'error': 'Name and password are required'}), 400

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE name = ?', (name,)).fetchone()
    conn.close()

    if not user or not check_password_hash(user['password'], password):
        return jsonify({'error': 'Invalid credentials'}), 401

    token = create_access_token(identity={'user_id': user['id']})

    return jsonify({'access_token': token})


@app.route('/users/<int:id>/bonus', methods=['GET'])
@jwt_required()
def get_bonus(id):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (id,)).fetchone()
    conn.close()
    if user:
        return jsonify({'bonus_level': user['bonus_level']})
    return jsonify({'error': 'User not found'}), 404

@app.route('/users/<int:id>/transactions', methods=['POST'])
@jwt_required()
def add_transaction(id):
    data = request.json
    amount = data.get('amount')
    
    conn = get_db_connection()
    conn.execute('INSERT INTO transactions (user_id, amount) VALUES (?, ?)', (id, amount))
    conn.commit()
    conn.close()
    
    bonus_observer.notify(id, amount)
    return jsonify({'message': 'Transaction added successfully'})

@app.route('/users', methods=['GET'])
# @jwt_required()  # Эндпоинт требует авторизации
def get_all_users():
    conn = get_db_connection()
    users = conn.execute('SELECT id, name, bonus_level FROM users').fetchall()
    conn.close()
    
    users_list = [
        {'id': user['id'], 'name': user['name'], 'bonus_level': user['bonus_level']}
        for user in users
    ]
    return jsonify(users_list)

if __name__ == '__main__':
    app.run(debug=True)
