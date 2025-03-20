var express = require('express')
var fs = require('fs')
var path = require("path")
var jsdom = require("jsdom")
const { JSDOM } = jsdom

var app = express()


var PORT = 8014
var orderList = null
var feedOrderDict = null

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
const hbs = exphbs.create({
    extname: 'hbs',
    helpers: {
        eq: (a, b) => a === b
    }
});
app.engine('hbs', hbs.engine);
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'hbs');

app.use(express.json())

app.get("/", (req, res, next) => {
    let podPath = path.join(__dirname, "content")
    // check for global meta and filter out the advanced stuff
    let contents = fs.readdirSync(podPath, { withFileTypes: true })
        .filter(dirent => dirent.isDirectory())
        .map(dirent => dirent.name)
    let pcData = []
    contents.forEach(file => {
        // console.log(file)
            let meta = readMetaPod(file)
            podEntry = { name: file, ...meta }
            pcData.push(podEntry)
    })
    metaGlobal = readMetaGlobal()
    res.render("podcasts", { pods: pcData, layout: false, coresetOnly: metaGlobal.coresetOnly})
})

function compareEpisode(ep1, ep2) {

    // TBD include various sorting criteria here based on data in _config.md
    i1 = getIndex(ep1.displayname)
    i2 = getIndex(ep2.displayname)
    return i1.index.localeCompare(i2.index)

}


