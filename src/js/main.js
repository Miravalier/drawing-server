import * as ui from "./ui.js";
import * as utils from "./utils.js";
import * as connection from "./connection.js";
import * as canvas from "./canvas.js";


function suppressEvent(ev) {
    ev.preventDefault();
}


async function main()
{
    // Globally expose modules
    window.connection = connection;
    window.canvas = canvas;
    window.ui = ui;
    window.utils = utils;

    // Set event handlers
    $("body").contextmenu(suppressEvent)
    $("#background, #canvas-screen #logo").on("mousedown", suppressEvent);
    $("#logo").on("dragstart", suppressEvent);

    $("#create-game-menu .accept").click(async ev => {
        await ui.fadeOut("#create-game-menu", 250);
        await connection.send({
            "type": "createLobby",
            "name": $("#create-game-menu .name").val(),
            "public": $("#create-game-menu .public").prop("checked"),
        });
        await ui.fadeIn("#main-menu", 250);
    });

    $("#create-game-menu .cancel").click(async ev => {
        await ui.fadeOut("#create-game-menu", 250);
        await ui.fadeIn("#main-menu", 250);
    });

    $("#main-menu .controls .create-game").click(async ev => {
        await ui.fadeOut("#main-menu", 250);
        await ui.fadeIn("#create-game-menu", 250);
    });

    $("#main-menu .controls .join-game").click(async ev => {
        await ui.fadeOut("#main-menu", 250);
        await ui.fadeIn("#join-game-menu", 250);
    });

    // Initialize components
    canvas.init()

    // Prepare network reply handlers
    connection.on("success", () => {});
    connection.once("connected", async message => {
        console.log("Connection to server established");
        await ui.fadeOut("#main-menu #loading-text", 500);
        await ui.fadeIn("#main-menu .controls", 500);
    });
    connection.on("drawingPrompt", async message => {
        await ui.fadeOut("#main-menu", 500);
        await ui.fadeIn("#canvas-screen", 500);
        canvas.activate();
    });

    // Wait for CSS and images to load
    await new Promise(resolve => setTimeout(resolve, 500));

    // Connect to server
    console.log("Initializing drawing game.");
    connection.connect();
}


// Run main on document ready
$(main)
