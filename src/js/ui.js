export async function fadeOut(selector, duration)
{
    // Default to one second
    if (duration === undefined) duration = 1000;

    // Set opacity to 1, display to flex
    $(selector).css({opacity: 1, display: "flex"});

    // Wait 50ms for opacity and display to take effect
    await new Promise(resolve => setTimeout(resolve, 50));

    // Set opacity transition
    $(selector).css("transition", (duration / 1000).toFixed(2) + "s opacity");

    // Start fade animation
    $(selector).css("opacity", 0);

    // Wait for fade animation to finish
    await new Promise(resolve => setTimeout(resolve, duration));

    // Remove opacity and transition
    $(selector).css({display: "none", opacity: "", transition: ""});
}

export async function fadeIn(selector, duration)
{
    // Default to one second
    if (duration === undefined) duration = 1000;

    // Set opacity to 0, display to flex
    $(selector).css({opacity: 0, display: "flex"});

    // Wait 50ms for opacity and display to take effect
    await new Promise(resolve => setTimeout(resolve, 50));

    // Set transition
    $(selector).css("transition", (duration / 1000).toFixed(2) + "s opacity");

    // Set opacity to 1
    $(selector).css("opacity", 1);

    // Wait for fade animation to finish
    await new Promise(resolve => setTimeout(resolve, duration));

    // Remove opacity and transition
    $(selector).css({opacity: "", transition: ""});
}


export function error(message)
{
    console.error(message);
}
