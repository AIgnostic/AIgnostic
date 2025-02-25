import React from 'react';
import { Page, Text, View, Document, StyleSheet } from '@react-pdf/renderer';
import { Report } from '../types';
import theme from '../theme';

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
        backgroundColor: 'rgb(197, 217, 230)',
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
                        formatUpperCase(section.property)
                    </Text>

                    {/* Computed Metrics */}
                    {section.computed_metrics.length > 0 && (
                        <View>
                            <Text style={styles.subsection}>Computed Metrics</Text>
                            {section.computed_metrics.map((metric, idx) => (
                                <Text key={idx} style={styles.bulletPoint}>
                                    • {metric.metric}: {metric.value}
                                </Text>
                            ))}
                        </View>
                    )}

                    {/* Legislation Extracts (Italicized) */}
                    {section.legislation_extracts.length > 0 && (
                        <View>
                            <Text style={styles.subsection}>Relevant Legislation Extracts</Text>
                            {section.legislation_extracts.map((legislation, idx) => (
                                <Text key={idx} style={[styles.bulletPoint, styles.quote]}>
                                    • Article {legislation.article_number} [{legislation.article_title}]: {legislation.description}
                                </Text>
                            ))}
                        </View>
                    )}

                    {/* LLM Insights */}
                    {section.llm_insights.length > 0 && (
                        <View>
                            <Text style={styles.subsection}>LLM Insights</Text>
                            {section.llm_insights.map((insight, idx) => (
                                <Text key={idx} style={styles.text}>{insight}</Text>
                            ))}
                        </View>
                    )}
                </View>
            ))}
        </Page>
    </Document>
);

export default ReportRenderer;
