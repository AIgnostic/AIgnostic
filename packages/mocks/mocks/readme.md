The mocks package contains a variety of example data servers and model servers for real models and datasets. In the context of AIgnostic, each mock model can be paired with a mock datapoint for pipeline testing for various tasks. A mock model and corresponding dataset for the mock are provided for each type of task:

| Model Input | Task Type                 | Mock Model             | Mock Dataset        |
| ----------- | ------------------------- | ---------------------- | ------------------- |
| Numeric     | Binary Classification     | Scikit Mock Classifier | Folktables          |
| Numeric     | Multiclass Classification | None                   | None                |
| Numeric     | Regression                | Scikit Mock Regressor  | Boston Housing Data |
| Text        | Binary Classification     | None                   | None                |
| Text        | Multiclass Classification | FinBERT                | Financial Data      |
| Text        | Regression                | None                   | None                |
| Text        | Next Token Generation     | tinystories-1M         | tinystories dataset |
