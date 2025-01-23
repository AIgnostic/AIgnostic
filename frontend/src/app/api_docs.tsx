import React from 'react';
import CodeBox from './components/CodeBox';


const APIDocs: React.FC = () => {
  return (

    <CodeBox
        language="python"
        code={`@app.post("/predict")
def predict(dataset: DataSet) -> DataSet:
    """
    Given a dataset, predict the expected outputs for the model
    """
    # Return identical dataframe for now - fill this in with actual test models when trained
    out: np.ndarray = model.predict(dataset.rows)
    rows: list[list] = out.tolist() if len(dataset.rows) > 1 else [out.tolist()]
    return DataSet(column_names=dataset.column_names, rows=rows)`}/>
          
  );
};

export default APIDocs;
