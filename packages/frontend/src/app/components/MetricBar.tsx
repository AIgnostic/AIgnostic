import React from "react";
import Slider from "@mui/material/Slider";
import { Box, Typography } from "@mui/material";

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
  // Calculate percentage positions for gradient stops
  const idealPercent = ((idealValue - min) / (max - min)) * 100;
  const valuePercent = ((value - min) / (max - min)) * 100;

  const marks = [
    { value: min, label: `${min}` }, // First marker (red)
    { value: idealValue, label: "" }, // Ideal marker (green)
    { value: value, label: value.toFixed(2) }, // Actual marker (white)
    { value: max, label: `${max}` }, // Last marker (blue)
  ];

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
                rgb(161, 23, 23) 0%, 
                rgb(161, 23, 23) ${idealPercent}%, 
                rgb(26, 165, 14) ${idealPercent}%,
                rgb(26, 165, 14) 100%
              )`,
              border: "none",
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
            left: `${valuePercent}%`,
            transform: "translate(-50%, -120%)",
            width: "4px",
            height: "30%",
            backgroundColor: "white",
            borderRadius: "2px",
          }}
        />
      </Box>
      <Typography variant="caption">
        Computed Value: {value}
        <br />
        Target: {idealValue}
      </Typography>
    </Box>
  );
};

export default MetricBar;
