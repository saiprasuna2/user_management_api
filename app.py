from flask import Flask, request, jsonify
import pymysql
import bcrypt
import re

app = Flask(__name__)

def get_db_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='',
        db='user_management_system',
        cursorclass=pymysql.cursors.DictCursor
    )

def sanitize_user_id(user_id):
    clean_id = re.sub(r'\D', '', user_id.strip())
    if not clean_id.isdigit():
        raise ValueError('Invalid user ID')
    return int(clean_id)

@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    required_fields = ['first_name', 'last_name', 'email', 'phone_number', 'password', 'role']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO user_management (first_name, last_name, email, phone_number, password_hash, role)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            data['first_name'],
            data['last_name'],
            data['email'],
            data['phone_number'],
            hashed_password,
            data['role']
        ))
        conn.commit()
        return jsonify({'message': 'User created successfully'}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/users', methods=['GET'])
def get_all_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, first_name, last_name, email, phone_number, role FROM user_management")
        users = cursor.fetchall()
        return jsonify(users), 200
    finally:
        cursor.close()
        conn.close()

@app.route('/users/<user_id>', methods=['GET'])
def get_user(user_id):
    try:
        user_id = sanitize_user_id(user_id)
    except ValueError:
        return jsonify({'error': 'Invalid user ID'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, first_name, last_name, email, phone_number, role FROM user_management WHERE id=%s", (user_id,))
        user = cursor.fetchone()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        return jsonify(user), 200
    finally:
        cursor.close()
        conn.close()

@app.route('/users/<user_id>', methods=['PUT'])
def update_user(user_id):
    try:
        user_id = sanitize_user_id(user_id)
    except ValueError:
        return jsonify({'error': 'Invalid user ID'}), 400

    data = request.get_json()
    allowed_fields = ['first_name', 'last_name', 'email', 'phone_number', 'role', 'password']
    updates = {field: data.get(field) for field in allowed_fields if data.get(field) is not None}

    if not updates:
        return jsonify({'error': 'No data provided for update'}), 400

    if 'password' in updates:
        password = updates['password']
        if len(password) < 8 or not any(c.isdigit() for c in password) or not any(not c.isalnum() for c in password):
            return jsonify({'error': 'Password must be at least 8 characters long and include a number and a special character'}), 400
        updates['password_hash'] = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        del updates['password']

    set_clause = ", ".join([f"{key}=%s" for key in updates])
    values = list(updates.values()) + [user_id]

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(f"UPDATE user_management SET {set_clause} WHERE id=%s", values)
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({'error': 'User not found'}), 404
        return jsonify({'message': 'User updated successfully'}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        user_id = sanitize_user_id(user_id)
    except ValueError:
        return jsonify({'error': 'Invalid user ID'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM user_management WHERE id=%s", (user_id,))
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({'error': 'User not found'}), 404
        return jsonify({'message': 'User deleted successfully'}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({'error': f"Database error: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)
