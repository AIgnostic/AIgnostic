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
      border: 'none',
      borderRadius: '4px',
      cursor: 'pointer' as const,
      margin: '10px',
    },
    accordion: {
        display: 'flex', 
        flexDirection: 'column', 
        justifyContent: 'center',
        alignItems: 'center',
        width: '80%',
        margin: '10px',
    },

};
  
export default styles;