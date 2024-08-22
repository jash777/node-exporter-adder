document.addEventListener('DOMContentLoaded', (event) => {
    const addNodeForm = document.getElementById('add-node-form');
    const messagesDiv = document.getElementById('messages');

    addNodeForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const hostname = document.getElementById('hostname').value;
        addNodeExporter(hostname);
    });

    function addNodeExporter(hostname) {
        fetch('/add_node_exporter', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `hostname=${encodeURIComponent(hostname)}`
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                messagesDiv.innerHTML = `<p style="color: #00ff00;">${data.message}</p>`;
                location.reload(); // Reload the page to show the new node exporter
            } else {
                messagesDiv.innerHTML = `<p style="color: #ff0000;">${data.message}</p>`;
            }
        })
        .catch((error) => {
            console.error('Error:', error);
            messagesDiv.innerHTML = '<p style="color: #ff0000;">An error occurred. Please try again.</p>';
        });
    }

    window.checkNodeStatus = function(nodeId) {
        fetch(`/check_node_exporter/${nodeId}`)
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                const nodeElement = document.getElementById(`node-${nodeId}`);
                const statusSpan = nodeElement.querySelector('.status');
                statusSpan.className = `status ${data.node_status.toLowerCase()}`;
                statusSpan.textContent = data.node_status.charAt(0).toUpperCase() + data.node_status.slice(1);
            } else {
                messagesDiv.innerHTML = `<p style="color: #ff0000;">${data.message}</p>`;
            }
        })
        .catch((error) => {
            console.error('Error:', error);
            messagesDiv.innerHTML = '<p style="color: #ff0000;">An error occurred while checking the node status.</p>';
        });
    }
});
function checkNodeStatus(nodeId) {
    fetch(`/check_node_exporter/${nodeId}`)
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            const statusElement = document.querySelector(`#node-${nodeId} .status`);
            statusElement.textContent = data.node_status;
            statusElement.className = `status ${data.node_status.toLowerCase()}`;
        } else {
            console.error('Failed to check node status');
        }
    })
    .catch(error => console.error('Error:', error));
}