import * as React from 'react';
import Accordion from '@mui/material/Accordion';
import AccordionActions from '@mui/material/AccordionActions';
import AccordionSummary from '@mui/material/AccordionSummary';
import AccordionDetails from '@mui/material/AccordionDetails';
import Button from '@mui/material/Button';
import CodeBox from './components/CodeBox';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import Typography from '@mui/material/Typography';
import styles from './styles';

const model_api_code = `
@app.post("/predict")
def predict(dataset: DataSet) -> DataSet:
    """
    Given a dataset, predict the expected outputs for the model
    """
    # Return identical dataframe for now - fill this in with actual test models when trained
    out: np.ndarray = model.predict(dataset.rows)
    rows: list[list] = out.tolist() if len(dataset.rows) > 1 else [out.tolist()]
    return DataSet(column_names=dataset.column_names, rows=rows)`


const data_api_code = `

@app.get('/fetch-datapoints')
async def fetch_datapoints(indices: list[int] = Body([0, 1])):
    """
    Given a list of indices, fetch the data at each index and convert into
    our expected JSON format, and returns it in a JSON response. Defaults to
    fetching the first row of the ACS data.

    Args:
        indices (list[int]): A list of indices to fetch from the ACS data.
    Returns:
        JSONResponse: A JSON response containing the random datapoints.
    """
    try:

        acs_datapoints = pd.concat([features.iloc[indices], label.iloc[indices]], axis=1)
        acs_datapoints = acs_datapoints.replace({
            pd.NA: None,
            np.nan: None,
            float('inf'): None,
            float('-inf'): None
        })

        return JSONResponse(content=df_to_JSON(acs_datapoints), status_code=200)
    except Exception as e:
        print(e)
        return JSONResponse(content={"error": str(e)}, status_code=500)
`

const APIDocs: React.FC = () => {
  return (
    <div>

      <h1>AIgnostic | API Documentation</h1>
      
      <Accordion>
        <AccordionSummary
            expandIcon={<ExpandMoreIcon />}
            aria-controls="panel1-content"
            id="panel1-header"
        >
        <Typography component="span">How do I create a Dataset API for my data?</Typography>
        </AccordionSummary>
        <AccordionDetails
            sx={styles.accordion}
        >
            <CodeBox
            language="python"
            codeSnippet={data_api_code}
            />
        </AccordionDetails>
        </Accordion>

        <Accordion>
            <AccordionSummary
                expandIcon={<ExpandMoreIcon />}
                aria-controls="panel2-content"
                id="panel2-header"
            >
            <Typography component="span">How do I create a Model API for the model I wish to evaluate?</Typography>
            </AccordionSummary>
            <AccordionDetails
                sx={styles.accordion}
            >
                <CodeBox
                language="python"
                codeSnippet={model_api_code}
                />
            </AccordionDetails>
        </Accordion>

        <Accordion defaultExpanded>
            <AccordionSummary
            expandIcon={<ExpandMoreIcon />}
            aria-controls="panel3-content"
            id="panel3-header"
            >
            <Typography component="span">Accordion Actions</Typography>
            </AccordionSummary>
            <AccordionDetails
                sx={styles.accordion}
            >
            Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse nuts
            malesuada lacus ex, sit amet blandit leo lobortis eget.
            </AccordionDetails>
            <AccordionActions>
            <Button>Cancel</Button>
            <Button>Agree</Button>
            </AccordionActions>
        </Accordion>
    </div>
  );
}

export default APIDocs;
