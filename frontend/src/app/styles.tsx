const styles = {
    container: {
      display: 'flex',
      flexDirection: 'column' as const,
      alignItems: 'center' as const,
      justifyContent: 'center' as const,
      height: '100%',
      fontFamily: 'Arial, sans-serif',
      backgroundColor: '#f5f5f5',
      width: '100%',
      paddingTop: '20px',
    },
    horizontalContainer: {
      display: 'flex',
      flexDirection: 'row' as const,
      alignItems: 'center' as const,
      justifyContent: 'space-between' as const,
    },
    logoText: {
      fontSize: '36px',
      fontWeight: 'bold' as const,
      color: '#333',
      fontFamily: 'serif',
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
      padding: '10px 20px',
      fontSize: '16px',
      backgroundColor: '#333',
      color: '#fff',
      border: 'none',
      borderRadius: '4px',
      cursor: 'pointer' as const,
      margin: '10px',
    },
    accordion: {
        display: 'flex', 
        flexDirection: 'column', 
        alignItems: 'center' 
    },

};
  
export default styles;