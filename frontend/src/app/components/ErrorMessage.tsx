import React, { useState } from 'react';
import { Dialog, DialogContent, DialogTitle, IconButton } from "@mui/material";
import CloseIcon from "@mui/icons-material/Close";
import theme from '../theme';
import { styles }from '../home.styles';

interface ErrorPopupProps {
    errorHeader?: string;
    errorMessage: string;
    onClose?: () => void;
}

const ErrorPopup: React.FC<ErrorPopupProps> = ({ errorHeader="Error", errorMessage, onClose }) => {
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
        sx={styles.errorMessageContainer}
        >
        <DialogTitle
            sx={styles.errorMessageHeader}
            id="error-dialog-title"
        >
            {errorHeader}
            <IconButton onClick={handleClose}>
            <CloseIcon />
            </IconButton>
        </DialogTitle>
        <DialogContent sx={{ fontSize: '16px', fontFamily: theme.typography.fontFamily }}>
            {errorMessage}
        </DialogContent>
        </Dialog>
    );
};

export default ErrorPopup;
