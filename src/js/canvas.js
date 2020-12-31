const saveFormat = "image/webp";
const saveQuality = 0.5;
const pathLimit = 16;

let container = null;
let canvas = null;
let context = null;
let penDown = false;
let pathLength = 0;
let penColor = "#000000";
let penSize = 3;
let canvasColor = "#c8c8c8";


export function fill(color)
{
    if (!color) color = canvasColor;
    canvasColor = color;

    const oldFillStyle = context.fillStyle;
    context.fillStyle = color;
    context.fillRect(0, 0, canvas.width, canvas.height);
    context.fillStyle = oldFillStyle;
}


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
    window.addEventListener("resize", onResize)

    // Create UI controls
}


export function deactivate()
{
    if (context) {
        canvas.removeEventListener("mousemove", onDraw);
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
    if (penDown) return;

    let x = ev.clientX - container.offsetLeft;
    let y = ev.clientY - container.offsetTop;

    context.beginPath();
    context.moveTo(x, y);
    context.strokeStyle = penColor;
    context.lineWidth = penSize;

    penDown = true;
}


function onPenUp(ev)
{
    if (!penDown) return;

    penDown = false;
    context.closePath();
    pathLength = 0;
}


function onDraw(ev)
{
    if (ev.buttons) onPenDown(ev);
    if (!ev.buttons) onPenUp(ev);
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
    fill();
}
