import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional

class Database:
    def __init__(self, db_path: str = "c2_server.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Agents table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agents (
                id TEXT PRIMARY KEY,
                hostname TEXT,
                platform TEXT,
                ip_address TEXT,
                first_seen TIMESTAMP,
                last_seen TIMESTAMP,
                status TEXT
            )
        ''')
        
        # Commands table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS commands (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id TEXT,
                command TEXT,
                module TEXT,
                timestamp TIMESTAMP,
                status TEXT,
                FOREIGN KEY (agent_id) REFERENCES agents(id)
            )
        ''')
        
        # Results table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id TEXT,
                command_id INTEGER,
                module TEXT,
                result TEXT,
                timestamp TIMESTAMP,
                FOREIGN KEY (agent_id) REFERENCES agents(id),
                FOREIGN KEY (command_id) REFERENCES commands(id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def register_agent(self, agent_id: str, hostname: str, platform: str, ip_address: str):
        """Register a new agent or update existing one"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        now = datetime.now()
        cursor.execute('''
            INSERT OR REPLACE INTO agents (id, hostname, platform, ip_address, first_seen, last_seen, status)
            VALUES (?, ?, ?, ?, COALESCE((SELECT first_seen FROM agents WHERE id = ?), ?), ?, 'active')
        ''', (agent_id, hostname, platform, ip_address, agent_id, now, now))
        
        conn.commit()
        conn.close()
    
    def get_agents(self) -> List[Dict]:
        """Get all registered agents"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM agents ORDER BY last_seen DESC')
        agents = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return agents
    
    def get_agent(self, agent_id: str) -> Optional[Dict]:
        """Get specific agent"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM agents WHERE id = ?', (agent_id,))
        row = cursor.fetchone()
        agent = dict(row) if row else None
        
        conn.close()
        return agent
    
    def add_command(self, agent_id: str, command: str, module: str = None) -> int:
        """Add a command for an agent"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO commands (agent_id, command, module, timestamp, status)
            VALUES (?, ?, ?, ?, 'pending')
        ''', (agent_id, command, module, datetime.now()))
        
        command_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return command_id
    
    def get_pending_commands(self, agent_id: str) -> List[Dict]:
        """Get pending commands for an agent"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM commands 
            WHERE agent_id = ? AND status = 'pending'
            ORDER BY timestamp ASC
        ''', (agent_id,))
        
        commands = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return commands
    
    def update_command_status(self, command_id: int, status: str):
        """Update command status"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('UPDATE commands SET status = ? WHERE id = ?', (status, command_id))
        
        conn.commit()
        conn.close()
    
    def add_result(self, agent_id: str, command_id: int, module: str, result: str):
        """Add command result"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO results (agent_id, command_id, module, result, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (agent_id, command_id, module, result, datetime.now()))
        
        conn.commit()
        conn.close()
    
    def get_results(self, agent_id: str = None, module: str = None) -> List[Dict]:
        """Get results with optional filtering"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = 'SELECT * FROM results WHERE 1=1'
        params = []
        
        if agent_id:
            query += ' AND agent_id = ?'
            params.append(agent_id)
        
        if module:
            query += ' AND module = ?'
            params.append(module)
        
        query += ' ORDER BY timestamp DESC'
        
        cursor.execute(query, params)
        results = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return results
