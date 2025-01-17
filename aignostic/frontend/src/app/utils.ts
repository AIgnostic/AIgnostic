import isURL from 'validator/lib/isURL';

function checkURL(url: string): boolean {
    // Logic for determining the boolean value based on the input string

    try {
        if (!isURL(url) || url.includes('%20')) {
            throw new Error('Invalid URL ');
        }
        new URL(url); // If the URL is valid, this will not throw an error
        return true;
    } catch (e) {
        console.log(e + url)
        return false; // If an error is thrown, the URL is invalid
    }

}

export default checkURL;
  