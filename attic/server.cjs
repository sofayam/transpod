var express = require('express')
var fs = require('fs')
var path = require("path")

var app = express()

var port = 8013
console = require("console"),
    error = console.error
//handlebars = require('express-handlebars'),
    path = require('path');

app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'hbs');

app.get("/", (req, res, next) => {
    let piecesPath = path.join(__dirname, "pieces")
    let contents = fs.readdirSync(piecesPath)
    let pieceData = []
    contents.forEach(file => {
        console.log(file)
        if (file !== ".DS_Store") {
            let metaPath = path.join(__dirname, "pieces", file, file + "meta.json")
            console.log(metaPath)
            let metaDataString = fs.readFileSync(metaPath)
            let metaData = JSON.parse(metaDataString)
            pieceData.push(metaData.description)
        }


    })
    res.render("index", { pieces: pieceData })

    // find all the subdirectories of pieces
    // grab their metadata
    // pull the first bit out to make a directory entry

})

app.get("/play/:id", (req, res, next) => {
    console.log(JSON.stringify(req.params))
    let pieceName = req.params.id
    console.log (__dirname, "pieces", pieceName, pieceName + "meta.json" )
    let filePath = path.join(__dirname, "pieces", pieceName, pieceName + "meta.json" )
    console.log(filePath)
    fs.readFile(filePath, {encoding: 'utf-8'}, function(err,data){
        if (!err) {
            let metadata = JSON.parse(data)
            // console.log('received data: ' + data);
            let mdstring = "let metadata = " + JSON.stringify(metadata)
            res.render("play", { metadata: mdstring, 
                pieceName: pieceName, 
                mp3s: metadata.mp3s, 
                defaultmp3: metadata.mp3s[0] })

        } else {
            console.log(err);
        }
    })
})

app.get("/play.js", (req, res, next) => {
    let playCodePath = path.join(__dirname, "play.js")
    let playCode = fs.readFile(playCodePath, {encoding: 'utf-8'}, function(err,data){
        if (!err) {
            res.send(data)
        } else {
            console.log(err);
        }
    })
})




app.use(express.static("pieces"));

app.listen(port, () =>
    console.log(`Example app listening on port ${port}`)
)