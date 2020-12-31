import * as connection from "./connection.js";
import * as canvas from "./canvas.js";


function main()
{
    // Prepare handlers
    connection.on("success", () => {});
    connection.on("connected", () => {
        console.log("Connection to server established");
    });

    // Connect to server
    console.log("Initializing drawing game.");
    connection.connect();

    // Activate canvas
    canvas.activate();

    // Globally expose objects
    window.connection = connection;
    window.canvas = canvas;
}


// Run main on document ready
$(main)
