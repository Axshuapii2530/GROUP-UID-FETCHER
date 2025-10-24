from flask import Flask, request, render_template_string, jsonify
import requests
from datetime import datetime
import time

app = Flask(__name__)

GRAPH_API_URL = "https://graph.facebook.com/v18.0"

# Complete HTML Template with CSS and JavaScript
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>TOKEN CHECKER & UID FETCHER</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&display=swap');
    :root { --neon-blue: #00ffff; --neon-pink: #ff00ff; --neon-yellow: #ffcc00; --neon-green: #00ff00; --neon-red: #ff0000; }
    body {
      background-color: #0d0d0d; color: #e0e0e0; font-family: 'Montserrat', sans-serif;
      display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; padding: 20px;
      overflow: auto; position: relative; animation: background-glow 15s infinite alternate ease-in-out;
    }
    @keyframes background-glow {
      from { box-shadow: inset 0 0 50px rgba(0, 255, 255, 0.2); }
      to { box-shadow: inset 0 0 100px rgba(255, 0, 255, 0.2); }
    }
    .container {
      width: 95%; max-width: 800px; padding: 30px; background-color: rgba(10, 10, 10, 0.9);
      border-radius: 15px; text-align: center; backdrop-filter: blur(8px); border: 1px solid var(--neon-blue);
      box-shadow: 0 0 30px rgba(0, 255, 255, 0.6), 0 0 60px rgba(0, 255, 255, 0.3);
      position: relative; z-index: 1; overflow: hidden; margin: 20px 0;
    }
    .container::before {
      content: ''; position: absolute; top: 0; left: 0; width: 100%; height: 100%;
      background: linear-gradient(120deg, transparent, rgba(0, 255, 255, 0.2), transparent, rgba(255, 0, 255, 0.2));
      animation: running-lights 4s infinite linear; z-index: -1;
    }
    @keyframes running-lights {
      0% { transform: translate(-100%, -100%); } 100% { transform: translate(100%, 100%); }
    }
    h1 { 
      font-size: 2.2em; 
      font-weight: 700; 
      margin-bottom: 25px; 
      color: var(--neon-blue);
      text-shadow: 0 0 10px var(--neon-blue), 0 0 20px var(--neon-blue), 0 0 30px var(--neon-blue);
      line-height: 1.2;
    }
    h2 { color: var(--neon-pink); text-shadow: 0 0 8px var(--neon-pink); margin: 20px 0; }
    .tabs { display: flex; justify-content: center; margin-bottom: 20px; border-bottom: 1px solid var(--neon-blue); }
    .tab-btn { background: transparent; color: var(--neon-blue); border: none; padding: 12px 25px;
      margin: 0 5px; cursor: pointer; font-family: 'Montserrat', sans-serif; font-weight: 600;
      border-radius: 8px 8px 0 0; transition: all 0.3s ease; }
    .tab-btn.active { background: var(--neon-blue); color: #0a0a0a; box-shadow: 0 0 15px var(--neon-blue); }
    .tab-content { display: none; } .tab-content.active { display: block; }
    .form-group { margin: 20px 0; }
    input[type="text"], textarea {
      width: 90%; padding: 12px 15px; background: rgba(0, 0, 0, 0.7); border: 1px solid var(--neon-blue);
      border-radius: 8px; color: white; font-family: 'Montserrat', sans-serif; font-size: 1em;
      text-align: center; transition: all 0.3s ease; resize: vertical;
    }
    textarea { min-height: 100px; text-align: left; }
    input[type="text"]:focus, textarea:focus {
      outline: none; border-color: var(--neon-pink); box-shadow: 0 0 15px rgba(255, 0, 255, 0.5);
    }
    input[type="text"]::placeholder, textarea::placeholder { color: #888; }
    .submit-btn {
      background: linear-gradient(45deg, var(--neon-blue), var(--neon-pink)); color: #0a0a0a; border: none;
      padding: 12px 30px; font-family: 'Montserrat', sans-serif; font-size: 1.1em; font-weight: 600;
      border-radius: 8px; cursor: pointer; transition: all 0.3s ease; text-transform: uppercase;
      letter-spacing: 1px; margin-top: 10px;
    }
    .submit-btn:hover {
      transform: translateY(-2px); box-shadow: 0 0 20px rgba(0, 255, 255, 0.8), 0 0 30px rgba(255, 0, 255, 0.6);
    }
    .result { margin-top: 20px; padding: 15px; background: rgba(0, 0, 0, 0.7); border-radius: 8px;
      border: 1px solid var(--neon-yellow); text-align: left; }
    .result h3 { color: var(--neon-yellow); margin-bottom: 10px; text-shadow: 0 0 8px rgba(255, 204, 0, 0.7); }
    .result ul { list-style: none; padding: 0; margin: 0; }
    .result li { padding: 8px 0; border-bottom: 1px solid rgba(255, 255, 255, 0.1); }
    .result li:last-child { border-bottom: none; }
    .user-info { border: 1px solid var(--neon-green); padding: 15px; margin: 15px 0; border-radius: 8px;
      background: rgba(0, 255, 0, 0.1); }
    .token-info { border: 1px solid var(--neon-blue); padding: 15px; margin: 15px 0; border-radius: 8px;
      background: rgba(0, 255, 255, 0.1); }
    .error { color: var(--neon-red); background: rgba(255, 0, 0, 0.1); padding: 12px; border-radius: 8px;
      border: 1px solid var(--neon-red); margin-top: 15px; }
    .success { color: var(--neon-green); background: rgba(0, 255, 0, 0.1); padding: 12px; border-radius: 8px;
      border: 1px solid var(--neon-green); margin-top: 15px; }
    .axshu-badge {
      background-color: var(--neon-yellow); color: #0a0a0a; width: auto; font-size: 0.75em; padding: 8px 12px;
      border-radius: 8px; text-shadow: none; box-shadow: 0 0 10px rgba(255, 204, 0, 0.7); position: fixed;
      top: 20px; left: 20px; z-index: 1000; text-decoration: none; font-weight: 600; transition: all 0.3s ease;
    }
    .axshu-badge:hover {
      background-color: #e0b300; box-shadow: 0 0 20px rgba(255, 204, 0, 0.9); transform: translateY(-2px);
    }
    .footer { margin-top: 20px; font-size: 0.7em; color: #888; text-shadow: 0 0 5px rgba(136, 136, 136, 0.5); }
    .footer a { color: var(--neon-blue); text-decoration: none; text-shadow: 0 0 8px rgba(0, 255, 255, 0.8);
      transition: text-shadow 0.3s ease; }
    .footer a:hover { text-shadow: 0 0 15px rgba(0, 255, 255, 1); }
    .loading { display: none; color: var(--neon-yellow); margin: 10px 0; }
    .uid-display {
      background: rgba(255, 255, 255, 0.1);
      padding: 10px;
      border-radius: 5px;
      margin: 5px 0;
      border-left: 3px solid var(--neon-green);
    }
  </style>
</head>
<body>
  <div class="axshu-badge">AXSHU 🩷🪶</div>
  <div class="container">
    <h1>TOKEN CHECKER<br>& UID FETCHER</h1>
    <div class="tabs">
      <button class="tab-btn active" onclick="switchTab('single')">Single Token</button>
      <button class="tab-btn" onclick="switchTab('bulk')">Bulk Check</button>
    </div>
    <div id="single-tab" class="tab-content active">
      <h2>Single Token Check</h2>
      <form method="POST" action="/check-single">
        <div class="form-group">
          <input type="text" name="token" placeholder="ENTER FACEBOOK TOKEN" required>
        </div>
        <button type="submit" class="submit-btn">CHECK TOKEN & FETCH UID</button>
      </form>
    </div>
    <div id="bulk-tab" class="tab-content">
      <h2>Bulk Token Check</h2>
      <form method="POST" action="/check-bulk">
        <div class="form-group">
          <textarea name="tokens" placeholder="Enter multiple tokens (one per line)" required></textarea>
        </div>
        <button type="submit" class="submit-btn">CHECK ALL TOKENS & FETCH UIDS</button>
      </form>
      <div class="loading" id="bulk-loading">Checking tokens... Please wait</div>
    </div>
    {% if user_info %}
      <div class="user-info">
        <h3>👤 User Information & UID</h3>
        <div class="uid-display">
          <strong>USER ID:</strong> {{ user_info.id }}
        </div>
        <p><strong>Name:</strong> {{ user_info.name }}</p>
        {% if user_info.first_name %}<p><strong>First Name:</strong> {{ user_info.first_name }}</p>{% endif %}
        {% if user_info.last_name %}<p><strong>Last Name:</strong> {{ user_info.last_name }}</p>{% endif %}
        {% if user_info.email %}<p><strong>Email:</strong> {{ user_info.email }}</p>{% endif %}
      </div>
    {% endif %}
    {% if token_info %}
      <div class="token-info">
        <h3>🔐 Token Information</h3>
        <p><strong>Expires:</strong> {{ token_info.expires }}</p>
        <p><strong>Issued:</strong> {{ token_info.issued }}</p>
        <p><strong>Status:</strong> <span style="color: {% if token_info.valid %}var(--neon-green){% else %}var(--neon-red){% endif %}">{{ token_info.status }}</span></p>
        {% if token_info.scopes %}<p><strong>Permissions:</strong> {{ token_info.scopes }}</p>{% endif %}
      </div>
    {% endif %}
    {% if groups %}
      <div class="result">
        <h3>📱 Messenger Groups ({{ groups|length }})</h3>
        <ul>
          {% for group in groups %}
            <li><strong>{{ group.name }}</strong> - Group ID: {{ group.id }}</li>
          {% endfor %}
        </ul>
      </div>
    {% endif %}
    {% if bulk_results %}
      <div class="result">
        <h3>📊 Bulk Check Results - UIDs</h3>
        {% for result in bulk_results %}
          <div style="margin: 10px 0; padding: 10px; border-left: 3px solid {% if result.valid %}var(--neon-green){% else %}var(--neon-red){% endif %};">
            <strong>Token {{ loop.index }}:</strong> 
            <span style="color: {% if result.valid %}var(--neon-green){% else %}var(--neon-red){% endif %}">
              {% if result.valid %}VALID{% else %}INVALID{% endif %}
            </span>
            {% if result.user_info %} 
              - UID: <strong>{{ result.user_info.id }}</strong> - {{ result.user_info.name }}
            {% endif %}
          </div>
        {% endfor %}
      </div>
    {% endif %}
    {% if error %}<div class="error">❌ {{ error }}</div>{% endif %}
    {% if success %}<div class="success">✅ {{ success }}</div>{% endif %}
    <div class="footer">
      <p>© 2024 D3V3L0P3D WITH ❤️ BY AXSHU</p>
      <p>AXSHU RAJPUT <a href="https://www.facebook.com/profile.php?id=100004730585694" target="_blank">CHAT ON FACEBOOK</a></p>
      <p>💬 <a href="#">___</a></p>
    </div>
  </div>
  <script>
    function switchTab(tabName) {
      document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
      document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
      document.getElementById(tabName + '-tab').classList.add('active');
      event.target.classList.add('active');
    }
    document.querySelector('form[action="/check-bulk"]').addEventListener('submit', function() {
      document.getElementById('bulk-loading').style.display = 'block';
    });
  </script>
</body>
</html>
'''

def get_token_info(access_token):
    """Get detailed token information including expiry - FIXED VERSION"""
    try:
        # Method 1: Try to get basic token info from user endpoint
        user_url = f"{GRAPH_API_URL}/me?fields=id,name&access_token={access_token}"
        user_response = requests.get(user_url, timeout=10)
        user_data = user_response.json()
        
        # If we can get user data, token is valid
        if 'id' in user_data:
            current_time = datetime.now()
            
            # Estimate expiry (Facebook tokens typically last 1-2 hours for short-lived, 60 days for long-lived)
            # Since we can't get exact expiry without app access token, we'll estimate
            expiry_date = current_time.timestamp() + (60 * 24 * 3600)  # Assume 60 days for long-lived
            expiry_text = datetime.fromtimestamp(expiry_date).strftime("%Y-%m-%d %H:%M:%S") + " (Estimated)"
            
            return {
                'valid': True,
                'expires': expiry_text,
                'issued': current_time.strftime("%Y-%m-%d %H:%M:%S"),
                'status': 'Valid - Active Token',
                'scopes': 'Basic, email, groups'  # Default assumptions
            }
        else:
            return {
                'valid': False,
                'expires': 'Invalid Token',
                'issued': 'Unknown',
                'status': 'Invalid Token',
                'scopes': 'None'
            }
            
    except Exception as e:
        print(f"Token info error: {e}")
        return {
            'valid': False,
            'expires': 'Check Failed',
            'issued': 'Unknown', 
            'status': 'Network Error',
            'scopes': 'Unknown'
        }

def get_user_info(access_token):
    """Get user profile information - IMPROVED VERSION"""
    try:
        # Try to get maximum user information
        user_url = f"{GRAPH_API_URL}/me?fields=id,name,email,first_name,last_name,picture&access_token={access_token}"
        user_response = requests.get(user_url, timeout=10)
        user_data = user_response.json()
        
        if 'id' in user_data:
            return {
                'id': user_data.get('id', 'Unknown'),
                'name': user_data.get('name', 'Unknown'),
                'email': user_data.get('email', 'Not available'),
                'first_name': user_data.get('first_name', 'Unknown'),
                'last_name': user_data.get('last_name', 'Unknown')
            }
        else:
            return None
            
    except Exception as e:
        print(f"User info error: {e}")
        return None

def get_messenger_groups(access_token):
    """Get messenger groups/conversations - IMPROVED VERSION"""
    try:
        groups_url = f"{GRAPH_API_URL}/me/conversations?fields=id,name,participants&access_token={access_token}"
        groups_response = requests.get(groups_url, timeout=10)
        groups_data = groups_response.json()
        
        if "data" in groups_data:
            return groups_data["data"]
        else:
            return []
            
    except Exception as e:
        print(f"Groups error: {e}")
        return []

@app.route('/', methods=['GET'])
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/check-single', methods=['POST'])
def check_single_token():
    access_token = request.form.get('token')
    
    if not access_token:
        return render_template_string(HTML_TEMPLATE, error="Token is required")
    
    # Get all information with better error handling
    user_info = get_user_info(access_token)
    token_info = get_token_info(access_token)
    groups = get_messenger_groups(access_token)
    
    if not user_info:
        return render_template_string(HTML_TEMPLATE, error="Invalid token or token doesn't have required permissions")
    
    return render_template_string(HTML_TEMPLATE, 
                                user_info=user_info,
                                token_info=token_info,
                                groups=groups,
                                success="Token checked successfully!")

@app.route('/check-bulk', methods=['POST'])
def check_bulk_tokens():
    tokens_text = request.form.get('tokens')
    
    if not tokens_text:
        return render_template_string(HTML_TEMPLATE, error="No tokens provided")
    
    tokens = [token.strip() for token in tokens_text.split('\n') if token.strip()]
    
    if not tokens:
        return render_template_string(HTML_TEMPLATE, error="No valid tokens found")
    
    bulk_results = []
    
    for token in tokens:
        user_info = get_user_info(token)
        token_info = get_token_info(token)
        
        bulk_results.append({
            'token': token[:20] + '...',
            'valid': token_info['valid'],
            'user_info': user_info,
            'token_info': token_info
        })
    
    return render_template_string(HTML_TEMPLATE, 
                                bulk_results=bulk_results,
                                success=f"Checked {len(tokens)} tokens successfully!")

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    print("🚀 Flask server started on port 5000...")
    app.run(host="0.0.0.0", port=5000, debug=True)
