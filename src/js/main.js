import * as ui from "./ui.js";
import * as connection from "./connection.js";
import * as canvas from "./canvas.js";


async function main()
{
    // Globally expose objects
    window.connection = connection;
    window.canvas = canvas;

    // Prepare handlers
    connection.on("success", () => {});
    connection.on("connected", async () => {
        console.log("Connection to server established");
        await ui.fadeOut("#load-screen");
        canvas.activate();
        await ui.fadeIn("#canvas");
    });

    // Connect to server
    console.log("Initializing drawing game.");
    await ui.fadeIn("#load-screen");
    connection.connect();
}


// Run main on document ready
$(main)
