import isURL from "validator/lib/isURL";
import jsPDF from "jspdf";
import { reportStyles } from "./home.styles";

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

    applyStyle(doc, reportStyles.subHeader);
    doc.text("Summary of Metrics:", 10, y);
    y += 10;

    results.forEach((result: any) => {
        applyStyle(doc, reportStyles.bulletText);
        doc.text(`• ${result.metric}`, 15, y);
        y += 6;
    });
    y += 10;

    applyStyle(doc, reportStyles.sectionHeader);
    doc.text("Results:", 10, y);
    y += 10;

    results.forEach((result: any) => {
        applyStyle(doc, reportStyles.subHeader);
        doc.text(result.metric, 10, y);
        y += 6;

        applyStyle(doc, reportStyles.normalText);
        doc.text(`Result: ${result.result}`, 15, y);
        y += 6;

        applyStyle(doc, reportStyles.normalText);
        doc.text(`Legislation Quote: ${result.legislation_results[0]}`, 15, y);
        y += 6;

        applyStyle(doc, reportStyles.normalText);
        doc.text(`LLM Summary: ${result.llm_model_summary[0]}`, 15, y);
        y += 10;
    });

    return doc;
}

export {checkURL, generateReportText, applyStyle };
