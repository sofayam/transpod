var express = require('express')
var fs = require('fs')
var path = require("path")
var jsdom = require("jsdom")
const { JSDOM } = jsdom
const http = require('http');
const sqlite3 = require('sqlite3').verbose();

var app = express()

var PORT = 8014
var orderList = null
var feedOrderDict = null

const mini = "192.168.68.101"

const LOG_SERVER_URL = 'http://' + mini + ':8015/log';
const GETNEW_SERVER_URL = 'http://' + mini + ':8015/getnew';

if (process.argv.length > 2) {
    PORT = parseInt(process.argv[2])
}

BADFILES = [".gitignore", ".DS_Store", "ReadMe.md"]
console = require("console"),
    error = console.error
//handlebars = require('express-handlebars'),
path = require('path');

const exphbs = require('express-handlebars');
const { getDefaultAutoSelectFamilyAttemptTimeout } = require('net')
const { default: e } = require('express')
const { info } = require('console')
const { finished } = require('stream')
const hbs = exphbs.create({
    extname: 'hbs',
    helpers: {
        gt: (a, b) => a > b,
        eq: (a, b) => a === b,
        formatTimestamp: (totalSeconds) => {
            const minutes = Math.floor(totalSeconds / 60);
            const seconds = Math.floor(totalSeconds % 60);
            return `${minutes}:${String(seconds).padStart(2, '0')}`;
        }
    }
});
app.engine('hbs', hbs.engine);
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'hbs');

app.use((req, res, next) => {
    req.on('aborted', () => {
        console.log('Request aborted by client');
    });
    next();
});
app.use(express.json())
app.use(express.urlencoded({ extended: true }))

function getPods(forceAll = false, language = 'all') {

    let coresetOnly = readMetaGlobal().coresetOnly === "true"
    if (forceAll) {
        coresetOnly = false
    }
    let isCore = function (pod) {
        if (coresetOnly) {
            // get path to meta file
            let metaPath = path.join(__dirname, "content", pod + ".meta")
            let meta = readMetaPod(pod)
            return meta.coreset === "true"
        } else {
            return true
        }
    }

    let podPath = path.join(__dirname, "content")
    let contents = fs.readdirSync(podPath, { withFileTypes: true })
        .filter(dirent => dirent.isDirectory())
        // ignore @eaDir directories
        .filter(dirent => !dirent.name.startsWith('@eaDir'))
        .filter(pod => isCore(pod.name))
        .map(dirent => dirent.name)

    if (language && language !== 'all') {
        contents = contents.filter(pod => {
            const config = readConfig(pod);
            const lang = config.lang || 'ja'; // Default to 'ja' if not specified
            return lang === language;
        });
    }

    return contents
}

app.get("/manifest.json", (req, res) => {
    res.type('application/manifest+json');
    res.sendFile(__dirname + '/manifest.json');
});

const getLanguages = () => {
    const contentPath = path.join(__dirname, "content");
    const podDirs = fs.readdirSync(contentPath, { withFileTypes: true })
        .filter(dirent => dirent.isDirectory())
        .map(dirent => dirent.name);

    const languages = new Set(['ja']);
    podDirs.forEach(podDir => {
        const configPath = path.join(contentPath, podDir, "_config.md");
        if (fs.existsSync(configPath)) {
            try {
                const config = JSON.parse(fs.readFileSync(configPath, 'utf-8'));
                if (config.lang) {
                    languages.add(config.lang);
                }
            } catch (error) {
                console.error(`Error reading or parsing ${configPath}:`, error);
            }
        }
    });
    return Array.from(languages).sort();
};

app.get("/", (req, res, next) => {
    const metaGlobal = readMetaGlobal();
    const selectedLanguage = metaGlobal.language || 'all';
    let contents = getPods(false, selectedLanguage)
    let pcData = []
    contents.forEach(file => {
        // console.log(file)
        let meta = readMetaPod(file)
        podEntry = { name: file, ...meta }
        pcData.push(podEntry)
    })
    const languages = getLanguages();
    res.render("podcasts", { pods: pcData, layout: false, coresetOnly: metaGlobal.coresetOnly, languages, selectedLanguage })
})

function compareEpisode(ep1, ep2) {

    // TBD include various sorting criteria here based on data in _config.md
    i1 = getIndex(ep1.displayname)
    i2 = getIndex(ep2.displayname)
    return i1.index.localeCompare(i2.index)

}

function readConfig(podName) {
    const configPath = path.join(__dirname, "content", podName, "_config.md");
    if (fs.existsSync(configPath)) {
        returnVal = JSON.parse(fs.readFileSync(configPath, 'utf-8'));
        return returnVal
    }
    return {}
}

function hasSortInfo(podName) {
    let meta = readConfig(podName)
    if (meta.sortInfo) {
        return true
    }
    return false
}

