const express = require('express');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = 3000;
const BASE_DIR = path.resolve('./content'); // Directory to browse

// Serve static files for the frontend
// app.use(express.static('./public'));
app.use(express.static(path.join(__dirname, 'content')));
// API to list files in a directory
app.get('/api/files', (req, res) => {
    fs.readdir(BASE_DIR, { withFileTypes: true }, (err, files) => {
        if (err) {
            return res.status(500).json({ error: 'Unable to read directory' });
        }

        const fileList = files.map((file) => ({
            name: file.name,
            isDirectory: file.isDirectory(),
        }));
        res.json(fileList);
    });
});

// API to get the selected file
app.get('/api/file/:name', (req, res) => {
    const fileName = req.params.name;
    const filePath = path.join(BASE_DIR, fileName);

    if (!fs.existsSync(filePath) || fs.statSync(filePath).isDirectory()) {
        return res.status(400).json({ error: 'Invalid file selection' });
    }

    res.sendFile(filePath);
});

app.listen(PORT, () => {
    console.log(`Server is running at http://localhost:${PORT}`);
});