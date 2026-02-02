import os
import sys
import json
from http.server import BaseHTTPRequestHandler

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

try:
    from subscriber_manager import SubscriberManager
except ImportError:
    try:
        from src.subscriber_manager import SubscriberManager
    except ImportError:
        pass

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data)
            email = data.get('email')
            
            if not email:
                self._send_response(400, {"success": False, "error": "Email is required"})
                return

            subscribers = SubscriberManager()
            result = subscribers.unsubscribe(email)
            
            if result.get("success"):
                self._send_response(200, {"success": True, "message": "Successfully unsubscribed"})
            else:
                # If not found, we still return success to avoid leaking subscriber existence
                # but with a different message internally if needed.
                self._send_response(200, {"success": True, "message": "Email not found or already unsubscribed"})
                
        except Exception as e:
            self._send_response(500, {"success": False, "error": str(e)})

    def do_GET(self):
        # Support GET for direct links from emails
        from urllib.parse import urlparse, parse_qs
        query_components = parse_qs(urlparse(self.path).query)
        email = query_components.get("email", [None])[0]
        
        if not email:
            self._send_response(400, {"success": False, "error": "Email is required"})
            return
            
        try:
            subscribers = SubscriberManager()
            result = subscribers.unsubscribe(email)
            
            # For GET, we might want to redirect to a success page
            self.send_response(302)
            self.send_header('Location', f'/unsubscribe.html?success=true&email={email}')
            self.end_headers()
            
        except Exception as e:
            self._send_response(500, {"success": False, "error": str(e)})

    def _send_response(self, status_code, data):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
