var express = require('express')
var fs = require('fs')
var path = require("path")
var jsdom = require("jsdom")
const { JSDOM } = jsdom

var app = express()


var PORT = 8014

if (process.argv.length > 2) {
    PORT = parseInt(process.argv[2])
}

BADFILES = [".gitignore", ".DS_Store", "ReadMe.md"]
console = require("console"),
    error = console.error
//handlebars = require('express-handlebars'),
    path = require('path');

app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'hbs');

app.get("/", (req, res, next) => {
    let podPath = path.join(__dirname, "content")
    let contents = fs.readdirSync(podPath)
    let pcData = []
    contents.forEach(file => {
        console.log(file)
        if (!(BADFILES.includes(file))){
            pcData.push(file)
        }
    })
    res.render("podcasts", { pods: pcData })
})

function compareEpisode (ep1, ep2) {
    // TBD include various sorting criteria here based on data in _config.md
    i1 = getIndex(ep1.displayname)
    i2 = getIndex(ep2.displayname)
    if (! (i1.match && i2.match)) {
        return ep1.displayname.localeCompare(ep2.displayName)
    } else {
        return i1.index.localeCompare(i2.index)
    }
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

                    epData.push({ displayname: fname, encoded: encodeURIComponent(fname), chunks: chunklist })
                }
            }
    })
   
    // sort episodes
    epData.sort(compareEpisode)

    res.render("episodes", { eps: epData, pod: podName })
    console.log(chunkdict)
})






app.get("/play/:pod/:ep", (req, res, next) => {
    let pod = req.params.pod
    let ep = req.params.ep
    let epPath = path.join(__dirname, "content", pod, ep)
    mp3name = "/" + pod + "/" + encodeURIComponent(ep) + ".mp3"
 
//    transcriptfile = path.join(__dirname, "content", pod, ep + ".json")
//    transcripttext = fs.readFileSync(transcriptfile)
//  TODO apologize if no transcript is available
    transcript = getTranscript(pod, ep)
    transcripttext = transcript.text
    transcriptsrc = transcript.src
    console.log("epPath", epPath)
    res.render("playtrans", {mp3file: mp3name, 
        transcript: transcripttext,
        source: transcriptsrc})

})

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
    let source = "whisper transcript"
    foundtranscript = false
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
        source = "patreon transcript"
        transcripttext = transhtml(path.join(transfolder, foundtranscript))
    } else {
    // 3 Else use the whisper thing from the json file
        transcriptfile = path.join(__dirname, "content", pod, ep + ".json")
        transcripttext = fs.readFileSync(transcriptfile)
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
