import isURL from "validator/lib/isURL";
import jsPDF from "jspdf";
import { reportStyles } from "./home.styles";
import { MOCK_SCIKIT_API_URL,
         MOCK_FINBERT_API_URL,
         MOCK_FOLKTABLES_DATASET_API_URL,
         MOCK_FINANCIAL_DATASET_API_URL,
         BACKEND_FETCH_METRIC_INFO_URL} from "./constants"
import { Article } from "@mui/icons-material";

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

// retrieves a dictionary mapping task types to the metrics that can be computed for them
// returns a dictionary with the following structure:
// {
//     "binary_classification": ["metric_1", "metric_2", ...],
//     "multi_class_classification": ["metric_1", "metric_2", ...],
//     "regression": ["metric_1", "metric_2", ...],
//     ...
// }

export interface TaskToMetricMap {
    [taskType: string]: string[];
}

export interface MetricInfo {
    task_to_metric_map : TaskToMetricMap;
}

async function fetchMetricInfo(): Promise<TaskToMetricMap> {
    try {
        const response = await fetch(BACKEND_FETCH_METRIC_INFO_URL);
        const data: MetricInfo = await response.json();
        return data.task_to_metric_map;
    } catch (error) {
        console.error('Error:', error);
        throw error; // Rethrow the error so the caller can handle it
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


    results.forEach((result: any) => {
        applyStyle(doc, reportStyles.subHeader);
        const capitalizedProperty = result.property.replace(/\b\w/g, (char: string) => char.toUpperCase());
        doc.text(capitalizedProperty, 10, y);
        y += 10;

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
            const bulletPoint = `• Article ${legislation.article_number} [${legislation.article_title}] - ${legislation.description}`;
            const lines = doc.splitTextToSize(bulletPoint, 160);
            lines.forEach((line: string) => {
            doc.text(line, 20, y);
            y += 6;
            if (y > 280) { // Check if the y-coordinate is near the bottom of the page
                doc.addPage();
                y = 20; // Reset y-coordinate for the new page
            }
            });
        });
        y += 6;


        applyStyle(doc, reportStyles.normalText);
        const llmSummary = result.llm_insights[0].content;
        const maxLineLength = 160;
        const lines = doc.splitTextToSize(llmSummary, maxLineLength);
        lines.forEach((line: string) => {
            doc.text(line, 15, y);
            y += 6;
            if (y > 280) { // Check if the y-coordinate is near the bottom of the page
                doc.addPage();
                y = 20; // Reset y-coordinate for the new page
            }
        });
        y += 10;

        if (y > 280) { // Check if the y-coordinate is near the bottom of the page
            doc.addPage();
            y = 20; // Reset y-coordinate for the new page
        }
    });

    return doc;
}

export {checkURL, generateReportText, applyStyle, fetchMetricInfo };
