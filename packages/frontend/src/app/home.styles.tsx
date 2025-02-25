import theme from './theme';

const styles = {
  container: {
    display: 'flex',
    flexDirection: 'column' as const,
    alignItems: 'center' as const,
    justifyContent: 'center' as const,
    height: '100%',
    fontFamily: 'Arial, sans-serif',
    width: '100%',
    paddingTop: '20px',
    margin: 0,
    bgcolor: 'background.default',
    color: 'text.primary',
    p: 4,
  },
  horizontalContainer: {
    display: 'flex',
    flexDirection: 'row' as const,
    alignItems: 'center' as const,
    justifyContent: 'space-between' as const,
    background: theme.palette.primary.main,
    padding: '14px',
    borderRadius: '10px',
    width: '60%',
  },
  logoText: {
    fontSize: '36px',
    fontWeight: 'bold' as const,
  },
  formContainer: {
    display: 'flex',
    flexDirection: 'column' as const,
  },
  input: {
    width: '100%',
    marginBottom: '10px',
    fontSize: '16px',
    alignContent: 'center' as const,
  },
  button: {
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer' as const,
  },
  secondaryButton: {
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer' as const,
    color: '#fff',
  },
  accordion: {
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'center',
    alignItems: 'center',
    width: '80%',
    margin: '10px',
    borderRadius: '10px',
    backgroundColor: theme.palette.primary.main,
  },

  codeBoxTopBar: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '8px',
    height: '40px',
    backgroundColor: theme.palette.primary.main,
    borderBottom: '1px solid #e0e0e0',
    borderRadius: '10px 10px 0 0',
  },
  errorMessageHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    fontSize: '18px',
    fontWeight: 'bold',
  },
  errorMessageContainer: {
    '& .MuiPaper-root': {
      borderRadius: '10px',
      boxShadow: '0 10px 25px rgba(0, 0, 0, 0.1)',
      padding: '20px',
      minWidth: '300px',
      backgroundColor: theme.palette.primary.main,
      border: '1px solid #e0e0e0',
    },
  },
};

const reportStyles = {
  title: { font: 'helvetica', style: 'bold', size: 24 },
  sectionHeader: { font: 'helvetica', style: 'bold', size: 16 },
  subHeader: { font: 'helvetica', style: 'bold', size: 14 },
  normalText: { font: 'helvetica', style: 'normal', size: 12 },
  bulletText: { font: 'helvetica', style: 'normal', size: 11 },
};

export { styles, reportStyles };
