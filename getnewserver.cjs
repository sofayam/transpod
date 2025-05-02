// This is a Node.js server that waits for a request and then calls the getnewpodcasts.sh script in the correct environment

const express = require('express');
const { spawn } = require('child_process');
const path = require('path');
const http = require('http');
const fs = require('fs');  

// Configuration
const PORT = 8015;
const SCRIPT_PATH = path.join(__dirname, 'getnewpodcasts.sh');
const DEFAULT_DELAY = 6 * 60 * 60 * 1000; // Default delay duration in milliseconds 

// State
let lastAccessTime = null;

// Create an Express app
const app = express();

/**
 * Get the delay duration for the next script run.
 * @returns {number} The delay in milliseconds.
 */
function getDelayDuration() {
    return DEFAULT_DELAY; // This can be replaced with dynamic logic if needed in the future
}

/**
 * Calculate the remaining delay until the next script run.
 * @returns {number} The remaining delay in milliseconds.
 */
function calculateRemainingDelay() {
    const now = Date.now();
    if (!lastAccessTime) {
        return 0; // Run immediately if no previous access time
    }
    const elapsed = now - lastAccessTime;
    return Math.max(getDelayDuration() - elapsed, 0); // Wait for the remaining time
}

/**
 * Schedule the next script run.
 */
function scheduleNextRun() {
    const delay = calculateRemainingDelay();
    console.log(`Next script run scheduled in ${(delay / (60 * 60 * 1000)).toFixed(2)} hours.`);
    setTimeout(() => {
        triggerScriptIfNeeded();
        scheduleNextRun(); // Schedule the next run after this one
    }, delay);
}

/**
 * Trigger the script if the delay duration has passed.
 */
function triggerScriptIfNeeded() {
    const now = Date.now();
    if (!lastAccessTime || now - lastAccessTime >= getDelayDuration()) {
        const currentDateTime = new Date().toISOString();
        console.log(`The delay duration has passed since the last call. Triggering script automatically at ${currentDateTime}.`);
        http.get(`http://localhost:${PORT}/getnew`, (res) => {
            console.log(`Self-triggered script response status: ${res.statusCode}`);
        }).on('error', (err) => {
            console.error(`Error self-triggering script: ${err.message}`);
        });
    }
}

/**
 * Execute the script and stream its output to the response.
 * @param {object} res - The Express response object.
 */
function executeScript(res) {
    // append the current date and time to the script execution log in podcatch.log
    const logFilePath = path.join(__dirname, 'podcatch.log');   
    const currentDateTime = new Date().toISOString();
    const logMessage = `Check for new episodes at ${currentDateTime}\n`;
    require('fs').appendFile(logFilePath, logMessage, (err) => {
        if (err) {
            console.error(`Error writing to log file: ${err.message}`);
        } else {
            console.log(`Log message written to ${logFilePath}`);
        }
    });

    console.log('Executing script...');
    const process = spawn('zsh', [SCRIPT_PATH]);

    // Set response headers for streaming
    res.setHeader('Content-Type', 'text/plain');

    // Stream stdout to the response
    process.stdout.on('data', (data) => {
        // console.log(`Script output: ${data}`);
        res.write(data);
    });

    // Stream stderr to the response
    process.stderr.on('data', (data) => {
        // console.error(`${data}`);
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
}

// Route to execute the script
app.get('/getnew', (req, res) => {
    const currentDateTime = new Date().toISOString();
    console.log(`Received request to run the script at ${currentDateTime}.`);

    // Update the last access time
    lastAccessTime = Date.now();

    // Execute the script
    executeScript(res);
});

app.get('/log', (req, res) => {
    const logFilePath = path.join(__dirname, 'podcatch.log');
    // send the first n lines of the log file
    const n = 20; // number of lines to send
 
    fs.readFile(logFilePath, 'utf8', (err, data) => {
        if (err) {
            console.error(`Error reading log file: ${err.message}`);
            res.status(500).send('Error reading log file');
            return;
        }
        const lines = data.split('\n').slice(-n).join('\n'); // Get the last n lines
        res.send(lines);
    });
})

// Start the server
app.listen(PORT, () => {
    console.log(`Podcast update server running on http://localhost:${PORT}`);
    scheduleNextRun(); // Start the scheduling process
});



