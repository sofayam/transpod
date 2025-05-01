// This is a Node.js server that waits for a request and then calls the nightly.sh script in the correct environment

const express = require('express');
const { spawn } = require('child_process');
const path = require('path');

// Define the port and script path
const PORT = 8015;
const SCRIPT_PATH = path.join(__dirname, 'getnewpodcasts.sh');

// Create an Express app
const app = express();

// Route to execute the script
app.get('/getnew', (req, res) => {
    console.log('Received request to run nightly script');

    // Spawn the process to execute the script
    const process = spawn('zsh', [SCRIPT_PATH]);

    // Set response headers for streaming
    res.setHeader('Content-Type', 'text/plain');

    // Stream stdout to the response
    process.stdout.on('data', (data) => {
        console.log(`Script output: ${data}`);
        res.write(data);
    });

    // Stream stderr to the response
    process.stderr.on('data', (data) => {
        console.error(`${data}`);
        res.write(`${data}`);
    });

    // Handle process exit
    process.on('close', (code) => {
        console.log(`Script exited with code ${code}`);
        res.end(`\nProcess finished with exit code ${code}`);
    });

    // Handle errors in spawning the process
    process.on('error', (error) => {
        console.error(`Error spawning process: ${error.message}`);
        res.status(500).end(`Error: ${error.message}`);
    });
});

// Start the server
app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});



