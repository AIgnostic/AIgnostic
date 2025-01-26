const styles: { [key: string]: React.CSSProperties } = {
  container: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    height: '100%',
    fontFamily: 'Arial, sans-serif',
    backgroundColor: '#f5f5f5',
    width: '100%',
    paddingTop: '20px',
  },
  horizontalContainer: {
    display: 'flex',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  logoText: {
    fontSize: '36px',
    fontWeight: 'bold',
    color: '#333',
    fontFamily: 'serif',
  },
  formContainer: {
    display: 'flex',
    flexDirection: 'column',
  },
  input: {
    width: '100%',
    marginBottom: '10px',
    fontSize: '16px',
    alignContent: 'center',

  },
  button: {
    padding: '10px 20px',
    fontSize: '16px',
    backgroundColor: '#007BFF',
    color: '#fff',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    margin: '10px',
  },
};

export default styles;
