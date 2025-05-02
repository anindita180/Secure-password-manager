# 🔒 Secure Password Manager

A secure, full-stack password manager application that helps users store and manage their passwords safely.

## 🎯 Purpose

This application provides a secure way to store and manage passwords for various services. It uses strong encryption to ensure that your passwords are safe even if the database is compromised.

## 🖥️ Tech Stack

### Backend
- **Flask** - Python web framework
- **MongoDB** - NoSQL database
- **Cryptography** - For encryption/decryption
  - Fernet symmetric encryption
  - PBKDF2HMAC for key derivation
  - SHA256 for hashing

### Frontend
- HTML5
- CSS3
- Vanilla JavaScript
- Flask Templates (Jinja2)

## 🚀 How to Run the Project

### Prerequisites
- Python 3.7+
- MongoDB
- pip (Python package manager)

### Installation Steps

1. Clone the repository:
```bash
git clone https://github.com/yourusername/secure-password-manager.git
cd secure-password-manager
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On Unix or MacOS
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Start MongoDB service:
```bash
# Make sure MongoDB is running on localhost:27017
```

5. Run the application:
```bash
python app.py
```

6. Open your browser and navigate to:
```
http://localhost:5000
```

## 🔐 Security Features

- **Master Password Protection**: All passwords are encrypted using a master password
- **Salted Key Derivation**: Uses PBKDF2 with SHA256 for secure key derivation
- **Encryption at Rest**: All passwords are encrypted before storage
- **Session Management**: Secure session handling for user authentication
- **CSRF Protection**: Built-in protection against Cross-Site Request Forgery

## 📂 Project Structure

```
secure-password-manager/
├── app.py                 # Main application file
├── requirements.txt       # Python dependencies
├── static/               # Static files (CSS, JS)
│   ├── styles.css
│   └── script.js
├── templates/            # HTML templates
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   └── dashboard.html
└── README.md            # Project documentation
```

## 📸 Screenshots

![image](https://github.com/user-attachments/assets/fdab68f1-cf55-42ce-9036-e1eb5c39644d)
![image](https://github.com/user-attachments/assets/b5a473f5-20c6-4f92-875e-0b0553b695c9)
![image](https://github.com/user-attachments/assets/779ce37e-8184-412e-bf22-cbc64a6e7466)


## 🙋 Author

[Anindita Das Badhan]
- GitHub: [anindita180]
- Email: [aninditadas2704@gmail.com]

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 
