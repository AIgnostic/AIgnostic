import isURL from "validator/lib/isURL";
import jsPDF from "jspdf";
import { reportStyles } from "./home.styles";
import { MOCK_MODEL_API_URL, MOCK_DATASET_API_URL} from "./constants"
import { Article } from "@mui/icons-material";

function checkURL(url: string): boolean {

    if (url === MOCK_MODEL_API_URL || url === MOCK_DATASET_API_URL) {
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

function generateReportText(results: any) : jsPDF {
    const doc = new jsPDF();
    let y = 20;

    applyStyle(doc, reportStyles.title);
    doc.text("AIgnostic Report", 105, y, { align: "center" });
    y += 15;


    results.forEach((result: any) => {
        applyStyle(doc, reportStyles.subHeader);
        doc.text(result.property, 10, y);
        y += 6;

        applyStyle(doc, reportStyles.normalText);
        doc.text(`Computed Metrics: `, 15, y);
        y += 6;

        result.computed_metrics.forEach((metric: any) => {
            applyStyle(doc, reportStyles.bulletText);
            doc.text(`• ${metric.metric}: ${metric.value}`, 20, y);
            y += 6;
        });

        applyStyle(doc, reportStyles.normalText);
        doc.text(`Relevant Legislation Extracts:`, 15, y);
        y += 6;

        result.legislation_extracts.forEach((legislation: any) => {
            applyStyle(doc, reportStyles.bulletText);
            doc.text(`• Article ${legislation.article_number} [${legislation.article_title}] - ${legislation.description}`, 20, y);
            y += 6;
        });

        applyStyle(doc, reportStyles.normalText);
        doc.text(`LLM Summary: ${result.llm_insights[0]}`, 15, y);
        y += 10;
    });

    return doc;
}

export {checkURL, generateReportText, applyStyle };
