import * as ui from "./ui.js";

const saveFormat = "image/webp";
const saveQuality = 0.5;
const pathLimit = 16;
const eraserSize = 8;
const drawCooldown = 3; // Milliseconds
const fillThreshold = 128;

let canvas = null;
let context = null;
let bounds = null;
let mouseHeld = false;
let pathLength = 0;
let penColor = "#000000";
let penSize = 3;
let canvasColor = "#c8c8c8";
let activeControl = null;
let tool = "";
let lastDrawTime = Date.now();


export function init()
{
    $("#settings .color").change(ev => {
        const colorPicker = ev.currentTarget;
        penColor = colorPicker.value;
    });
    $("#settings .size").change(ev => {
        const sizeField = ev.currentTarget;
        penSize = sizeField.value;
    });

    async function onControlClicked(ev) {
        // Trigger a mouse up event
        onMouseUp();

        // If the previous tool was settings
        if (tool == "settings")
        {
            ui.fadeOut("#settings", 100).then(() => {
                $("#settings").css("display", "none");
            });
        }

        // If the active control is clicked, set inactive
        const control = $(ev.currentTarget);
        if (activeControl && control.data("tool") == activeControl.data("tool"))
        {
            activeControl.removeClass("active");
            $("#canvas").removeClass(activeControl.data("tool"));
            activeControl = null;
            tool = "";
            return;
        }

        // Swap out active control
        if (activeControl)
        {
            activeControl.removeClass("active");
            $("#canvas").removeClass(activeControl.data("tool"));
        }
        control.addClass("active");
        $("#canvas").addClass(control.data("tool"));
        activeControl = control;

        // Swap out tool
        tool = control.data("tool");

        // If the new tool is settings
        if (tool == "settings")
        {
            $("#settings").css("display", "flex");
            ui.fadeIn("#settings", 100);
        }
    }

    $("#canvas-screen .controls a").click(onControlClicked);
}


export function fill(color)
{
    if (!color) color = canvasColor;
    canvasColor = color;

    context.fillStyle = color;
    context.fillRect(0, 0, canvas.width, canvas.height);
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
    if (!canvas) canvas = $("#canvas").get(0);
    context = canvas.getContext("2d");
    bounds = canvas.getBoundingClientRect();
    canvasColor = "#c8c8c8";
    penColor = "#000000";
    penSize = 3;

    // Set canvas dimensions
    onResize();

    // Attach listeners
    canvas.addEventListener("mousedown", onMouseEvent);
    canvas.addEventListener("mouseup", onMouseEvent);
    canvas.addEventListener("mousemove", onMouseEvent);
    canvas.addEventListener("mouseenter", onMouseEvent);
    canvas.addEventListener("mouseleave", onMouseUp);
    window.addEventListener("resize", onResize)
}


export function deactivate()
{
    if (context) {
        canvas.removeEventListener("mousedown", onMouseEvent);
        canvas.removeEventListener("mouseup", onMouseEvent);
        canvas.removeEventListener("mousemove", onMouseEvent);
        canvas.removeEventListener("mouseenter", onMouseEvent);
        canvas.removeEventListener("mouseleave", onMouseUp);
        window.removeEventListener("resize", onResize)
        clear();
    }

    context = null;
    bounds = null;
}


export function save()
{
    return canvas.toDataURL(saveFormat, saveQuality);
}


function onMouseDown(x, y)
{
    if (!mouseHeld)
    {
        mouseHeld = true;
        switch (tool)
        {
            case "pen": onPenStart(x, y); break;
            case "eraser": onEraserStart(x, y); break;
            case "fill": onFillStart(x, y); break;
            case "dropper": onDropperStart(x, y); break;
            case "settings": onSettingsStart(x, y); break;
        }
    }
}


function onMouseUp(x, y)
{
    if (mouseHeld)
    {
        mouseHeld = false;
        switch (tool)
        {
            case "pen": onPenEnd(x, y); break;
            case "eraser": onEraserEnd(x, y); break;
            case "fill": onFillEnd(x, y); break;
            case "dropper": onDropperEnd(x, y); break;
            case "settings": onSettingsEnd(x, y); break;
        }
    }
}


function onMouseEvent(ev)
{
    let x = ev.clientX - bounds.left;
    let y = ev.clientY - bounds.top;

    if (ev.buttons) {
        onMouseDown(x, y);
    }
    else {
        onMouseUp(x, y);
    }

    if (mouseHeld)
    {
        // Limit draw by cooldown
        const currentTime = Date.now();
        const timeElapsed = currentTime - lastDrawTime;
        if (timeElapsed < drawCooldown) return;
        lastDrawTime = currentTime;

        switch (tool)
        {
            case "pen": onPen(x, y); break;
            case "eraser": onEraser(x, y); break;
            case "fill": onFill(x, y); break;
            case "dropper": onDropper(x, y); break;
            case "settings": onSettings(x, y); break;
        }
    }
}