app.get("/pod/:id", (req, res, next) => {
    let podName = req.params.id
    let epPath = path.join(__dirname, "content", podName)
    // console.log("epPath ", epPath) 
    let contents = fs.readdirSync(epPath)
    let epData = []
    // find no of chunks for each file
    let sortonpubdate = false

    sortonpubdate = hasSortInfo(podName)

    const config = readConfig(podName);
    const lang = config.lang || 'ja';

    contents.forEach(file => {
        // console.log(file)
        if (!(BADFILES.includes(file)))
            if (file.substring(file.length - 4) === ".mp3") {
                // filter out all the chunks from the main list
                fname = file.substring(0, file.length - 4)
                // get the info file
                let info = {}
                let infopath = path.join(epPath, fname + ".info")
                if (fs.existsSync(infopath)) {
                    info = JSON.parse(fs.readFileSync(infopath, 'utf-8'))
                }
                epData.push({
                    podName, displayname: fname, encoded: encodeURIComponent(fname),
                    finished: !(isUnfinished(podName, fname)), info, language: lang
                })

            }
    })

    const meta = readMetaPod(podName)
    // if we only want unfinished
    if (meta.show === "unfinished") {
        epData = epData.filter((item) => isUnfinished(podName, item.displayname))
    }
    // throw out the finished episodes 

    // sort episodes
    if (sortonpubdate) {
        epData = epData.filter((item) => item.info.published_parsed) // mysterious bug on noriko sorting solved by this
        epData.sort((a, b) => comparePublishedParsed(a.info.published_parsed, b.info.published_parsed))
    } else {
        epData.sort(compareEpisode)
    }

    // reverse order if dropdown set to latest

    if (meta.order === "latest") {
        epData.reverse()
    }

    orderList = epData

    res.render("episodes", { eps: epData, pod: podName, meta, layout: false })
})


function isUnfinished(podName, epName) {
    // console.log("isUnfinished", podName, epName)

    meta = readMetaEp(podName, epName)
    return !meta.finished

}

function getNextep(ep) {
    if (!orderList || orderList.length === 0) {
        return ""; // No episodes available
    }

    // Find the index of the current episode
    const currentIndex = orderList.findIndex(item => item.displayname === ep);

    if (currentIndex === -1) {
        return ""; // Episode not found
    }

    // Determine the next episode based on the sorting order
    const meta = readMetaPod(orderList[0].podName); // Assuming all episodes belong to the same podcast
    const isLatestFirst = meta && meta.order === "latest";

    if (isLatestFirst) {
        // If sorted latest first, the "next" episode is the previous one in the list
        return currentIndex > 0 ? orderList[currentIndex - 1].displayname : "";
    } else {
        // If sorted oldest first, the "next" episode is the next one in the list
        return currentIndex < orderList.length - 1 ? orderList[currentIndex + 1].displayname : "";
    }
}

app.get("/play/:pod/:ep", (req, res, next) => {
    let pod = req.params.pod
    let ep = req.params.ep
    let startTime = req.query.t || null;

    let epPath = path.join(__dirname, "content", pod, ep)
    mp3name = "/" + pod + "/" + encodeURIComponent(ep) + ".mp3"
    meta = readMetaEp(pod, ep)

    if (startTime === null) {
        startTime = meta.timeInPod || 0;
    }

    transcript = getTranscript(pod, ep)
    transcripttext = transcript.text
    transcriptsrc = transcript.src
    nextep = encodeURIComponent(getNextep(ep))
    let infopath = epPath + ".info"
    let info = {}
    if (fs.existsSync(infopath)) {
        info = JSON.parse(fs.readFileSync(infopath, 'utf-8'))
    }
    info.language = readConfig(pod).lang || 'ja';
    const config = readConfig(pod);
    info.language = config.lang || 'ja';

    res.render("playtranspwa", {
        pod, mp3file: mp3name,
        transcript: transcripttext,
        source: transcriptsrc, meta, nextep,
        info,
        startTime,
        layout: false
    })

})

function comparePublishedParsed(a, b) {
    if (!a || !b) {
        return 0
    }
    for (let i = 0; i < a.length; i++) {
        if (a[i] !== b[i]) {
            return a[i] - b[i];
        }
    }
    return 0;
}

