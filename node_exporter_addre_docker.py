import os
import logging
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.middleware.proxy_fix import ProxyFix
import yaml
import requests
import docker

# Configure logging
logging.basicConfig(filename='app.log', level=logging.INFO,
                    format='%(asctime)s [%(levelname)s] - %(message)s')

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
app.config['SECRET_KEY'] = os.urandom(24)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///monitoring.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class NodeExporter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String(100), unique=True, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Unknown')

with app.app_context():
    db.create_all()

def get_prometheus_container():
    client = docker.from_env()
    containers = client.containers.list()
    for container in containers:
        if 'prometheus' in container.name.lower():
            return container
    raise Exception("Prometheus container not found")

def find_prometheus_config_path():
    prometheus_container = get_prometheus_container()
    mounts = prometheus_container.attrs['Mounts']
    for mount in mounts:
        if mount['Destination'] == '/etc/prometheus/prometheus.yml':
            return mount['Source']
    raise Exception("Prometheus configuration file mount not found")

def update_prometheus_config(new_target):
    try:
        config_path = find_prometheus_config_path()
        logging.info(f"Found Prometheus config at: {config_path}")

        # Read the current configuration
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)

        # Find the scrape_configs section
        scrape_configs = config.get('scrape_configs', [])

        # Find or create the node_exporter job
        node_exporter_job = next((job for job in scrape_configs if job['job_name'] == 'node_exporter'), None)
        if not node_exporter_job:
            node_exporter_job = {'job_name': 'node_exporter', 'static_configs': [{'targets': []}]}
            scrape_configs.append(node_exporter_job)

        # Add the new target
        node_exporter_job['static_configs'][0]['targets'].append(f"{new_target}:9100")

        # Write the updated configuration back to the file
        with open(config_path, 'w') as file:
            yaml.dump(config, file)

        # Reload Prometheus configuration
        prometheus_container = get_prometheus_container()
        reload_result = prometheus_container.exec_run('killall -HUP prometheus')
        if reload_result.exit_code != 0:
            raise Exception(f"Failed to reload Prometheus: {reload_result.output.decode()}")

        logging.info("Prometheus configuration updated and reloaded successfully")
    except Exception as e:
        logging.error(f"Error in update_prometheus_config: {str(e)}")
        raise

@app.route('/')
def index():
    node_exporters = NodeExporter.query.all()
    return render_template('index.html', node_exporters=node_exporters)

@app.route('/add_node_exporter', methods=['POST'])
def add_node_exporter():
    hostname = request.form['hostname']
    if not hostname:
        return jsonify({'status': 'error', 'message': 'Hostname is required'}), 400

    existing_node = NodeExporter.query.filter_by(hostname=hostname).first()
    if existing_node:
        return jsonify({'status': 'error', 'message': 'Node Exporter already exists'}), 400

    try:
        new_node = NodeExporter(hostname=hostname, status='Unknown')
        db.session.add(new_node)

        # Update Prometheus configuration
        update_prometheus_config(hostname)
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Node Exporter added and Prometheus updated successfully'})
    except Exception as e:
        db.session.rollback()
        logging.error(f"Failed to add Node Exporter: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Failed to add Node Exporter', 'details': str(e)}), 500

@app.route('/check_node_exporter/<int:node_id>')
def check_node_exporter(node_id):
    node = NodeExporter.query.get_or_404(node_id)
    try:
        response = requests.get(f"http://{node.hostname}:9100/metrics", timeout=5)
        if response.status_code == 200:
            node.status = 'Active'
        else:
            node.status = 'Inactive'
    except requests.RequestException:
        node.status = 'Unreachable'

    db.session.commit()
    return jsonify({'status': 'success', 'node_status': node.status})

if __name__ == '__main__':
    port = 5000
    print(f"\nStarting the application...")
    print(f"Once the server has started, open your browser and navigate to: http://localhost:{port}")
    print("If you're running this on a remote server, replace 'localhost' with the server's IP address.")
    app.run(debug=False, host='0.0.0.0', port=port)
