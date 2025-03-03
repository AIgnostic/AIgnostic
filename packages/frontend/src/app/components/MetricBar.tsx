import React from "react";
import Slider from "@mui/material/Slider";
import { Box, Typography } from "@mui/material";
import theme from "../theme";

interface MetricBarProps {
  min?: number;
  max?: number;
  value: number;
  idealValue: number;
  label?: string;
}

const MetricBar: React.FC<MetricBarProps> = ({
  min = 0,
  max = 1,
  value,
  idealValue,
  label = "",
}) => {
  const minLabel = min === -Infinity ? "-∞" : min;
  if (min === -Infinity) {
    min = idealValue - Math.abs(idealValue - value) * 2;
  }

  const maxLabel = max === Infinity ? "∞" : max;
  if (max === Infinity) {
    max = idealValue + Math.abs(idealValue - value) * 2;
  }

  const marks = [
    { value: min, label: `${minLabel}` }, // First marker (red)
    { value: idealValue, label: "" }, // Ideal marker (green)
    { value: value, label: value.toFixed(2) }, // Actual marker (white)
    { value: max, label: `${maxLabel}` }, // Last marker (blue)
  ];

  // Calculate percentage positions for gradient stops
  const idealPercent = ((idealValue - min) / (max - min)) * 100;
  const valuePercent = ((value - min) / (max - min)) * 100;
  const barColor = value > idealValue ? "rgb(114, 232, 139)" : "rgb(220, 59, 59)"


  return (
    <Box >
      <Typography variant="body1" sx={{ mb: 1 }}>
        {label}
      </Typography>
      <Box sx={{ position: "relative", width: "100%" }}>
        <Slider
          value={[min, max]}
          min={min}
          max={max}
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
