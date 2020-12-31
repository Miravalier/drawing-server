export async function fadeOut(selector)
{
    // Set opacity transition
    $(selector).css("transition", "1s opacity");

    // Start fade animation
    $(selector).css("opacity", 0);

    // Wait one second for fade animation to finish
    await new Promise(resolve => setTimeout(resolve, 1000));

    // Disable element
    $(selector).css("display", "none");

    // Remove opacity transition
    $(selector).css("transition", "");
}

export async function fadeIn(selector)
{
    // Set opacity to 0
    $(selector).css("opacity", 0);

    // Set opacity transition
    $(selector).css("transition", "1s opacity");

    // Set opacity to 1
    $(selector).css("opacity", 1);

    // Wait one second for fade animation to finish
    await new Promise(resolve => setTimeout(resolve, 1000));

    // Remove opacity transition
    $(selector).css("transition", "");
}
