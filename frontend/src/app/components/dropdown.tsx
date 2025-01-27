import { FormControl, InputLabel, MenuItem, Select, SelectChangeEvent } from '@mui/material';
import React from 'react';

interface DropdownProps {
    items: string[];
    label: string;
    value: string;
    onChange: (value: string) => void;
    style?: React.CSSProperties; // Add style prop
}

const Dropdown: React.FC<DropdownProps> = ({ items, label, value, onChange, style }) => {
    const handleChange = (event: SelectChangeEvent<string>) => {
        onChange(event.target.value as string);
    };

    return (
        <FormControl fullWidth style={style}> {/* Apply style prop */}
            <InputLabel>{label}</InputLabel>
            <Select value={value} onChange={handleChange} label={label}>
                {items.map((item, index) => (
                    <MenuItem key={index} value={item}>
                        {item}
                    </MenuItem>
                ))}
            </Select>
        </FormControl>
    );
};

export default Dropdown;
