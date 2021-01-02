import * as ui from "./ui.js";
import * as connection from "./connection.js";
import * as canvas from "./canvas.js";


async function main()
{
    // Globally expose objects
    window.connection = connection;
    window.canvas = canvas;

    // Prevent right click and mousedown events
    $("body").contextmenu(ev => ev.preventDefault())
    $("#background, #canvas-screen, #load-screen").on(
        "mousedown",
        ev => ev.preventDefault()
    );

    // Initialize components
    canvas.init()

    // Prepare network reply handlers
    connection.on("success", () => {});
    connection.on("connected", async () => {
        console.log("Connection to server established");
        await ui.fadeOut("#load-screen", 500);
        canvas.activate();
        await ui.fadeIn("#canvas-screen", 500);
    });

    // Connect to server
    console.log("Initializing drawing game.");
    await ui.fadeIn("#load-screen", 500);
    connection.connect();
}


// Run main on document ready
$(main)
