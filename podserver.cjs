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
    let contents = fs.readdirSync(podPath, {withFileTypes: true})
    .filter(dirent => dirent.isDirectory())
    .map(dirent => dirent.name)
    let pcData = []
    contents.forEach(file => {
        console.log(file)
        if (!(BADFILES.includes(file))){
            let meta = readMetaPod(file)
            podEntry = {name: file, ...meta}
            pcData.push(podEntry)
        }
    })
    res.render("podcasts", { pods: pcData, layout: false})
})

function compareEpisode (ep1, ep2) {
    if (feedOrderDict) {
        i1 = feedOrderDict[ep1.displayname]
        i2 = feedOrderDict[ep2.displayname]
        return i1 - i2
    } else {
    
    // TBD include various sorting criteria here based on data in _config.md
    i1 = getIndex(ep1.displayname)
    i2 = getIndex(ep2.displayname)
    return i1.index.localeCompare(i2.index)
    }

}

function makeFeedOrderDict(feed) {
    let dict = {}
    let index = 1
    feed.forEach(ep => {
        let cleanEp = ep.title.replace(/ /g, "_").replace(/\//g, "_") 
        dict[cleanEp] = index;
        index++
    })
    return dict
}

app.get("/pod/:id", (req, res, next) => {
    let podName = req.params.id
    let epPath = path.join(__dirname, "content", podName)
    console.log("epPath ", epPath) 
    let contents = fs.readdirSync(epPath)
    let epData = []
    // find no of chunks for each file
    let chunkdict = {}
    let reg = /(^.*)chunk.*.mp3/

    let latestfeedPath = path.join(__dirname, "content", podName + ".latestfeed") 
    if (fs.existsSync(latestfeedPath)) {
        console.log("latestfeed exists")
        let latestFeed = JSON.parse(fs.readFileSync(latestfeedPath))
        feedOrderDict = makeFeedOrderDict(latestFeed)
    } else {
        feedOrderDict = null
    }
  
    contents.forEach(file => {
        let matches = reg.exec(file);
        if (matches) {
            stem = matches[1]
            if (!(Object.keys(chunkdict).includes(stem))) {
                chunkdict[stem] = 0
            }
            chunkdict[stem]++
        }
    })
    contents.forEach(file => {
        console.log(file)
        if (!(BADFILES.includes(file)))
            if (file.substring(file.length - 4) === ".mp3") {
                // filter out all the chunks from the main list
                if (!(file.includes("chunk"))) {
                    fname = file.substring(0, file.length - 4)
                    var chunklist = []
                    if (Object.keys(chunkdict).includes(file)) {
                        for (let i = 1; i <= chunkdict[file]; i++) {
                            chunklist.push(i.toString().padStart(2, "0"))
                        }
                    }

                    epData.push({ podName, displayname: fname, encoded: encodeURIComponent(fname), finished: !(isUnfinished(podName, fname)), chunks: chunklist })
                }
            }
    })

    const meta = readMetaPod(podName)
    // if we only want unfinished
    if(meta.show === "unfinished") {
        epData = epData.filter((item) => isUnfinished(podName, item.displayname))
    }
    // throw out the finished episodes 

    // sort episodes
    epData.sort(compareEpisode)

    // reverse order if dropdown set to latest
  
    if (meta.order === "latest") {
        epData.reverse()
    }

    orderList = epData

    res.render("episodes", { eps: epData, pod: podName, layout: false })
    console.log(chunkdict)
})


function isUnfinished(podName, epName) {
    meta = readMetaEp(podName, epName)
    // console.log("isunfinished: ",  meta)
    return ! meta.finished 

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
    nextep =  encodeURIComponent(getNextep(ep))
    console.log("epPath", epPath,   "meta",  meta)
    res.render("playtrans", {pod, mp3file: mp3name, 
        transcript: transcripttext,
        source: transcriptsrc, meta, nextep, layout: false})

})

app.get("/recentListen", (req, res) => {
    // Get all podcast metadata, sort on timeLastOpened field, filter for unfinished
    let epList = []
    res.render("recentListen", {epList, layout: false})
})

app.get("/recentPublish", (req, res) => {
    // TBD get data from podcast feed ? when ?
    let epList = []
    res.render("recentPublish", {epList, layout: false})
})

