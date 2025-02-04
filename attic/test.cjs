const fs = require('fs');
const jsdom = require('jsdom');
const { JSDOM } = jsdom;

// Load the HTML file

const fname = "/Volumes/ex0/repos/transpod/content/teppeinoriko/transcripts/0002_朝ごはんについて！.html"
fs.readFile(fname, 'utf8', (err, html) => {
    if (err) {
        console.error('Error reading file:', err);
        return;
    }
    
    // Parse the HTML
    const dom = new JSDOM(html);
    const document = dom.window.document;
    
    // Extract subtitles
    const subtitles = [];
    document.querySelectorAll('div').forEach(div => {
        const timestamp = div.querySelector('.timestamp');
        const textElement = div.querySelector('.subtitle-text');
        
        if (timestamp && textElement) {
            const start = parseTimestamp(timestamp.getAttribute('data-subbegin'));
            const end = parseTimestamp(timestamp.getAttribute('data-subend'));
            const text = textElement.textContent.trim();
            
            subtitles.push({ start, end, text });
        }
    });
    
    // Save as JSON
    fs.writeFile('output.json', JSON.stringify(subtitles, null, 4), (err) => {
        if (err) {
            console.error('Error writing JSON:', err);
        } else {
            console.log('Conversion completed. Saved as output.json');
        }
    });
});

// Convert timestamp format "HH:MM:SS,MS" to seconds
function parseTimestamp(timestamp) {
    if (!timestamp) return 0;
    const parts = timestamp.split(/[:,]/);
    const hours = parseInt(parts[0], 10) || 0;
    const minutes = parseInt(parts[1], 10) || 0;
    const seconds = parseInt(parts[2], 10) || 0;
    const milliseconds = parseInt(parts[3], 10) || 0;
    return hours * 3600 + minutes * 60 + seconds + milliseconds / 1000;
}
