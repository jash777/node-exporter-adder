# Node Exporter Adder for Prometheus

This application provides a web interface to easily add Node Exporter instances to your Prometheus configuration. It's designed to work on Ubuntu servers and requires Prometheus to be pre-installed.

## Prerequisites

- Ubuntu Server
- Prometheus installed and configured
- Python 3.6+
- pip (Python package manager)

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/node-exporter-adder.git
   cd node-exporter-adder
   ```

2. Install the required Python packages:
   ```
   pip install -r requirements.txt
   ```

3. Ensure that the application has the necessary permissions to read and write to the Prometheus configuration file (usually located at `/etc/prometheus/prometheus.yml`). You may need to run the application with sudo or adjust file permissions.

## Usage

1. Start the application:
   ```
   sudo python app.py  |  sudo python app.py   | sudo  python3 app.py
   ```

2. Open your web browser and navigate to `http://your_server_ip:5000`

3. Use the web interface to add new Node Exporter instances:
   - Enter the hostname or IP address of the server running Node Exporter
   - Click "Add Node Exporter"

4. The application will automatically update the Prometheus configuration and reload Prometheus to apply the changes.

5. You can check the status of added Node Exporters using the "Check Status" button.

## Important Notes

- This application assumes that Node Exporter is running on the default port (9100) on the target servers.
- The application needs permission to modify the Prometheus configuration file and send a SIGHUP signal to the Prometheus process.
- Make sure your firewall allows connections to port 9100 on the servers running Node Exporter.

## Troubleshooting

- Check the `app.log` file for any error messages or important information.
- Ensure that Prometheus is running and that its configuration file is accessible.
- Verify that the target servers are reachable and that Node Exporter is running on them.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