function readMetaEp(pod, ep)  {
    const metaPath = path.join(__dirname, "content", pod, ep + ".meta")
    if (fs.existsSync(metaPath)) {
        try {
            return JSON.parse(fs.readFileSync(metaPath, 'utf-8'));
        } catch (error) {
            console.error(`Error reading ${metaPath}:`, error);
        }
    }
    return { finished: false, timeLastOpened: 0, timeInPod: 0}; // Default values
}


function readMetaPod(folderName) {
    const metaPath = path.join(__dirname, "content", `${folderName}.meta`);
    if (fs.existsSync(metaPath)) {
        try {
            return JSON.parse(fs.readFileSync(metaPath, 'utf-8'));
        } catch (error) {
            console.error(`Error reading ${metaPath}:`, error);
        }
    }
    return { order: "latest", show: "all" }; // Default values
}

function writeMetaEp(metaPath, finished, timeLastOpened, timeInPod){
    const metaData = {finished, timeLastOpened, timeInPod}
    fs.writeFileSync(metaPath, JSON.stringify(metaData, null, 4), 'utf-8')
    console.log(`Updated meta file: ${metaPath}`);
}


function writeMetaPod(folderName, order, show) {
    const metaPath = path.join(__dirname, "content", `${folderName}.meta`);
    const metaData = { order, show };
    
    try {
        fs.writeFileSync(metaPath, JSON.stringify(metaData, null, 4), 'utf-8');
        console.log(`Updated meta file: ${metaPath}`);
    } catch (error) {
        console.error(`Error writing ${metaPath}:`, error);
    }
}



app.post('/update-meta-ep', (req, res) => {
    console.log("BODY>", req.body)
    const { name, finished, timeLastOpened, timeInPod } = req.body;
    // TBD cut off mp3 and change to meta
    // TBD maybe some URL ding needed here
    const deconame = decodeURIComponent(name)
    const podcastpath = deconame.slice(0,-4)
    const metapath = path.join(__dirname, "content", podcastpath + ".meta")
    try {
         writeMetaEp(metapath, finished, timeLastOpened, timeInPod)

        res.json({ success: true });
    } catch (error) {
        console.error(`Error writing ${metapath}`, error)
        res.status(400).json({  success: false, message: "Invalid Episode"});
    }

});

app.post('/update-meta-pod', (req, res) => {
    console.log("BODY>", req.body)
    const { name, order, show } = req.body;
    const folderPath = path.join(__dirname, "content", name);

    if (fs.existsSync(folderPath) && fs.statSync(folderPath).isDirectory()) {
        writeMetaPod(name, order, show);
        res.json({ success: true });
    } else {
        res.status(400).json({ success: false, message: "Invalid Podcast" });
    }
});

app.use(express.static("content"))

app.listen(PORT, () =>
    console.log(`Example app listening on port ${PORT}`)
)

function findFileInDirectory(directory, searchString) {
    try {
        const files = fs.readdirSync(directory); // Read all files in the directory
        const matchingFiles = files.filter(file => file.includes(searchString));

        if (matchingFiles.length > 0) {
            console.log("Found files:", matchingFiles);
            return matchingFiles
        } else {
            console.log("No matching files found.");
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
        return {match: true, index: paddedNumber}
    }
    else
       return {match: false, index: title}
} 

const getTranscript = (pod, ep) => {
    // 1 Is there an html transcript
    //    1.1 Derive canonical index
    // const match = ep.match(/^#(\d+)/)
    const {match, index} = getIndex(ep)
    paddedNumber = ""
    transfolder = ""
    let source = "whisper"
    foundtranscript = false
    transcripttext = ""

    if  (match) {

    //    1.2 Look for file containing canonical index in transcripts folder

            transfolder = path.join(__dirname, "content", pod, "transcripts")
            const res = findFileInDirectory(transfolder, index)
            if (res.length == 1) {
                foundtranscript = res[0]
                console.log("found ", foundtranscript)
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
        } catch(error) {
            console.log("no transcript found, defaulting to polite apology")
            transcripttext = '[{ "start": 0.0, "end": 10000.0, "text": "申し訳ありませんが、このエピソードのトランスクリプトはまだ利用できません。"}]'
        }
    }

    return {src: source, text: transcripttext}
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