app.get("/recentPublish", (req, res) => {

    // Get all podcast info, sort on published_parsed field
    let podPath = path.join(__dirname, "content")

    let contents = getPods()
    // for each podcast
    let epList = []
    contents.forEach(podName => {

        if (!(BADFILES.includes(podName))) {
            let ppath = path.join(podPath, podName)

            let eps = fs.readdirSync(ppath, { withFileTypes: true })
                .filter(dirent => dirent.isFile() && dirent.name.endsWith('.info'))
                .map(dirent => dirent.name);
            eps.forEach(ep => {

                let infopath = path.join(ppath, ep)

                let info = JSON.parse(fs.readFileSync(infopath, 'utf-8'))
                if (info.published_parsed) {

                    let barename = ep.slice(0, -5)

                    let epentry = { pod: podName, name: barename, encoded: encodeURIComponent(barename), info, finished: !(isUnfinished(podName, barename)) }
                    epList.push(epentry)
                }
            })
        }
    })


    // Sort the data array based on the published_parsed field
    epList.sort((a, b) => comparePublishedParsed(b.info.published_parsed, a.info.published_parsed))

    // take the first 100
    epList = epList.slice(0, 100)

    res.render("recentPublish", { epList, layout: false })
})

function parseTimeToSeconds(time) {
    // Remove the leading colon if present
    const cleanTime = time.startsWith(':') ? time.substring(1) : time;

    // Split the time string into parts
    const parts = cleanTime.split(':').map(Number);

    // Handle different formats
    var totalseconds = 0;
    if (parts.length === 3) {
        // Format is HH:mm:ss
        const [hours, minutes, seconds] = parts;
        totalseconds = (hours * 3600) + (minutes * 60) + seconds;
    } else if (parts.length === 2) {
        // Format is mm:ss
        const [minutes, seconds] = parts;
        totalseconds = (minutes * 60) + seconds;
    }
    return totalseconds
}

