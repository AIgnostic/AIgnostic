import React from 'react';
import { Text, View } from '@react-pdf/renderer';

const MetricBarPDF: React.FC<{ value: number; idealValue: number; min?: number; max?: number }> = ({
    value,
    idealValue,
    min = 0,
    max = 1,
  }) => {

    if (min === -Infinity) {
        min = idealValue - Math.abs(idealValue - value) * 2;
    }
    
    if (max === Infinity) {
        max = idealValue + Math.abs(idealValue - value) * 2;
    }

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
        <Text style={{ color: value >= idealValue ? `${green}` : `${red}`, fontSize: 10 }}>Value: {value.toFixed(2)} | Target: {idealValue.toFixed(2)}</Text>
      </View>
    );
  };
  
export default MetricBarPDF;