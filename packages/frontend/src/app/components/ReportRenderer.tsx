import React from 'react';
import { Page, Text, View, Document, Link, StyleSheet } from '@react-pdf/renderer';
import { Report } from '../types';
import theme from '../theme';
import MetricBarPDF from './MetricBarPDF';

// Create styles
const styles = StyleSheet.create({
    page: {
        padding: 70,
        backgroundColor: '#ffffff',
    },
    mainTitle: {
        fontSize: 32,
        fontWeight: 'bold',
        textAlign: 'center',
        fontFamily: 'Times-Roman',
        color: theme.palette.primary.main,
        marginBottom: 20,
        padding: 20,
        // borderWidth: 5,
        // borderRadius: 10,
        // borderColor: theme.palette.primary.main,
    },
    section: {
        marginBottom: 15,
        paddingBottom: 10,
        borderBottomWidth: 1,
        borderBottomColor: '#ddd',
        borderBottomStyle: 'solid',
    },
    header: {
        fontSize: 20,
        fontWeight: 'bold',
        marginBottom: 8,
        // textDecoration: 'underline',
        fontFamily: 'Times-Roman',
        padding: 5,
        borderRadius: 5,
        backgroundColor: 'rgb(157, 183, 199)',
    },
    subsection: {
        marginTop: 8,
        marginBottom: 8,
        fontSize: 16,
        fontWeight: 'bold',
        fontFamily: 'Times-Roman',
        padding: 5,
        borderRadius: 5,
        backgroundColor: 'grey',
    },
    bulletPoint: {
        marginLeft: 10,
        fontSize: 12,
        fontFamily: 'Times-Roman',
    },
    quote: {
        fontStyle: 'italic',
    },
    text: {
        fontSize: 12,
        marginBottom: 6,
        fontFamily: 'Times-Roman',
    },
    hyperlink: {
        color: 'blue',
        textDecorationLine: 'underline',
    },
});

interface ReportProps {
    report: Report;
}

const formatUpperCase = (key: string) =>
    key.replace(/_/g, ' ').replace(/\b\w/g, (char) => char.toUpperCase());

const ReportRenderer: React.FC<ReportProps> = ({ report }) => (
    <Document>
        <Page size="A4" style={styles.page}>
            {/* Report Title */}
            <Text style={styles.mainTitle}>AIgnostic | Final Report</Text>

            {/* Disclaimers Section */}
            <View style={styles.section}>
                <Text style={styles.header}>Legal Information and Disclaimers</Text>
                <Text style={styles.text}>AIgnostic is a tool for aiding audits and evaluations. It is merely a framework and guide.</Text>
                <Text style={styles.text}>The developers of this tool cannot be held liable for any decisions, complaints and legal matters that arise from the AIgnostic evaluation or report.</Text>
            </View>

            {/* General Info Section */}
            <View style={styles.section}>
                <Text style={styles.header}>General Info</Text>
                {Object.entries(report.info).map(([key, value], index) => (
                    <Text key={index} style={styles.text}>
                        {formatUpperCase(key)}: {value}
                    </Text>
                ))}
            </View>

            {/* Report Properties */}
            {report.properties.map((section, index) => (
                <View key={index} style={styles.section}>
                    {/* Section Header */}
                    <Text style={styles.header}>
                        {formatUpperCase(section.property)}
                    </Text>

                    {/* Computed Metrics */}
                    {section.computed_metrics.length > 0 ?
                        <View>
                            <Text style={styles.subsection}>Computed Metrics</Text>
                            {section.computed_metrics.map((metric, idx) => (
                                <View key={idx} style={{ marginBottom: 10 }}>
                                    <Text style={[styles.text, {fontSize: 14}]}>
                                        {metric.metric.replace(/_/g, ' ').replace(/\b\w/g, (char) => char.toUpperCase())}
                                    </Text>
                                    <MetricBarPDF
                                        value={parseFloat(metric.value)}
                                        idealValue={parseFloat(metric.ideal_value)}
                                        min={(metric.range[0] === null) ? -Infinity : parseFloat(metric.range[0])}
                                        max={(metric.range[1] === null) ? Infinity : parseFloat(metric.range[1])}
                                    />
                                </View>
                            ))}
                        </View>  

                        :

                        // TODO: Add suggested metrics
                        <View>
                            <Text style={styles.subsection}>Computed Metrics</Text>
                            <Text style={styles.text}>No metrics were computed for this property.</Text>
                        </View>
                    }

                    {/* LLM Insights */}
                    {section.llm_insights.length > 0 && (
                        <View>
                            <Text style={styles.subsection}>LLM Insights</Text>
                            {section.llm_insights.map((insight, idx) => (
                                <Text key={idx} style={styles.text}>{insight}</Text>
                            ))}
                        </View>
                    )}

                    
                    {/* Legislation Extracts (Italicized) */}
                    {section.legislation_extracts.length > 0 && (
                        <View>
                            <Text style={styles.subsection}>Legislation</Text>
                            <Text style={styles.text}>For more detailed information pertaining to the legislation, refer to the relevant legislation articles via the following links:</Text>
                            {section.legislation_extracts.map((legislation, idx) => (
                                <Text key={idx} style={[styles.bulletPoint, styles.quote]}>
                                    • Article {legislation.article_number} [{legislation.article_title}]:  
                                    <Link src={legislation.link} style={styles.hyperlink}>
                                        {legislation.link}
                                    </Link>
                                </Text>
                            ))}
                        </View>
                    )}

                </View>
            ))}
        </Page>
    </Document>
);

export default ReportRenderer;

