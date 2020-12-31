const saveFormat = "image/webp";
const saveQuality = 0.5;
const pathLimit = 16;

let container = null;
let canvas = null;
let context = null;
let penDown = false;
let pathLength = 0;


export function clear()
{
    context.clearRect(0, 0, canvas.width, canvas.height);
}


export function activate()
{
    // Deactivate old canvas, if present
    deactivate();

    // Set the global variables
    if (!container) container = $("#canvas-container").get(0);
    if (!canvas) canvas = $("#canvas").get(0);
    context = canvas.getContext("2d");

    // Set canvas dimensions
    onResize();

    // Attach listeners
    canvas.addEventListener("mousemove", onDraw);
    canvas.addEventListener("mousedown", onPenDown);
    canvas.addEventListener("mouseup", onPenUp);
    window.addEventListener("resize", onResize)
}


export function deactivate()
{
    if (context) {
        canvas.removeEventListener("mousemove", onDraw);
        canvas.removeEventListener("mousedown", onPenDown);
        canvas.removeEventListener("mouseup", onPenUp);
        window.removeEventListener("resize", onResize)
        clear();
    }

    context = null;
}


export function save()
{
    return canvas.toDataURL(saveFormat, saveQuality);
}


function onPenDown(ev)
{
    console.log("Pen Down");

    let x = ev.clientX - container.offsetLeft;
    let y = ev.clientY - container.offsetTop;

    context.beginPath();
    context.moveTo(x, y);
    context.strokeStyle = "orange";
    context.lineWidth = 5;

    penDown = true;
}


function onPenUp(ev)
{
    if (!penDown) return;

    console.log("Pen Up");
    penDown = false;

    onDraw(ev);

    context.closePath();
    pathLength = 0;
}


function onDraw(ev)
{
    if (!penDown) return;

    let x = ev.clientX - container.offsetLeft;
    let y = ev.clientY - container.offsetTop;

    context.lineTo(x, y);
    context.stroke();
    pathLength++;

    if (pathLength == pathLimit)
    {
        onPenUp(ev);
        onPenDown(ev);
    }
}


function onResize()
{
    canvas.width = canvas.parentElement.clientWidth;
    canvas.height = canvas.parentElement.clientHeight;
}
