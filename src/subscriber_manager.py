"""
Ferrari F1 Newsletter - Subscriber Manager (SQLite)
Manages newsletter subscriptions using SQLite database
"""

import sqlite3
import os
from datetime import datetime
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)


class SubscriberManager:
    """Manages newsletter subscribers using SQLite"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = os.path.join(
                os.path.dirname(__file__), 
                "..", 
                "data", 
                "subscribers.db"
            )
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize the SQLite database and create tables"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subscribers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                language TEXT DEFAULT 'en',
                subscribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                active INTEGER DEFAULT 1,
                unsubscribed_at TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info(f"Database initialized at {self.db_path}")
    
    def subscribe(self, email: str) -> dict:
        """
        Add a new subscriber
        
        Args:
            email: Subscriber email address
            
        Returns:
            Success/error response
        """
        email = email.lower().strip()
        
        # Validate email
        if not self._is_valid_email(email):
            return {"success": False, "error": "Invalid email address"}
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO subscribers (email, language, active)
                VALUES (?, 'en', 1)
                ON CONFLICT(email) DO UPDATE SET
                    active = 1,
                    unsubscribed_at = NULL
            ''', (email,))
            conn.commit()
            logger.info(f"New subscriber: {email}")
            return {"success": True, "message": "Successfully subscribed"}
        except sqlite3.Error as e:
            logger.error(f"Database error: {e}")
            return {"success": False, "error": "Database error"}
        finally:
            conn.close()
    
    def unsubscribe(self, email: str) -> dict:
        """Remove a subscriber (soft delete)"""
        email = email.lower().strip()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE subscribers 
            SET active = 0, unsubscribed_at = ?
            WHERE email = ?
        ''', (datetime.now().isoformat(), email))
        
        if cursor.rowcount > 0:
            conn.commit()
            conn.close()
            logger.info(f"Unsubscribed: {email}")
            return {"success": True, "message": "Successfully unsubscribed"}
        
        conn.close()
        return {"success": False, "error": "Email not found"}
    
    def get_active_subscribers(self) -> List[dict]:
        """Get list of active subscribers"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT email, subscribed_at
            FROM subscribers
            WHERE active = 1
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_stats(self) -> dict:
        """Get subscription statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM subscribers')
        total = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM subscribers WHERE active = 1')
        active = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "total_subscribers": total,
            "active_subscribers": active
        }
    
    def _is_valid_email(self, email: str) -> bool:
        """Basic email validation"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))


if __name__ == "__main__":
    # Test the subscriber manager
    manager = SubscriberManager()
    
    # Add some test subscribers
    print("Adding test subscribers...")
    print(manager.subscribe("tifoso@ferrari.com"))
    print(manager.subscribe("fan@f1.com"))
    
    # Get stats
    print("\n📊 Subscriber Stats:")
    stats = manager.get_stats()
    print(f"  Total: {stats['total_subscribers']}")
    print(f"  Active: {stats['active_subscribers']}")
    
    # Get active subscribers
    print("\n📧 Active Subscribers:")
    subscribers = manager.get_active_subscribers()
    for sub in subscribers:
        print(f"  {sub['email']}")
