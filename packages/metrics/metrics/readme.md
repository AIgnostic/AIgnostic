# What is the metrics package about

The metrics package contains various black-box metrics used to test attributes of a model. The types of models for which metrics are implemented are listed below.

## Multi-class Classification

- Accuracy
- Per-class Precision
- Macro Precision
- Per-class Recall
- Macro Recall
- Per-class F1-score
- Macro F1-score
- ROC-AUC
- Explanation Stability Score (ESS)
- Explanation Sparsity Score (ESP)
- Explanation Fidelity Score (FS)
- Out-of-Distribution AUROC (OOD-AUROC)

## Binary Classification

Everything in multi-class classification as well as:

- Statistical Parity Difference
- Equal Opportunity Difference
- Equalized Odds Difference
- Disparate Impact
- False Negative Rate Difference
- Negative Predictive Value
- Positive Predictive Value
- True Positive Rate Difference

## Regression

- Mean Absolute Error
- Mean Squared Error
- R-squared
- Explanation Stability Score (ESS)
- Explanation Sparsity Score (ESP)
- Explanation Fidelity Score (FS)
