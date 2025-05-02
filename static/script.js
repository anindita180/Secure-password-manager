// Handle form submissions and UI interactions
document.addEventListener('DOMContentLoaded', function() {
    // Load passwords if on dashboard
    if (window.location.pathname === '/dashboard') {
        loadPasswords();
    }

    // Register form handler
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            
            try {
                const response = await fetch('/register', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, password })
                });
                
                if (response.ok) {
                    window.location.href = '/dashboard';
                } else {
                    const data = await response.json();
                    alert(data.error || 'Registration failed');
                }
            } catch (error) {
                alert('Registration failed');
            }
        });
    }

    // Login form handler
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            
            try {
                const response = await fetch('/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, password })
                });
                
                if (response.ok) {
                    window.location.href = '/dashboard';
                } else {
                    const data = await response.json();
                    alert(data.error || 'Login failed');
                }
            } catch (error) {
                alert('Login failed');
            }
        });
    }

    // Password storage form handler
    const passwordForm = document.getElementById('passwordForm');
    if (passwordForm) {
        passwordForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const service = document.getElementById('service').value;
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const masterPassword = prompt('Enter your master password to encrypt:');
            
            if (!masterPassword) {
                alert('Master password is required');
                return;
            }
            
            try {
                const response = await fetch('/store_password', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        service,
                        email,
                        password,
                        master_password: masterPassword
                    })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    alert('Password stored successfully!');
                    passwordForm.reset();
                    loadPasswords();
                } else {
                    alert(data.error || 'Failed to store password');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Failed to store password');
            }
        });
    }
});

async function loadPasswords() {
    const passwordList = document.getElementById('passwordList');
    try {
        const response = await fetch('/get_passwords');
        const passwords = await response.json();
        
        passwordList.innerHTML = passwords.map(pass => `
            <div class="password-entry">
                <h4>${pass.service}</h4>
                <p>Email: ${pass.email}</p>
                <p>Password: ********</p>
                <button onclick="decryptPassword('${pass.encrypted_password}')">Show</button>
                <button onclick="deletePassword('${pass.service}', '${pass.email}')">Delete</button>
            </div>
        `).join('') || '<p>No saved passwords</p>';
    } catch (error) {
        passwordList.innerHTML = '<p>Failed to load passwords</p>';
    }
}

async function decryptPassword(encryptedPassword) {
    const masterPassword = prompt('Enter your master password to decrypt:');
    
    if (!masterPassword) {
        alert('Master password is required');
        return;
    }
    
    try {
        const response = await fetch('/decrypt_password', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                encrypted_password: encryptedPassword,
                master_password: masterPassword
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            alert(`Decrypted password: ${data.password}`);
        } else {
            alert(data.error || 'Failed to decrypt password');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to decrypt password');
    }
}

async function deletePassword(service, email) {
    if (!confirm('Are you sure you want to delete this password?')) return;
    
    try {
        const response = await fetch('/delete_password', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ service, email })
        });
        
        if (response.ok) {
            alert('Password deleted successfully!');
            loadPasswords();
        } else {
            const data = await response.json();
            alert(data.error || 'Failed to delete password');
        }
    } catch (error) {
        alert('Failed to delete password');
    }
}
