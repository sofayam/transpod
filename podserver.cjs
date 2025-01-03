var express = require('express')
var fs = require('fs')
var path = require("path")

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

app.get("/pod/:id", (req, res, next) => {
    let podName = req.params.id
    let epPath = path.join(__dirname, "content", podName)
    console.log("epPath ", epPath) 
    let contents = fs.readdirSync(epPath)
    let epData = []
    contents.forEach(file => {
        console.log(file)
        if (!(BADFILES.includes(file)))
            if (file.substring(file.length - 4) === ".mp3") {
                fname = file.substring(0, file.length-4)
                epData.push(fname)
            }
    })
    res.render("episodes", { eps: epData, pod: podName })
})






app.get("/play/:pod/:ep", (req, res, next) => {
    let pod = req.params.pod
    let ep = req.params.ep
    let epPath = path.join(__dirname, "content", pod, ep)
    mp3name = "/" + pod + "/" + ep + ".mp3"
    transcriptfile = path.join(__dirname, "content", pod, ep + ".json")
    transcripttext = fs.readFileSync(transcriptfile)
    console.log("epPath", epPath)
    res.render("playtrans", {mp3file: mp3name, transcript: transcripttext})

})

app.use(express.static("content"))

app.listen(PORT, () =>
    console.log(`Example app listening on port ${PORT}`)
)