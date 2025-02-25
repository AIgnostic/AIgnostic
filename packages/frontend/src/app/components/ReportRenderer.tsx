import React from 'react';
import { Page, Text, View, Document, StyleSheet } from '@react-pdf/renderer';
import { ReportSection } from '../types';

// Create styles
const styles = StyleSheet.create({
  page: {
    padding: 20,
    backgroundColor: '#ffffff',
  },
  section: {
    marginBottom: 15,
    paddingBottom: 10,
    borderBottom: '1px solid #ddd',
  },
  header: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 8,
    textDecoration: 'underline',
  },
  subsection: {
    marginTop: 8,
    fontSize: 14,
    fontWeight: 'bold',
  },
  bulletPoint: {
    marginLeft: 10,
    fontSize: 12,
  },
  text: {
    fontSize: 12,
    marginBottom: 4,
  },
});

interface ReportProps {
  report: ReportSection[];
}

const Report: React.FC<ReportProps> = ({ report }) => (
  <Document>
    <Page size="A4" style={styles.page}>
      {report.map((section, index) => (
        <View key={index} style={styles.section}>
          {/* Section Header */}
          <Text style={styles.header}>{section.property}</Text>

          {/* Computed Metrics */}
          {section.computed_metrics.length > 0 && (
            <>
              <Text style={styles.subsection}>Computed Metrics:</Text>
              {section.computed_metrics.map((metric, idx) => (
                <Text key={idx} style={styles.bulletPoint}>
                  • {metric.metric}: {metric.result}
                </Text>
              ))}
            </>
          )}

          {/* Legislation Extracts */}
          {section.legislation_extracts.length > 0 && (
            <>
              <Text style={styles.subsection}>Relevant Legislation Extracts:</Text>
              {section.legislation_extracts.map((legislation, idx) => (
                <Text key={idx} style={styles.bulletPoint}>
                  • Article {legislation.article_number} [{legislation.article_title}]: {legislation.description}
                </Text>
              ))}
            </>
          )}

          {/* LLM Insights */}
          {section.llm_insights.length > 0 && (
            <>
              <Text style={styles.subsection}>LLM Insights:</Text>
              {section.llm_insights.map((insight, idx) => (
                <Text key={idx} style={styles.text}>{insight.content}</Text>
              ))}
            </>
          )}
        </View>
      ))}
    </Page>
  </Document>
);

export default Report;