function onPenStart(x, y)
{
    context.beginPath();
    context.moveTo(x, y);
    context.strokeStyle = penColor;
    context.lineWidth = penSize;
    context.lineCap = "round";
    context.lineJoin = "round";
}


function onPenEnd(x, y)
{
    context.closePath();
    pathLength = 0;
}


function onPen(x, y)
{
    context.lineTo(x, y);
    context.stroke();
    pathLength++;

    if (pathLength == pathLimit)
    {
        onPenEnd(x, y);
        onPenStart(x, y);
    }
}


function onEraserStart(x, y)
{
    context.beginPath();
    context.moveTo(x, y);
    context.strokeStyle = canvasColor;
    context.lineWidth = eraserSize * 4;
    context.lineCap = "round";
    context.lineJoin = "round";
}


function onEraserEnd(x, y)
{
    context.closePath();
    pathLength = 0;
}


function onEraser(x, y)
{
    context.lineTo(x, y);
    context.stroke();
    pathLength++;

    if (pathLength == pathLimit)
    {
        onEraserEnd(x, y);
        onEraserStart(x, y);
    }
}


function onFillStart(originX, originY)
{
    // Get pixels
    const imageData = context.getImageData(0, 0, canvas.width, canvas.height);
    const pixels = new Uint32Array(imageData.data.buffer);

    // Get colors
    const fillColor = swap32(parseInt(penColor.substring(1) + "FF", 16));
    const targetColor = pixels[originY * canvas.width + originX];

    // Make sure colors are different
    if (targetColor === fillColor) return;

    // Perform flood fill
    const nodes = [originX, originY];
    const visited = new Set();
    while (nodes.length > 0)
    {
        // Get the next position to check
        const y = nodes.pop();
        const x = nodes.pop();
        const index = y * canvas.width + x;

        // Make sure this position has not yet been checked
        if (visited.has(index)) continue;
        visited.add(index);

        // If the color difference is greater than the threshold,
        // perform the fill.
        const nodeColor = pixels[index];
        const difference = colorDifference(nodeColor, targetColor);
        if (difference < fillThreshold)
        {
            pixels[index] = fillColor;
            if (x + 1 < canvas.width) nodes.push(x + 1, y);
            if (x - 1 >= 0) nodes.push(x - 1, y);
            if (y + 1 < canvas.height) nodes.push(x, y + 1);
            if (y - 1 >= 0) nodes.push(x, y - 1);
        }
    }

    // Update pixels
    context.putImageData(imageData, 0, 0);
}


function onFillEnd(x, y)
{
}


function onFill(x, y)
{
}


function onDropperStart(x, y)
{
    // Get pixels
    const imageData = context.getImageData(0, 0, canvas.width, canvas.height);
    const pixels = new Uint32Array(imageData.data.buffer);

    // Get color under cursor
    let targetColor = swap32(pixels[y * canvas.width + x]);
    targetColor = targetColor.toString(16).padStart(8, '0');

    // Set pen color
    penColor = '#' + targetColor.slice(0, -2);

    // Update settings picker
    $("#settings .color").val(penColor);
}


function onDropperEnd(x, y)
{
}


function onDropper(x, y)
{
}


function onSettingsStart(x, y)
{
    $("#canvas-screen .controls .settings").trigger("click");
}


function onSettingsEnd(x, y)
{
}


function onSettings(x, y)
{
}


function onResize()
{
    canvas.width = canvas.parentElement.clientWidth - 16;
    canvas.height = canvas.parentElement.clientHeight - 56;
    fill();
    
}


function colorDifference(a, b)
{
    return  (Math.abs((a & 0x00FF0000) - (b & 0x00FF0000)) >> 16) +
            (Math.abs((a & 0x0000FF00) - (b & 0x0000FF00)) >> 8) +
            Math.abs((a & 0x000000FF) - (b & 0x000000FF));
}


const swapBuffer = new ArrayBuffer(4);
const swapView = new DataView(swapBuffer);
export function swap32(value)
{
    swapView.setUint32(0, value, true);
    return swapView.getUint32(0, false);
}


export function hex(value)
{
    return "0x" + value.toString(16).padStart(8, "0");
}
