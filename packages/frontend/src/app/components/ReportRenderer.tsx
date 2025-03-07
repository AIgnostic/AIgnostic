import React from 'react';
import { Page, Text, View, Document, Link, StyleSheet } from '@react-pdf/renderer';
import { Report, Metric, LegislationExtract } from '../types';
import theme from '../theme';
import MetricBarPDF from './MetricBarPDF';
import { legislation } from '../constants';

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
    boldText: {
        marginLeft: 8,
        fontSize: 12,
        fontWeight: 'bold',
        fontFamily: 'Times-Roman',
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
        marginBottom: 8,
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
                <Text style={styles.text}>
                    AIgnostic is a tool for aiding audits and evaluations. It is merely a framework and guide.
                </Text>
                <Text style={styles.text}>
                    The developers of this tool cannot be held liable for any decisions, complaints, and legal matters
                    that arise from the AIgnostic evaluation or report.
                </Text>
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
                    <Text style={styles.header}>{formatUpperCase(section.property)}</Text>

                    {/* Computed Metrics */}
                    {Object.entries(section.computed_metrics).length > 0 ? (
                        <View>
                            <Text style={styles.subsection}>Computed Metrics</Text>
                            {section.computed_metrics.map((metric_info, idx) => (
                                <View key={idx} style={{ marginBottom: 10 }}>
                                    <Text style={[styles.text, { fontSize: 14 }]}>
                                        {metric_info.metric.replace(/_/g, ' ').replace(/\b\w/g, (char) => char.toUpperCase())}
                                    </Text>
                                    {metric_info.error ? (
                                        <Text style={styles.text}>
                                            An error occurred during the computation of this metric.
                                        </Text>
                                    ) : (
                                        <MetricBarPDF
                                            value={parseFloat(metric_info.value)}
                                            idealValue={parseFloat(metric_info.ideal_value)}
                                            min={metric_info.range[0] === null ? -Infinity : parseFloat(metric_info.range[0])}
                                            max={metric_info.range[1] === null ? Infinity : parseFloat(metric_info.range[1])}
                                        />
                                    )}
                                </View>
                            ))}
                        </View>
                    ) : (
                        <View>
                            <Text style={styles.subsection}>Computed Metrics</Text>
                            <Text style={styles.text}>No metrics were computed for this property.</Text>
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

                    {/* Legislation Extracts (Detailed with Links) */}
                    {section.legislation_extracts.length > 0 && (
                        <View>
                            <Text style={styles.subsection}>Legislation</Text>
                            {section.legislation_extracts.map((leg, idx) => (
                                <View key={idx}>
                                    <Text style={styles.boldText}>{leg[0].article_type}</Text>
                                        {leg.map((extract: LegislationExtract, idx1: number) => (
                                            <View key={idx1}>
                                                <Text style={[styles.text, { fontStyle: 'italic' }]}> 
                                                    Article {extract.article_number}: {extract.article_title}
                                                </Text>
                                                {}
                                                <Text style={styles.bulletPoint}>
                                                    • Link: <Link src={extract.link} style={styles.hyperlink}>{extract.link}</Link>
                                                </Text>
                                            </View>
                                        ))}
                                    </View>
                            ))}
                        </View>
                    )}
                </View>
            ))}
        </Page>
    </Document>
);


export default ReportRenderer;

