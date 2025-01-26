import isURL from "validator/lib/isURL";
import { BACKEND_URL } from "./constants";
import setState from "react";

type State = {
    modelURL: string;
    datasetURL: string;
    modelAPIKey: string;
    datasetAPIKey: string;
    isModelURLValid: boolean;
    isDatasetURLValid: boolean;
    activeStep: number;
    selectedItem: string;
    metricChips: { label: string; selected: boolean }[];
    metricsHelperText: string;
}; 

function checkURL(url: string): boolean {
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
}

export default checkURL;
