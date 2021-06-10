import * as ui from "./ui.js";
import * as utils from "./utils.js";
import * as connection from "./connection.js";
import * as canvas from "./canvas.js";


let readied = false;


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
        const name = $("#create-game-menu .name").val();
        if (!name) {
            ui.error("You must enter a name.");
            return;
        }

        let reply = await connection.send({
            "type": "setName",
            "name": name
        });
        if (reply.type === "error") return;

        reply = await connection.send({
            "type": "createLobby",
            "public": $("#create-game-menu .public").prop("checked"),
        });
        if (reply.type === "error") return;

        await ui.fadeOut("#create-game-menu", 250);

        $("#game-lobby .join-code").val(reply.joinCode);
        $("#game-lobby .owner-name").text(reply.ownerName);
        $("#game-lobby .round-timer").val(reply.roundTimer);
        await ui.fadeIn("#game-lobby", 250);
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

    $("#game-lobby .ready.button").click(async ev => {
        await ui.fadeOut("#game-lobby", 250);
        await ui.fadeIn("#canvas-screen", 250);
        canvas.activate();
        await connection.send({
            "type": "ready",
            "value": !readied
        });
    });

    $("#game-lobby .cancel.button").click(async ev => {
        await ui.fadeOut("#game-lobby", 250);
        await ui.fadeIn("#main-menu", 250);
    });

    $("#join-game-menu .cancel.button").click(async ev => {
        await ui.fadeOut("#join-game-menu", 250);
        await ui.fadeIn("#main-menu", 250);
    });

    $("#join-game-menu .join.button").click(async ev => {
        const name = $("#join-game-menu .name").val();
        const joinCode = $("#join-game-menu .join-code").val()
        if (!name) {
            ui.error("You must enter a name.");
            return;
        }
        if (!joinCode) {
            ui.error("You must enter a join code.");
            return;
        }

        let reply = await connection.send({
            "type": "setName",
            "name": name
        });
        if (reply.type === "error") return;

        reply = await connection.send({
            "type": "joinLobby",
            "joinCode": joinCode
        });
        if (reply.type === "error") return;

        await ui.fadeOut("#join-game-menu", 250);

        $("#game-lobby .join-code").val(joinCode);
        $("#game-lobby .owner-name").text(reply.ownerName);
        $("#game-lobby .round-timer").val(reply.roundTimer);
        $("#game-lobby .round-timer").prop("disabled", true);
        await ui.fadeIn("#game-lobby", 250);
    });

    // Initialize components
    connection.init();
    canvas.init();

    // Prepare network reply handlers
    connection.on("success", () => {});
    connection.on("reload", message => {
        console.log("Session terminated, reloading.");
        location.reload();
    });
    connection.once("connected", async message => {
        console.log("Connection to server established");
        await ui.fadeOut("#main-menu #loading-text", 500);
        await ui.fadeIn("#main-menu .controls", 500);
        connection.on("reconnected", message => {
            console.log("Connection re-established.");
        });
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
$(main);
