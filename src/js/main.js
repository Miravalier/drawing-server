import * as connection from "./connection.js";

function main()
{
    console.log("Initializing drawing game.");
    // Ignore success messages
    connection.on("success", () => {});
    connection.on("connected", () => {
        console.log("Connection to server established");
    });
    connection.connect();
}

$(main)