function formatSeconds(totalSeconds) {

    const hours = Math.floor(totalSeconds / 3600);
    const minutes = Math.floor((totalSeconds % 3600) / 60);
    const seconds = totalSeconds % 60;

    // Format with leading zeros and return with leading colon
    return `${hours}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
}

function addTimes(times) {
    // Initialize total seconds
    let totalSeconds = 0;

    // Process each time string
    times.forEach(time =>
        totalSeconds += parseTimeToSeconds(time)
    );

    // Convert total seconds back to HH:mm:ss format
    return formatSeconds(totalSeconds)
}


function listenData() {

    // Get all podcast metadata, sort on timeLastOpened field, filter for unfinished
    let podPath = path.join(__dirname, "content")

    let contents = getPods(forceAll = true)
    // for each podcast
    let epList = []
    contents.forEach(podName => {

        if (!(BADFILES.includes(podName))) {
            let ppath = path.join(podPath, podName)

            let eps = fs.readdirSync(ppath, { withFileTypes: true })
                .filter(dirent => dirent.isFile() && dirent.name.endsWith('.meta'))
                .map(dirent => dirent.name);
            eps.forEach(ep => {

                let metapath = path.join(ppath, ep)

                // get info file TODO
                let infopath = path.join(ppath, ep.slice(0, -5) + ".info")

                let meta = JSON.parse(fs.readFileSync(metapath, 'utf-8'))

                let info = {}
                if (fs.existsSync(infopath)) {
                    info = JSON.parse(fs.readFileSync(infopath, 'utf-8'))
                }

                let barename = ep.slice(0, -5)
                let epentry = { pod: podName, name: barename, encoded: encodeURIComponent(barename), meta, info, finished: !(isUnfinished(podName, barename)) }
                epList.push(epentry)
            })
        }
    })
    let times = []
    epList.forEach(ep => {
        if (ep.meta.finished) {
            if (ep.info) {
                //  check if itunes_duration is present and is of type string
                if (ep.info.itunes_duration && typeof ep.info.itunes_duration === 'string') {
                    times.push(ep.info.itunes_duration)
                }
            }
        }
    })

    return { epList, times }

}

app.get("/seltest", (req, res) => {
    res.render("seltest", { layout: false })
})


app.get("/geticon", (req, res) => { 
    const podName = req.query.pod;
    const iconPath = path.join(__dirname, "content", podName, "icon.jpg-64x64.jpg");
    if (fs.existsSync(iconPath)) {
        res.type('image/jpeg');
        res.sendFile(iconPath);
    } else {
        // Send the default podcast icon
        const defaultIconPath = path.join(__dirname, "content", "default.svg");
        if (fs.existsSync(defaultIconPath)) {
            res.type('image/svg+xml');
            res.sendFile(defaultIconPath);
        } else {
            res.status(404).send("Icon not found");
        }
    }
})
        


app.get("/getNew", (req, res) => {
    const currentDateTime = new Date().toISOString(); // Get the current date and time
    console.log(`[${currentDateTime}] Proxying request to getnewserver...`);

    // Forward the request to the getnewserver
    const request = http.get(GETNEW_SERVER_URL, (getnewRes) => {
        // Set the response headers
        res.setHeader('Content-Type', 'text/plain');

        // Stream the response from getnewserver to the browser
        getnewRes.on('data', (chunk) => {
            // console.log(`Streaming chunk: ${chunk}`);
            res.write(chunk);
        });

        // End the response when the getnewserver finishes
        getnewRes.on('end', () => {
            const currentDateTime = new Date().toISOString(); // Get the current date and time
            console.log(`[${currentDateTime}] Finished streaming from getnewserver...`);
            res.end();
        });

        // Handle errors from getnewserver
        getnewRes.on('error', (err) => {
            console.error(`Error from getnewserver: ${err.message}`);
            res.status(500).end(`Error: ${err.message}`);
        });
    }).on('error', (err) => {
        console.error(`Error connecting to getnewserver: ${err.message}`);
        res.status(500).end(`Error: ${err.message}`);
    });
/*     request.setTimeout(10000, () => { // Timeout after 10 seconds
        console.error('Request timed out.');
        res.status(500).end('Error: Request timed out.');
        request.abort(); // Abort the request
    }); */

})

app.get("/showGetNew", (req, res) => {

    // get the log from the getnewserver by calling the log endpoint
   
    console.log('Proxying request to getnewserver...');     
    // Forward the request to the getnewserver
    try {
    const request = http.get(LOG_SERVER_URL, (getnewRes) => {
        // get the log text into a string
        let logText = '';
        getnewRes.on('data', (chunk) => {
            logText += chunk;
        });
        // End the response when the getnewserver finishes
        getnewRes.on('end', () => {
            console.log('Finished streaming from getnewserver.');
            const logLines = logText.split('\n').filter(line => line.trim() !== '');
            // reverse the order of the log lines
            logLines.reverse();
            res.render("getNew", { logLines, layout: false })
        });
        // Handle errors from getnewserver
        getnewRes.on('error', (err) => {
            console.error(`Error from getnewserver: ${err.message}`);
            res.render("sulkingServer", { message: err.message, layout: false })
        }); 
    }).on('error', (err) => {
        console.error(`Error connecting to getnewserver: ${err.message}`);
        res.render("sulkingServer", { message: err.message,  layout: false })
        // res.status(500).end(`Error: ${err.message}`);
    });

    request.setTimeout(10000, () => { // Timeout after 10 seconds
        console.error('Request timed out.');
        // res.status(500).end('Error: Request timed out.');
        res.render("sulkingServer", {message : "Timed Out",  layout: false })
        request.abort(); // Abort the request
    });

} catch (err) {
    // Catch any unexpected errors and render the sulkingServer page
    console.error(`Unexpected error: ${err.message}`);
    res.render("sulkingServer", { message: err.message, layout: false });
} 



})

app.get("/recentListen", (req, res) => {

    let { epList, times } = listenData();

    let totalTime = addTimes(times)


    epList = epList.filter(ep => ep.meta.timeLastOpened !== 0)
    epList.sort((a, b) => b.meta.timeLastOpened.localeCompare(a.meta.timeLastOpened))

    // take the first 100
    epList = epList.slice(0, 100)

    res.render("recentListen", { epList, totalTime, layout: false })
})

app.get("/concordances", (req, res) => {
    const concordancesPath = path.join(__dirname, "public", "concordances");
    fs.readdir(concordancesPath, (err, files) => {
        if (err) {
            console.error("Error reading concordances directory:", err);
            return res.status(500).send("Error loading concordances.");
        }
        const htmlFiles = files.filter(file => file.endsWith(".html"));
        res.render("concordances", { files: htmlFiles, layout: false });
    });
});

function readMetaEp(pod, ep) {
    const metaPath = path.join(__dirname, "content", pod, ep + ".meta")
    if (fs.existsSync(metaPath)) {
        try {
            return JSON.parse(fs.readFileSync(metaPath, 'utf-8'));
        } catch (error) {
            console.error(`Error reading ${metaPath}:`, error);
        }
    }
    return { finished: false, timeLastOpened: 0, timeInPod: 0 }; // Default values
}


function readMetaPod(folderName) {
    const metaPath = path.join(__dirname, "content", `${folderName}.meta`);
    if (fs.existsSync(metaPath)) {
        try {
            returnVal = JSON.parse(fs.readFileSync(metaPath, 'utf-8'));
            if (!returnVal.coreset) {
                returnVal.coreset = "false"
            }
            return returnVal
        } catch (error) {
            console.error(`Error reading ${metaPath}:`, error);
        }
    }
    return { order: "latest", show: "all", coreset: "false" }; // Default values
}

function readMetaGlobal() {
    const metaPath = path.join(__dirname, "content/_global.meta");
    if (fs.existsSync(metaPath)) {
        try {
            return JSON.parse(fs.readFileSync(metaPath, 'utf-8'));
        } catch (error) {
            console.error(`Error reading ${metaPath}:`, error);
        }
    }
    return { coresetOnly: "true" }; // Default values
}

function writeMetaEp(metaPath, finished, timeLastOpened, timeInPod) {
    const metaData = { finished, timeLastOpened, timeInPod }
    fs.writeFileSync(metaPath, JSON.stringify(metaData, null, 4), 'utf-8')
    console.log(`Updated meta ep file: ${metaPath}`);
}


function writeMetaPod(folderName, order, show, coreset) {
    const metaPath = path.join(__dirname, "content", `${folderName}.meta`);
    const metaData = { order, show, coreset };

    try {
        fs.writeFileSync(metaPath, JSON.stringify(metaData, null, 4), 'utf-8');
        console.log(`Updated meta pod file: ${metaPath}`);
    } catch (error) {
        console.error(`Error writing ${metaPath}:`, error);
    }
}

function writeMetaGlobal(coresetOnly, language) {
    const metaPath = path.join(__dirname, "content/_global.meta");
    const metaData = readMetaGlobal();

    if (coresetOnly !== undefined) {
        metaData.coresetOnly = coresetOnly;
    }
    if (language !== undefined) {
        metaData.language = language;
    }

    try {
        fs.writeFileSync(metaPath, JSON.stringify(metaData, null, 4), 'utf-8');
        console.log(`Updated global meta file: ${metaPath}`);
    } catch (error) {
        console.error(`Error writing ${metaPath}:`, error);
    }
}


app.post('/update-meta-ep', (req, res) => {

    const { name, finished, timeLastOpened, timeInPod } = req.body;
    // TBD cut off mp3 and change to meta
    // TBD maybe some URL ding needed here
    const deconame = decodeURIComponent(name)
    const podcastpath = deconame.slice(0, -4)
    const metapath = path.join(__dirname, "content", podcastpath + ".meta")
    try {
        writeMetaEp(metapath, finished, timeLastOpened, timeInPod)

        res.json({ success: true });
    } catch (error) {
        console.error(`Error writing ${metapath}`, error)
        res.status(400).json({ success: false, message: "Invalid Episode" });
    }

});

app.post('/update-meta-pod', (req, res) => {

    const { name, order, show, coreset } = req.body;
    const folderPath = path.join(__dirname, "content", name);

    if (fs.existsSync(folderPath) && fs.statSync(folderPath).isDirectory()) {
        writeMetaPod(name, order, show, coreset);
        res.json({ success: true });
    } else {
        res.status(400).json({ success: false, message: "Invalid Podcast" });
    }
});

app.post('/update-meta-global', (req, res) => {

    const { coresetOnly, language } = req.body;
    try {
        writeMetaGlobal(coresetOnly, language);
        res.json({ success: true });
    } catch (error) {
        res.status(400).json({ success: false, message: "Error storing global metadata" });
    }
});



app.use(express.static("public"))
app.use(express.static("content"))

app.listen(PORT, () =>
    console.log(`Listening on port ${PORT}`)
)

function findFileInDirectory(directory, searchString) {
    try {
        const files = fs.readdirSync(directory); // Read all files in the directory
        // find only the files that start with the search string

        const matchingFiles = files.filter(file => file.startsWith(searchString))

        // const matchingFiles = files.filter(file => file.includes(searchString));

        if (matchingFiles.length > 0) {

            return matchingFiles
        } else {
            console.error("No matching files found ",  directory, " for search string: ", searchString);
        }
    } catch (error) {
        console.error("Error reading directory:", error);
    }
    return []
}

function getIndex(title) {
    const match = title.match(/#(\d+)/)
    if (match) {
        const paddedNumber = match[1].padStart(4, '0');
        return { match: true, index: paddedNumber }
    }
    else
        return { match: false, index: title }
}

const getTranscript = (pod, ep) => {


     let source = "whisper"
        transcriptfile = path.join(__dirname, "content", pod, ep + ".json")
        try {
            transcripttext = fs.readFileSync(transcriptfile, 'utf-8')
        } catch (error) {
            console.log("no transcript found, defaulting to polite apology")
            transcripttext = '[{ "start": 0.0, "end": 10000.0, "text": "申し訳ありませんが、このエピソードのトランスクリプトはまだ利用できません。"}]'
        }

    return { src: source, text: transcripttext }
}


const transhtml = (fname) => {
    const html = fs.readFileSync(fname, 'utf8');

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
    return JSON.stringify(subtitles, null, 4)

}



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

// Initialize SQLite database
const db = new sqlite3.Database(path.join(__dirname, 'content', 'TIMEDATA.db'), (err) => {
    if (err) {
        console.error('Error opening database:', err.message);
    } else {
        console.log('Connected to SQLite database.');
        db.run(`
            CREATE TABLE IF NOT EXISTS podcast_time (
                date TEXT NOT NULL,
                podcast_name TEXT NOT NULL,
                episode_name TEXT NOT NULL,
                total_seconds INTEGER NOT NULL,
                language TEXT NOT NULL DEFAULT 'ja',
                PRIMARY KEY (date, podcast_name, episode_name)
            )
        `, (err) => {
            if (err) {
                console.error('Error creating table:', err.message);
            }
        });
        db.run(`ALTER TABLE podcast_time ADD COLUMN language TEXT DEFAULT 'ja'`, (err) => {
            if (err) {
                // ignore error if column already exists
                if (err.message.includes('duplicate column name')) {
                    return;
                }
                console.error('Error adding language column:', err.message);
            }
        });
    }
});

app.get('/initdbfrommeta', (req, res) => {

    // Probably not needed anymore (says the vibe code robot that wrote this)


    // initialize historical values in the database from the meta files
    // using the values collected for the chart
    let { epList, times } = listenData();

    let listenDays = {}
    let totpod = 0
    let totseconds = 0

    epList.forEach(ep => {
        if (ep.meta.finished && ep.meta.timeLastOpened) {

            if (ep.info) {
                if (ep.info.itunes_duration && typeof ep.info.itunes_duration === 'string') {
                    // get time of ep
                    // {date: "2025-03-01", count: 2, totalMinutes: 70},
                    let time = ep.info.itunes_duration
                    let seconds = parseTimeToSeconds(time)
                    let date = ep.meta.timeLastOpened.substring(0, 10)
                    const config = readConfig(ep.pod);
                    const lang = config.lang || 'ja';

                    // create the db record
                    const query = `
                        INSERT INTO podcast_time (date, podcast_name, episode_name, total_seconds, language)
                        VALUES (?, ?, ?, ?, ?)
                        ON CONFLICT(date, podcast_name, episode_name)
                        DO UPDATE SET total_seconds = total_seconds + excluded.total_seconds
                    `;
                    db.run(query, [date, ep.pod, ep.name, seconds, lang], function (err) {
                        if (err) {
                            console.error('Error inserting into database:', err.message);
                        } else {
                            console.log(`Inserted/Updated record for ${ep.pod} - ${ep.name} on ${date}`);
                        }
                    });
                               
                }
            }
        }
    })
})

function extractFileNameWithoutExtension(path) {
    // Split the path by '/' and get the last part (filename with extension)
    const filenameWithExtension = path.split('/').pop();
    
    // Split the filename by '.' and get the part before the extension
    const filenameWithoutExtension = filenameWithExtension.split('.')[0];
    
    return filenameWithoutExtension;
  }

app.get('/update-time', (req, res) => {
    const { date, podcastName, episodeName, seconds, language } = req.query;

    if (!date || !podcastName || !episodeName || !seconds) {
        return res.status(400).json({ success: false, message: 'Missing required parameters.' });
    }

    const query = `
        INSERT INTO podcast_time (date, podcast_name, episode_name, total_seconds, language)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(date, podcast_name, episode_name)
        DO UPDATE SET total_seconds = total_seconds + excluded.total_seconds
    `;

    // decode the episode name
    const decodedEpisodeName = decodeURIComponent(episodeName);
    const episodeNameWithoutExtension = extractFileNameWithoutExtension(decodedEpisodeName);
    let lang = language;
    if (!lang) {
        const config = readConfig(podcastName);
        lang = config.lang || 'ja';
    }

    db.run(query, [date, podcastName, episodeNameWithoutExtension, parseInt(seconds), lang], function (err) {
        if (err) {
            console.error('Error updating database:', err.message);
            return res.status(500).json({ success: false, message: 'Database error.' });
        }

        res.json({ success: true, message: 'Time updated successfully.' });
    });
});

app.get("/chartFromDB", (req, res) => {
    const selectedLanguage = req.query.language;

    let query = `
        SELECT date, language, SUM(total_seconds) AS totalSeconds
        FROM podcast_time
    `;
    const params = [];

    if (selectedLanguage && selectedLanguage !== 'all') {
        query += ' WHERE language = ?';
        params.push(selectedLanguage);
    }

    query += `
        GROUP BY date, language
        ORDER BY date ASC
    `;

    db.all(query, params, (err, rows) => {
        if (err) {
            console.error('Error querying database:', err.message);
            return res.status(500).send('Database error.');
        }

        db.all('SELECT DISTINCT language FROM podcast_time', [], (langErr, langs) => {
            if (langErr) {
                console.error('Error querying languages:', langErr.message);
                return res.status(500).send('Database error.');
            }

            db.get('SELECT MIN(date) as minDate, MAX(date) as maxDate FROM podcast_time', [], (dateErr, dateRange) => {
                if (dateErr) {
                    console.error('Error querying date range:', dateErr.message);
                    return res.status(500).send('Database error.');
                }

                if (rows.length === 0) {
                    return res.render("chart", { listenList: '[]', tottime: '0:00:00', languages: langs, selectedLanguage, layout: false });
                }

                const dataByDate = {};
                rows.forEach(row => {
                    if (!dataByDate[row.date]) {
                        dataByDate[row.date] = {
                            date: row.date,
                            totalMinutes: 0,
                            languages: {}
                        };
                    }
                    dataByDate[row.date].languages[row.language] = row.totalSeconds / 60;
                    dataByDate[row.date].totalMinutes += row.totalSeconds / 60;
                });

                const listenList = [];
                if (dateRange.minDate && dateRange.maxDate) {
                    const startDate = new Date(dateRange.minDate);
                    const endDate = new Date(dateRange.maxDate);
                    endDate.setDate(endDate.getDate() + 1);
                    
                    for (let d = new Date(startDate); d < endDate; d.setDate(d.getDate() + 1)) {
                        const dateString = d.toISOString().split('T')[0];
                        if (dataByDate[dateString]) {
                            listenList.push(dataByDate[dateString]);
                        } else {
                            listenList.push({
                                date: dateString,
                                totalMinutes: 0,
                                languages: {}
                            });
                        }
                    }
                }

                const totseconds = rows.reduce((sum, row) => sum + row.totalSeconds, 0);
                const tottime = formatSeconds(totseconds);

                res.render("chart", { listenList: JSON.stringify(listenList), tottime, languages: langs, selectedLanguage, layout: false });
            });
        });
    });
});

app.get("/debug-db", (req, res) => {
    db.all("SELECT * FROM podcast_time ORDER BY date DESC", [], (err, rows) => {
        if (err) {
            res.status(500).json({ "error": err.message });
            return;
        }
        res.json(rows);
    });
});

// Initialize concordance SQLite database
const concordanceDb = new sqlite3.Database(path.join(__dirname, 'content/concordance.db'), (err) => {
    if (err) {
        console.error('Error opening concordance database:', err.message);
    } else {
        console.log('Connected to concordance database.');
    }
});

app.get("/autocomplete", (req, res) => {
    const query = req.query.q;
    if (!query) {
        return res.json([]);
    }

    const sql = `
        SELECT word 
        FROM words 
        WHERE word LIKE ? 
        ORDER BY length(word)
        LIMIT 10
    `;
    const searchTerm = query + '%';

    concordanceDb.all(sql, [searchTerm], (err, rows) => {
        if (err) {
            console.error('Error querying concordance database:', err.message);
            return res.status(500).send("Error performing search.");
        }
        res.json(rows.map(row => row.word));
    });
});

app.get("/searchword", (req, res) => {
    res.render("searchword", { layout: false, query: "", results: null });
});

app.post("/searchword", (req, res) => {
    const queryWord = req.body.word;

    if (!queryWord) {
        return res.render("searchword", { layout: false, query: "", results: null, message: "Please enter a word to search." });
    }

    const sql = `
        SELECT
            p.name AS podcast_name,
            e.name AS episode_name,
            s.start_time,
            s.end_time,
            s.text AS segment_text
        FROM
            words w
        JOIN
            entries en ON w.id = en.word_id
        JOIN
            segments s ON en.segment_id = s.id
        JOIN
            episodes e ON s.episode_id = e.id
        JOIN
            podcasts p ON e.podcast_id = p.id
        WHERE
            w.word = ? COLLATE NOCASE;
    `;

    concordanceDb.all(sql, [queryWord], (err, rows) => {
        if (err) {
            console.error('Error querying concordance database:', err.message);
            return res.status(500).send("Error performing search.");
        }

        const groupedResults = {};
        rows.forEach(row => {
            if (!groupedResults[row.podcast_name]) {
                groupedResults[row.podcast_name] = {
                    podcastName: row.podcast_name,
                    episodes: {}
                };
            }
            if (!groupedResults[row.podcast_name].episodes[row.episode_name]) {
                groupedResults[row.podcast_name].episodes[row.episode_name] = {
                    episodeName: row.episode_name,
                    segments: []
                };
            }
            // Highlight the search word in the segment text
            const highlightedText = row.segment_text.replace(new RegExp(queryWord, 'gi'), (match) => `<mark>${match}</mark>`);
            groupedResults[row.podcast_name].episodes[row.episode_name].segments.push({
                start: row.start_time,
                end: row.end_time,
                text: highlightedText
            });
        });

        // Convert groupedResults object to an array for Handlebars iteration
        const resultsArray = Object.values(groupedResults).map(podcast => {
            const podName = podcast.podcastName;
            const meta = readMetaPod(podName);

            podcast.episodes = Object.values(podcast.episodes).map(episode => {
                // Read episode info for sorting
                let info = {};
                const infoPath = path.join(__dirname, "content", podName, episode.episodeName + ".info");
                if (fs.existsSync(infoPath)) {
                    try {
                        info = JSON.parse(fs.readFileSync(infoPath, 'utf-8'));
                    } catch (e) {
                        console.error(`Error reading info file for ${podName}/${episode.episodeName}:`, e);
                    }
                }
                episode.info = info; // Attach info for sorting
                episode.displayname = episode.episodeName; // Add displayname for compareEpisode

                episode.segments = episode.segments.map(segment => {
                    const encodedEpisodeName = encodeURIComponent(episode.episodeName);
                    segment.playUrl = `/play/${podName}/${encodedEpisodeName}?t=${segment.start}&from=search`;
                    return segment;
                });
                return episode;
            });

            // Apply sorting logic: always oldest first
            const episodesWithPublishedParsed = podcast.episodes.filter(item => item.info && item.info.published_parsed);
            const episodesWithoutPublishedParsed = podcast.episodes.filter(item => !(item.info && item.info.published_parsed));

            // Sort episodes with published_parsed
            episodesWithPublishedParsed.sort((a, b) => comparePublishedParsed(a.info.published_parsed, b.info.published_parsed));

            // Sort episodes without published_parsed using compareEpisode
            episodesWithoutPublishedParsed.sort((a, b) => compareEpisode(a, b));

            // Concatenate them, putting those with published_parsed first
            podcast.episodes = episodesWithPublishedParsed.concat(episodesWithoutPublishedParsed);

            return podcast;
        });

        res.render("searchword", { layout: false, query: queryWord, results: resultsArray });
    });
});

app.get("/transformhtmltranscriptstojson", (req, res) => {
    // Transform all html transcripts in for a given podcast into json files
    const podcastName = req.query.podcast;
    // convert name to directory in content folder
    const podcastPath = path.join(__dirname, "content", podcastName);
    const transcriptDir = path.join(podcastPath, "transcripts");
    if (!fs.existsSync(transcriptDir)) {
        return res.status(404).send("Transcript directory not found.");
    }
    // first find all the ".mp3" files in the podcast folder
    const mp3Files = fs.readdirSync(podcastPath).filter(file => file.endsWith('.mp3'))

    for (const mp3File of mp3Files) {
        // if it is missing a corresponding .json file then create one based on the html transcript with a corresponding name
        const baseName = mp3File.slice(0, -4); // Remove the .mp3 extension
        const jsonFilePath = path.join(podcastPath, baseName + ".json");
        if (!fs.existsSync(jsonFilePath)) {
            // Check if the corresponding HTML transcript exists
            // using the numerical id encoded in the mp3 file name
            // using the algorithm also used in getTranscript
            const { match, index } = getIndex(baseName);
            let paddedNumber = "";
            if (match) {
                paddedNumber = index.padStart(4, '0'); // Ensure it is 4 digits
            }
            // find the htmlfile in the transcripts folder, it start with paddedNumber but you have to 
            // find the exact file by searching for paddedNumber in the transcript folder
            const htmlFiles = findFileInDirectory(transcriptDir, paddedNumber);
            if (htmlFiles.length === 1) {
                // We found exactly one HTML file that matches the padded number
                const htmlFilePath = path.join(transcriptDir, htmlFiles[0]);
                // Convert HTML transcript to JSON
                const jsonContent = transhtml(htmlFilePath);
                // Write the JSON content to the corresponding .json file
                fs.writeFileSync(jsonFilePath, jsonContent, 'utf-8');
                console.log(`Converted ${htmlFilePath} to ${jsonFilePath}`);
            } else {
                console.warn(`No HTML transcript found for ${baseName}, skipping.`);
            }
        } else {
            console.log(`JSON file already exists for ${baseName}, skipping.`);
        }
    }
    res.send("HTML transcripts converted to JSON where applicable.");
})


app.get("/legacyChartForSentimentalReasonsOnlyDoNotCallThis", (req, res) => {
    let { epList, times } = listenData();

    let listenDays = {}
    let totpod = 0
    let totseconds = 0

    epList.forEach(ep => {
        if (ep.meta.finished && ep.meta.timeLastOpened) {
            if (ep.info) {
                if (ep.info.itunes_duration && typeof ep.info.itunes_duration === 'string') {
                    // get time of ep
                    // {date: "2025-03-01", count: 2, totalMinutes: 70},
                    totpod += 1
                    let time = ep.info.itunes_duration
                    let seconds = parseTimeToSeconds(time)
                    totseconds += seconds
                    let date = ep.meta.timeLastOpened.substring(0, 10)
                    if (listenDays[date]) {
                        listenDays[date].count++
                        listenDays[date].totalSeconds += seconds
                    } else {
                        listenDays[date] = { date, count: 1, totalSeconds: seconds }
                    }
                }
            }
        }
    })

    // convert listenDays to an array of objects with date, count, time

    listenList = []
    Object.keys(listenDays).sort().forEach(key => {
        let entry = { date: key, count: listenDays[key].count, totalMinutes: listenDays[key].totalSeconds / 60 }
        listenList.push(entry)
    })

    tottime = formatSeconds(totseconds)

    res.render("chart", { listenList, totpod, tottime, layout: false })
})
