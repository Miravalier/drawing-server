export async function fadeOut(selector, duration)
{
    // Default to one second
    if (duration === undefined) duration = 1000;

    // Set opacity transition
    $(selector).css("transition", (duration / 1000).toFixed(2) + "s opacity");

    // Start fade animation
    $(selector).css("opacity", 0);

    // Wait one second for fade animation to finish
    await new Promise(resolve => setTimeout(resolve, duration));

    // Remove opacity transition
    $(selector).css("transition", "");
}

export async function fadeIn(selector, duration)
{
    // Default to one second
    if (duration === undefined) duration = 1000;

    // Set opacity to 0
    $(selector).css("opacity", 0);

    // Wait 10ms for opacity to take effect
    await new Promise(resolve => setTimeout(resolve, 10));

    // Set opacity transition
    $(selector).css("transition", (duration / 1000).toFixed(2) + "s opacity");

    // Set opacity to 1
    $(selector).css("opacity", 1);

    // Wait one second for fade animation to finish
    await new Promise(resolve => setTimeout(resolve, duration));

    // Remove opacity transition
    $(selector).css("transition", "");
}
