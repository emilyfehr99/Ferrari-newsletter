import os
import sys
import json
from http.server import BaseHTTPRequestHandler

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

# Only import the essential components for signup
try:
    from email_sender import EmailSender
    from subscriber_manager import SubscriberManager
except ImportError as e:
    # Fallback for Vercel's relative imports if needed
    try:
        from src.email_sender import EmailSender
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

            # Initialize managers
            subscribers = SubscriberManager()
            sender = EmailSender()
            
            # Subscribe user (SQLite might be read-only on Vercel, handle gracefully)
            db_result = subscribers.subscribe(email)
            
            # Even if DB fails (read-only), we still want to send the confirmation email
            # This ensures the user experience is preserved for the demo
            email_sent, error_msg = sender.send_confirmation(email)
            
            if email_sent:
                self._send_response(200, {
                    "success": True, 
                    "message": "Successfully subscribed",
                    "db_status": db_result.get("success", False)
                })
            else:
                self._send_response(500, {"success": False, "error": f"Failed to send confirmation email: {error_msg}"})
                
        except Exception as e:
            self._send_response(500, {"success": False, "error": str(e)})

    def _send_response(self, status_code, data):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
