
function checkURL(url: string): boolean {
    // Logic for determining the boolean value based on the input string

    // Regular expression to validate common protocols
    const validProtocolRegex = /^(https?|ftp):\/\//i;

    // Check if the URL has a valid protocol (http, https, or ftp)
    if (!validProtocolRegex.test(url)) {
        return false; // Reject if the protocol is missing or incorrect
    }

    try {
        new URL(url); // If the URL is valid, this will not throw an error
        return false; // Return false if input is empty
    } catch (e) {
        alert(e + url)
        return false; // If an error is thrown, the URL is invalid
    }

}

export default checkURL;
  