import isURL from "validator/lib/isURL";

function checkURL(url: string): boolean {

    if (url === 'http://mock-dataset-api:5000/fetch-datapoints' || url === 'http://mock-model-api:5001/predict') {
        return true; 
    }
    if (url === '') {
        return false;
    }
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
};

export default checkURL;
