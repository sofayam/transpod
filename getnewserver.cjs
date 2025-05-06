// This is a Node.js server that waits for a request and then calls the getnewpodcasts.sh script in the correct environment

const express = require('express');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');
const fsPromises = fs.promises;


const HOURDELAY = 12
const LOGLINES = 40; // Number of lines to read from the log file

// Configuration
const PORT = 8015;
const SCRIPT_PATH = path.join(__dirname, 'getnewpodcasts.sh');

const DEFAULT_DELAY = HOURDELAY * 60 * 60 * 1000; // Default delay duration in milliseconds (6 hours)
const LOG_FILE_PATH = path.join(__dirname, 'podcatch.log');


// State
let lastAccessTime = null;
let scriptRunning = false;
let scriptTimer = null;

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
 * Append a message to the log file
 * @param {string} message - The message to log
 */
async function appendToLog(message) {
    try {
        await fsPromises.appendFile(LOG_FILE_PATH, message);
        console.log(`Log message written to ${LOG_FILE_PATH}`);
    } catch (err) {
        console.error(`Error writing to log file: ${err.message}`);
    }
}

/**
 * Schedule the next script execution
 */
function scheduleNextRun() {
    // Clear any existing timer
    if (scriptTimer) {
        clearTimeout(scriptTimer);
    }
    
    const now = Date.now();
    const nextRunTime = lastAccessTime ? lastAccessTime + getDelayDuration() : now;
    const delay = Math.max(nextRunTime - now, 0);
    
    console.log(`Next script run scheduled in ${(delay / (60 * 60 * 1000)).toFixed(2)} hours.`);
    
    scriptTimer = setTimeout(async () => {
        if (!scriptRunning) {
            lastAccessTime = Date.now();
            await runScript();
            scheduleNextRun(); // Schedule the next run after this one completes
        } else {
            // If script is already running, check again in a minute
            setTimeout(() => scheduleNextRun(), 60 * 1000);
        }
    }, delay);
}

/**
 * Execute the script and return its output
 * @returns {Promise<string>} The script output
 */

// TBD add res as an optional parameter and, if it exists, use it to stream the output to the client

async function runScript(res = null) {
    if (scriptRunning) {
        return "Script already running. Try again later.";
    }
    
    scriptRunning = true;
    
    try {
        // Check if script exists
        try {
            await fsPromises.access(SCRIPT_PATH, fs.constants.X_OK);
        } catch (err) {
            throw new Error(`Script not found or not executable: ${SCRIPT_PATH}`);
        }
        
        // Log the execution
        const currentDateTime = new Date().toISOString();
        await appendToLog(`Check for new episodes at ${currentDateTime}\n`);
        
        console.log('Executing script...');
        
        return new Promise((resolve, reject) => {
            // Try zsh first, fall back to bash if needed
          
            const process = spawn('zsh', [SCRIPT_PATH]);
            
            // Collect stdout
            process.stdout.on('data', (data) => {
                if (res)
                    res.write(data.toString());
                else
                    console.log(data.toString());

            });
            
            // Collect stderr
            process.stderr.on('data', (data) => {
                if (res)
                    res.write(data.toString());
                else
                    console.log(data.toString());
            });
            
            // Handle process exit
            process.on('close', (code) => {
                console.log(`Script exited with code ${code}`);
                scriptRunning = false;
                
                if (code === 0) {
                    resolve();
                } else {
                    reject(new Error(`Process failed with exit code ${code}. Error: ${errorOutput}`));
                }
            });
            
            // Handle errors in spawning the process
            process.on('error', (error) => {
                console.error(`Error spawning process: ${error.message}`);
                scriptRunning = false;
                reject(error);
            });
            
        });
    } catch (error) {
        scriptRunning = false;
        throw error;
    }
}

// Route to execute the script
app.get('/getnew', async (req, res) => {
    const currentDateTime = new Date().toISOString();
    console.log(`Received request to run the script at ${currentDateTime}.`);
    
    // Update the last access time
    lastAccessTime = Date.now();
    
    // Reset the schedule
    scheduleNextRun();
    
    try {
        // Execute the script
        await runScript(res);
        res.end(); // End the response if streaming
    } catch (error) {
        console.error(`Error running script: ${error.message}`);
        res.status(500).send(`Error: ${error.message}`);
    }
});

app.get('/log', async (req, res) => {
    try {
        const n = parseInt(req.query.lines) || LOGLINES; // Number of lines to send, default to 20
        
        const data = await fsPromises.readFile(LOG_FILE_PATH, 'utf8');
        const lines = data.split('\n').slice(-n).join('\n'); // Get the last n lines
        res.send(lines);
    } catch (err) {
        console.error(`Error reading log file: ${err.message}`);
        res.status(500).send('Error reading log file');
    }
});

// Start the server
app.listen(PORT, async () => {
    console.log(`Podcast update server running on http://localhost:${PORT}`);
    
    // Check if log file exists, create if not
    try {
        await fsPromises.access(LOG_FILE_PATH);
    } catch (err) {
        await fsPromises.writeFile(LOG_FILE_PATH, `Log created at ${new Date().toISOString()}\n`);
    }
    
    scheduleNextRun(); // Start the scheduling process
});
