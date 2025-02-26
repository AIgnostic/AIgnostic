import React from "react";
import Slider from "@mui/material/Slider";
import { Box, Typography } from "@mui/material";
import theme from "../theme";


interface MetricBarProps {
  min?: string | null;
  max?:  string | null;
  actual: string;
  ideal: string;
  label?: string;
}

const MetricBar: React.FC<MetricBarProps> = ({
  min = "0",
  max = "0",
  actual,
  ideal,
  label = "",
}) => {


  var minValue = min === null ? -Infinity : parseFloat(min as string)
  var maxValue = max === null ? Infinity : parseFloat(max as string)
  const value = parseFloat(actual);
  const idealValue = parseFloat(ideal);

  const minLabel = minValue === -Infinity ? "-∞" : minValue;
  if (minValue === -Infinity) {
    minValue = idealValue - Math.abs(idealValue - value) * 2;
  }

  const maxLabel = maxValue === Infinity ? "∞" : maxValue;
  if (maxValue === Infinity) {
    maxValue = idealValue + Math.abs(idealValue - value) * 2;
  }

  const marks = [
    { value: minValue, label: `${minLabel}` }, // First marker (red)
    { value: idealValue, label: "" }, // Ideal marker (green)
    { value: value, label: value.toFixed(2) }, // Actual marker (white)
    { value: maxValue, label: `${maxLabel}` }, // Last marker (blue)
  ];

  // Calculate percentage positions for gradient stops
  const idealPercent = ((idealValue - minValue) / (maxValue - minValue)) * 100;
  const valuePercent = ((value - minValue) / (maxValue - minValue)) * 100;
  const barColor = value > idealValue ? "rgb(114, 232, 139)" : "rgb(220, 59, 59)"


  return (
    <Box >
      <Typography variant="body1" sx={{ mb: 1 }}>
        {label}
      </Typography>
      <Box sx={{ position: "relative", width: "100%" }}>
        <Slider
          value={[minValue, maxValue]}
          min={minValue}
          max={maxValue}
          disabled
          valueLabelDisplay="off"
          marks={marks}
          sx={{
            "& .MuiSlider-track": {
              background: `linear-gradient(
                to right, 
                ${barColor} 0%, 
                ${barColor} ${valuePercent}%, 
                grey ${valuePercent}%,
                grey 100%
              )`,
              border: "none",
            },
            "& .MuiSlider-mark": {
              display: "none", // Hide marks
            },

            "& .MuiSlider-markLabel": {
              color: "white",
              fontSize: "0.75rem",
            },
            "& .MuiSlider-thumb": {
              display: "none", // Hide thumb
            },
            position: "relative",
          }}
        />
        {/* value marker */}
        <Box
          sx={{
            position: "absolute",
            top: "50%",
            left: `${idealPercent}%`,
            transform: "translate(-50%, -120%)",
            width: "4px",
            height: "30%",
            backgroundColor: "white",
            borderRadius: "2px",
            border: "1px solid dotted",
          }}
        />

        <Box
          sx={{
            position: "absolute",
            top: "31%",
            left: `${valuePercent}%`,
            transform: "translate(-50%, -150%)",
            width: "2px",
            height: "2px",
            backgroundColor: "white",
            borderRadius: "5px",
          }}
        />
      </Box>
      <Typography variant="caption">
        Computed Value: {value.toFixed(3)}
        <br />
        Target: {idealValue}
      </Typography>
    </Box>
  );
};

export default MetricBar;
