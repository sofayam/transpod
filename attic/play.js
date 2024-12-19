
let isPlaying = false;
let mode = "Display"
// These are absolute bars
let currentBar = -1
let currentPage = ""
let dumpPages = []
let pieceName = metadata.description.shortname


// let clickFields = metadata.pages[0].coords

let captureFields = []

function toggleMode() {
    if (mode == "Capture")
        mode = "Display"
    else
        mode = "Capture"
    return mode
}

let BARS = countBars(metadata)
let barlength = audio.duration / BARS
let barMap = buildBarMap(metadata)
let pageMap = buildPageMap(metadata)
let rabMap = buildRelAbsBarMap(metadata)

function countBars(metadata) {
    let total = 0
    for (i in metadata.pages) {
        total += metadata.pages[i].coords.length
    }
    return total
}


function buildBarMap(metadata) {
    // bar map is zero based
    let barMap = {}
    let barCount = 0
    for (i in metadata.pages) {
        let relCount = 0
        let page = metadata.pages[i].page
        for (j in metadata.pages[i].coords) {
            barMap[barCount] = {page: page, idx: relCount }
            barCount++
            relCount++
        }
    }
    return barMap   
}

function buildRelAbsBarMap(metadata) {
    let rabMap = {}
    let absCtr = 0
    for (i in metadata.pages) {
        let page = metadata.pages[i].page
        rabMap[page] = []
        for (j in metadata.pages[i].coords) {
            rabMap[page].push(absCtr)
            absCtr++
        }
    }
    return rabMap
}

function buildPageMap(metadata) {
    let pageMap = {}
    for (i in metadata.pages) {
        let page = metadata.pages[i]
        pageMap[page.page] = page.coords
    }
    return pageMap
}

function closestBarFromClick(x, y) {
    //the bars start at 0
    closestbardistance = 10000000000.0
    var closestbar = 0
    var idx = 0
    let clickFields = pageMap[currentPage]
    while (idx < clickFields.length) {
        bar = clickFields[idx]
        distance = Math.sqrt(Math.abs(x - bar[0]) * Math.abs(y - bar[1]))
        if (distance < closestbardistance) {
            closestbardistance = distance
            closestbar = idx
        }
        idx++      
    }

    // Now work out what the absolute bar is 
    let absBar = rabMap[currentPage][closestbar]


    return absBar + 1 // Convert to human numbering
}


function getMousePos(canvas, evt) {
    var rect = canvas.getBoundingClientRect();
    return {
        x: (evt.clientX - rect.left) / (rect.right - rect.left) * canvas.width,
        y: (evt.clientY - rect.top) / (rect.bottom - rect.top) * canvas.height
    };
}

function changemp3(obj) {
    const whichmp3 = document.getElementById("whichmp3")
    var strUser = whichmp3.options[whichmp3.selectedIndex].value;
    let a = 1;
    let b = obj.options
}

window.onload = function () {

    const goButton = document.getElementById("go-button");
    const dumpButton = document.getElementById("dump-button");
    const storeButton = document.getElementById("store-button");
    const modeButton = document.getElementById("mode-button")
    const whichbar = document.getElementById("whichbar")
    const whichmp3 = document.getElementById("whichmp3")
    const metadatadump = document.getElementById("metadatadump")

    var backgroundCanvas = document.getElementById('backgroundCanvas');
    var backgroundCtx = backgroundCanvas.getContext('2d');
    var drawingCanvas = document.getElementById('drawingCanvas');
    var drawingCtx = drawingCanvas.getContext('2d');

    // var drawing = false;

    whichmp3.addEventListener("change", () => {
        var strUser = whichmp3.options[whichmp3.selectedIndex].value;
        audio.src = strUser
    })

    modeButton.addEventListener("click", () => {
        let newmode = toggleMode()
        // window.alert(newmode)
        modeButton.textContent = newmode;
    })

    function goBar(x) {
        // This only moves the audio point. The barTick function will later trigger updating the
        // page displayed and the bar marker 
        barlength = audio.duration / BARS
        newbar = x - 1 // convert back from human bar numbering
        newdestination = barlength * newbar;
        // window.alert("I want to go to: " + newdestination)
        audio.currentTime = newdestination
    }

    dumpButton.addEventListener("click", () => {
        let dumpString = JSON.stringify(dumpPages)
        metadatadump.value = dumpString
    })
    storeButton.addEventListener("click", () => {
        let newPage = {page: currentPage, coords: captureFields}
        captureFields = []
        dumpPages.push(newPage)
    })
    goButton.addEventListener("click", () => {

        newbar = whichbar.value
        goBar(newbar)

    })


    function loadNotes(pageName) {
        var img = new Image();
        img.onload = function () {
            var canvas = backgroundCanvas;
            var ctx = backgroundCtx;
            var hRatio = canvas.width / img.width;
            var vRatio = canvas.height / img.height;
            var ratio = Math.min(hRatio, vRatio);
            var centerShift_x = (canvas.width - img.width * ratio) / 2;
            var centerShift_y = (canvas.height - img.height * ratio) / 2;
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.drawImage(img, 0, 0, img.width, img.height,
                centerShift_x, centerShift_y, img.width * ratio, img.height * ratio);
        }
        img.src = "/" + pieceName + "/" + pageName + ".jpg"; // TBD derive from metadata

    }

    drawingCanvas.addEventListener('mousedown', function (e) {

        let mpos = getMousePos(drawingCanvas, e)

        var x = mpos.x
        var y = mpos.y

        if (mode == "Capture") {
            window.alert("Capture Mode " + x + " " + y)
            captureFields.push([Math.round(x), Math.round(y)])
            markCapture(x,y)

        } else {
            // window.alert("Playback Mode " + x  + " " + y)
            var closestbar = closestBarFromClick(x, y)
            goBar(closestbar)
            whichbar.value = closestbar
            // window.alert("Closest bar " + closestbar) 
        }

    })


    function barTick() {
        let nextBar = Math.floor((audio.currentTime / audio.duration) * BARS)
        if (nextBar < BARS)
        displayChange(nextBar) 
    }

    function displayChange(nextBar) {
        if (nextBar == currentBar) {
            return 
        } else {
            let newPage = pageForBar(nextBar)
            if (newPage != currentPage) {
                changePage(newPage)
                currentPage = newPage
            }
            let relBar = relativeBar(nextBar)
            changeBar(relBar, currentPage)
            currentBar = nextBar
        }       
    }


    function pageForBar(absoluteBar) {
        // catch end of piece problem
        return barMap[absoluteBar].page
    }
    function relativeBar(absoluteBar) {
        return barMap[absoluteBar].idx
    }

    function changePage(pageName) {
        loadNotes(pageName)
    }

    function changeBar(barOnPage, currentPage) {
        let clickFields = pageMap[currentPage]
        let xy = clickFields[barOnPage]
        drawingCtx.clearRect(0, 0, drawingCanvas.width, drawingCanvas.height);
        drawingCtx.strokeStyle = "red"
        drawingCtx.lineWidth = 3
        drawingCtx.beginPath();
        drawingCtx.arc(xy[0], xy[1], 10, 0, 2 * Math.PI);
        drawingCtx.stroke();
    }

    function markCapture(x,y) {
        drawingCtx.strokeStyle = "green"
        drawingCtx.lineWidth = 3
        drawingCtx.beginPath();
        drawingCtx.arc(x, y, 10, 0, 2 * Math.PI);
        drawingCtx.stroke();
    }

    window.setInterval(barTick, 100)

    loadNotes()


}

