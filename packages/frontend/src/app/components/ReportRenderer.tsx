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
                        {formatUpperCase(section.property)}
                    </Text>

                    {/* Computed Metrics */}
                    {section.computed_metrics.length > 0 && (
                        <View>
                            <Text style={styles.subsection}>Computed Metrics</Text>
                            {section.computed_metrics.map((metric, idx) => (
                                <View key={idx}>
                                    {/* <Text style={styles.bulletPoint}>
                                        • {metric.metric}: {metric.value}
                                    </Text>
                                    <Text style={styles.bulletPoint}>
                                        • Ideal Value: {metric.ideal_value}
                                    </Text>
                                    <Text style={styles.bulletPoint}>
                                        • Range: {metric.range[0]} - {metric.range[1]}
                                    </Text> */}
                                    <MetricBarPDF
                                        value={parseFloat(metric.value)}
                                        idealValue={parseFloat(metric.ideal_value)}
                                        min={parseFloat(metric.range[0])}
                                        max={parseFloat(metric.range[1])}
                                    />
                                </View>
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


const MetricBarPDF: React.FC<{ value: number; idealValue: number; min?: number; max?: number }> = ({
    value,
    idealValue,
    min = 0,
    max = 1,
  }) => {
    // const width = 200; // Total width of the bar
    const valuePercent = ((value - min) / (max - min)) * 100;
    const idealPercent = ((idealValue - min) / (max - min)) * 100;

    const red = 'rgb(139, 20, 20)';
    const lightRed = 'rgb(220, 59, 59)';
    const green = 'rgb(65, 163, 86)';
    const lightGreen = 'rgb(114, 232, 139)';
  
    return (
      <View style={{ marginVertical: 10 }}>
        {/* Bar container */}
        <View style={{
          height: 10,
          backgroundColor: "lightgray",
          position: "relative",
          borderRadius: 5,
          marginVertical: 5,
        }}>
          {/* Red section (before ideal value) */}
          <View style={{
            position: "absolute",
            left: 0,
            width: `${valuePercent}%`,
            height: "100%",
            backgroundColor: `${value > idealValue ? lightGreen : lightRed}`,
            borderTopLeftRadius: 5,
            borderBottomLeftRadius: 5,
          }} />
          
          {/* Green section (after ideal value) */}
          <View style={{
            position: "absolute",
            left: `0%`,
            width: `100%`,
            height: "100%",
            borderRadius: 5,
            // border: `1px solid black`,
          }} />
      
          {/* Marker for actual value */}
          <View style={{
            position: "absolute",
            left: `${idealPercent}%`,
            width: 2,
            height: "180%",
            borderLeftWidth: 1,
            borderLeftColor: "black",
            borderLeftStyle: "dashed",
            transform: "translateY(-4%)",
            borderRadius: 5,
          }} />
        </View>
  
        {/* Labels */}
        <Text style={{ color: value >= idealValue ? `${green}` : `${red}`, fontSize: 10 }}>
            Value: {value.toFixed(2)} | Target: {idealValue.toFixed(2)}
        </Text>
      </View>
    );
  };
  
  