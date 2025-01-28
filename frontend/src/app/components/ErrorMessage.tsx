import React, { useState } from 'react';
import { Dialog, DialogContent, DialogTitle, Button, IconButton } from "@mui/material";
import CloseIcon from "@mui/icons-material/Close";

interface ErrorPopupProps {
    errorMessage: string;
    onClose?: () => void;
}

const ErrorPopup: React.FC<ErrorPopupProps> = ({ errorMessage, onClose }) => {
    const [open, setOpen] = useState(true);

    const handleClose = () => {
        setOpen(false);
        if (onClose) onClose();
    };

    return (
        <Dialog
        open={open}
        onClose={handleClose}
        aria-labelledby="error-dialog-title"
        sx={{
            '& .MuiPaper-root': {
            borderRadius: '2xl',
            boxShadow: '0 10px 25px rgba(0, 0, 0, 0.1)',
            padding: '20px',
            minWidth: '300px',
            },
        }}
        >
        <DialogTitle
            sx={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            fontSize: '18px',
            fontWeight: 'bold',
            }}
            id="error-dialog-title"
        >
            Error
            <IconButton onClick={handleClose}>
            <CloseIcon />
            </IconButton>
        </DialogTitle>
        <DialogContent sx={{ fontSize: '16px', color: '#d32f2f' }}>
            {errorMessage}
        </DialogContent>
        </Dialog>
    );
};

export default ErrorPopup;
