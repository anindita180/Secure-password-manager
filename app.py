from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from pymongo import MongoClient
from bson import ObjectId
import base64
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)

# MongoDB setup
client = MongoClient('mongodb://localhost:27017/')
db = client.password_manager

# Add this after your imports
MASTER_KEY_SALT = b'\x8a\x1f\x9b\x3e\x4c\x5d\x6f\x7a\x8b\x9c\x0d\x1e\x2f\x3a\x4b\x5c'

def generate_key(password: str, salt: bytes = None) -> tuple:
    """Generate encryption key using PBKDF2"""
    if not salt:
        salt = os.urandom(16)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encaode(kdf.derive(password.encode()))
    return Fernet(key), salt

@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    
    data = request.get_json()
    username = data.get('username')
    master_password = data.get('password')
    
    if db.users.find_one({'username': username}):
        return jsonify({'error': 'Username already exists'}), 400
    
    # Use constant salt instead of generating new one
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=MASTER_KEY_SALT,
        iterations=100000,
    )
    encrypted_master_password = base64.b64encode(
        kdf.derive(master_password.encode())
    ).decode('utf-8')
    
    # Remove salt from storage
    user_id = db.users.insert_one({
        'username': username,
        'encrypted_master_password': encrypted_master_password
    }).inserted_id
    
    session['user_id'] = str(user_id)
    session['username'] = username
    return jsonify({'success': True})

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    user = db.users.find_one({'username': username})
    if not user:
        return jsonify({'error': 'Invalid credentials'}), 401

    # Verify master password
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=user['salt'],
        iterations=100000,
    )
    hashed_password = base64.b64encode(
        kdf.derive(password.encode())
    ).decode('utf-8')
    
    if hashed_password != user['encrypted_master_password']:
        return jsonify({'error': 'Invalid credentials'}), 401
    
    session['user_id'] = str(user['_id'])
    session['username'] = username
    return jsonify({'success': True})

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', username=session.get('username'))

@app.route('/store_password', methods=['POST'])
def store_password():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        service = data.get('service')
        email = data.get('email')
        password = data.get('password')
        master_password = data.get('master_password')
        
        if not all([service, email, password, master_password]):
            return jsonify({'error': 'All fields are required'}), 400
        
        user = db.users.find_one({'_id': ObjectId(session['user_id'])})
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Use constant salt
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=MASTER_KEY_SALT,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(master_password.encode()))
        cipher = Fernet(key)
        
        encrypted_password = cipher.encrypt(password.encode()).decode()
        
        db.passwords.insert_one({
            'user_id': session['user_id'],
            'service': service,
            'email': email,
            'encrypted_password': encrypted_password
        })
        
        return jsonify({'success': True, 'message': 'Password stored successfully'})
        
    except Exception as e:
        print(f"Storage error: {str(e)}")
        return jsonify({'error': f'Failed to store password: {str(e)}'}), 500

@app.route('/get_passwords', methods=['GET'])
def get_passwords():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        passwords = list(db.passwords.find(
            {'user_id': session['user_id']},
            {'_id': 0, 'user_id': 0}
        ))
        return jsonify(passwords)
    except Exception as e:
        print(f"Error getting passwords: {str(e)}")  # For debugging
        return jsonify({'error': 'Failed to get passwords'}), 500

@app.route('/decrypt_password', methods=['POST'])
def decrypt_password():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        encrypted_password = data.get('encrypted_password')
        master_password = data.get('master_password')
        
        if not all([encrypted_password, master_password]):
            return jsonify({'error': 'All fields are required'}), 400

        # Use constant salt
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=MASTER_KEY_SALT,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(master_password.encode()))
        cipher = Fernet(key)
        
        decrypted_password = cipher.decrypt(encrypted_password.encode()).decode()
        return jsonify({'password': decrypted_password})
        
    except Exception as e:
        print(f"Decryption error: {str(e)}")
        return jsonify({'error': 'Failed to decrypt password'}), 500

@app.route('/delete_password', methods=['POST'])
def delete_password():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        service = data.get('service')
        email = data.get('email')
        
        result = db.passwords.delete_one({
            'user_id': session['user_id'],
            'service': service,
            'email': email
        })
        
        if result.deleted_count == 0:
            return jsonify({'error': 'Password not found'}), 404
        return jsonify({'success': True, 'message': 'Password deleted successfully'})
    except Exception as e:
        print(f"Error deleting password: {str(e)}")  # For debugging
        return jsonify({'error': 'Failed to delete password'}), 500

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True) 