app.get("/pod/:id", (req, res, next) => {
    let podName = req.params.id
    let epPath = path.join(__dirname, "content", podName)
    // console.log("epPath ", epPath) 
    let contents = fs.readdirSync(epPath)
    let epData = []
    // find no of chunks for each file
    let sortonpubdate = false

    let latestfeedPath = path.join(__dirname, "content", podName + ".latestfeed")
    if (fs.existsSync(latestfeedPath)) { // TODO change to use a sensible config value
        sortonpubdate = true
    }

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
                    finished: !(isUnfinished(podName, fname)), info
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
        epData.sort((a, b) => comparePublishedParsed(b.info.published_parsed, a.info.published_parsed))
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
    if (!orderList)
        return
    let epData = orderList
    let found = false
    let nextep = ""
    epData.forEach(item => {
        if (found) {
            nextep = item.displayname
            found = false
        }
        if (item.displayname === ep) {
            found = true
        }
    })
    return nextep
}

app.get("/play/:pod/:ep", (req, res, next) => {
    let pod = req.params.pod
    let ep = req.params.ep
    let epPath = path.join(__dirname, "content", pod, ep)
    mp3name = "/" + pod + "/" + encodeURIComponent(ep) + ".mp3"
    meta = readMetaEp(pod, ep)

    //    transcriptfile = path.join(__dirname, "content", pod, ep + ".json")
    //    transcripttext = fs.readFileSync(transcriptfile)
    //  TODO apologize if no transcript is available
    transcript = getTranscript(pod, ep)
    transcripttext = transcript.text
    transcriptsrc = transcript.src
    nextep = encodeURIComponent(getNextep(ep))
    let infopath = epPath + ".info"
    let info = {}
    if (fs.existsSync(infopath)) {
        info = JSON.parse(fs.readFileSync(infopath, 'utf-8'))
    }   

    res.render("playtrans", {
        pod, mp3file: mp3name,
        transcript: transcripttext,
        source: transcriptsrc, meta, nextep, 
        info,
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

    let contents = fs.readdirSync(podPath, { withFileTypes: true })
        .filter(dirent => dirent.isDirectory())
        .map(dirent => dirent.name)
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

function addTimes(times) {
    // Initialize total seconds
    let totalSeconds = 0;
    
    // Process each time string
    times.forEach(time => {
      // Remove the leading colon if present
      const cleanTime = time.startsWith(':') ? time.substring(1) : time;
      
      // Split the time string into parts
      const parts = cleanTime.split(':').map(Number);
      
      // Handle different formats
      if (parts.length === 3) {
        // Format is HH:mm:ss
        const [hours, minutes, seconds] = parts;
        totalSeconds += (hours * 3600) + (minutes * 60) + seconds;
      } else if (parts.length === 2) {
        // Format is mm:ss
        const [minutes, seconds] = parts;
        totalSeconds += (minutes * 60) + seconds;
      }
    });
    
    // Convert total seconds back to HH:mm:ss format
    const hours = Math.floor(totalSeconds / 3600);
    const minutes = Math.floor((totalSeconds % 3600) / 60);
    const seconds = totalSeconds % 60;
    
    // Format with leading zeros and return with leading colon
    return `${hours}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
  }
  


app.get("/recentListen", (req, res) => {

    // Get all podcast metadata, sort on timeLastOpened field, filter for unfinished
    let podPath = path.join(__dirname, "content")

    let contents = fs.readdirSync(podPath, { withFileTypes: true })
        .filter(dirent => dirent.isDirectory())
        .map(dirent => dirent.name)
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
                let epentry = { pod: podName, name: barename, encoded: encodeURIComponent(barename), meta, info }
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
    let totalTime = addTimes(times)
     
    
    epList = epList.filter(ep => ep.meta.timeLastOpened !== 0)
    epList.sort((a, b) => b.meta.timeLastOpened.localeCompare(a.meta.timeLastOpened))

    // take the first 100
    epList = epList.slice(0, 100)

    res.render("recentListen", { epList, totalTime, layout: false })
})

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


function  readMetaPod(folderName) {
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
    return { order: "latest", show: "all" , coreset: "false"}; // Default values
}

function  readMetaGlobal() {
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
    const metaData = { order, show, coreset};

    try {
        fs.writeFileSync(metaPath, JSON.stringify(metaData, null, 4), 'utf-8');
        console.log(`Updated meta pod file: ${metaPath}`);
    } catch (error) {
        console.error(`Error writing ${metaPath}:`, error);
    }
}

function writeMetaGlobal(coresetOnly) {
    const metaPath = path.join(__dirname, "content/_global.meta");
    const metaData = { coresetOnly };  
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

    const { coresetOnly } = req.body;
    try {
        writeMetaGlobal(coresetOnly);
        res.json({ success: true });
    } catch (error) {
        res.status(400).json({ success: false, message: "Error storing global metadata" });
    }
});

app.use(express.static("content"))

app.listen(PORT, () =>
    console.log(`Listening on port ${PORT}`)
)

function findFileInDirectory(directory, searchString) {
    try {
        const files = fs.readdirSync(directory); // Read all files in the directory
        const matchingFiles = files.filter(file => file.includes(searchString));

        if (matchingFiles.length > 0) {

            return matchingFiles
        } else {
            console.error("No matching files found.");
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
    // 1 Is there an html transcript
    //    1.1 Derive canonical index
    // const match = ep.match(/^#(\d+)/)
    const { match, index } = getIndex(ep)
    paddedNumber = ""
    transfolder = ""
    let source = "whisper"
    foundtranscript = false
    transcripttext = ""

    if (match) {

        //    1.2 Look for file containing canonical index in transcripts folder

        transfolder = path.join(__dirname, "content", pod, "transcripts")
        const res = findFileInDirectory(transfolder, index)
        if (res.length == 1) {
            foundtranscript = res[0]
        }

        // 2 If so convert to json and use that
    }
    if (foundtranscript) {
        source = "patreon"
        transcripttext = transhtml(path.join(transfolder, foundtranscript))
    } else {
        // 3 Else use the whisper thing from the json file
        transcriptfile = path.join(__dirname, "content", pod, ep + ".json")
        try {
            transcripttext = fs.readFileSync(transcriptfile)
        } catch (error) {
            console.log("no transcript found, defaulting to polite apology")
            transcripttext = '[{ "start": 0.0, "end": 10000.0, "text": "申し訳ありませんが、このエピソードのトランスクリプトはまだ利用できません。"}]'
        }
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
