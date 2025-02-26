import isURL from "validator/lib/isURL";
import jsPDF from "jspdf";
import { MOCK_SCIKIT_API_URL,
         MOCK_FINBERT_API_URL,
         MOCK_FOLKTABLES_DATASET_API_URL,
         MOCK_FINANCIAL_DATASET_API_URL} from "./constants"

function checkURL(url: string): boolean {

    if (url === MOCK_SCIKIT_API_URL ||
        url === MOCK_FINBERT_API_URL ||
        url === MOCK_FOLKTABLES_DATASET_API_URL ||
        url === MOCK_FINANCIAL_DATASET_API_URL)  {
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

function applyStyle(doc: jsPDF, style: any) {
    doc.setFont(style.font, style.style);
    doc.setFontSize(style.size);
}

export {checkURL, applyStyle };
