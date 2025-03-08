# What utility functions are available to me when developing metrics?

When developing metrics, you may find it useful to use the utility functions provided in the 'metrics/utils.py' file. These functions are designed to help you compute common metrics and perform common operations on your data. Below are some of the utility functions available to you:

```python
def _finite_difference_gradient_predictions(info: CalculateRequest,
                                h: float = 1e-5) -> np.ndarray:
    """
    Compute the finite difference approximation of the gradient for given data.

    Args:
        info: Information required to compute the gradient including info.input_features,
              model_url and model_api_key.
        h: Perturbation magnitude.

    Returns:
        Gradient matrix of shape (num_samples, num_features).
    """
    ...
    return gradients
```

```python
def _fgsm_attack(x: np.array, gradient: np.array, epsilon: float) -> np.array:
    """
    Compute adversarial example using FGSM.

    Args:
        x: Original input sample (d-dimensional array)
        gradient: Gradient of the loss w.r.t. input (d-dimensional array)
        epsilon: Perturbation magnitude

    Returns:
        x_adv: Adversarially perturbed input
    """
    ...
    return x_adv
```

```python
def _lime_explanation(info: CalculateRequest, kernel_width: float = 0.75, esp=False) -> np.ndarray:
    """
    Compute LIME explanation for a black-box model.

    Args:
        info: information required to compute the explanation including info.input_features,
              confidence_scores, model_url and model_api_key
        kernel_width: Width of the Gaussian kernel for weighting
        esp: flag indicating if the metric to compute is Explainability Sparsity Score (ESP
             always uses predictions - not probabilities)

    Returns:
        explanation: Linear surrogate model coefficients (d-dimensional array)
    """
    ...
    return explanation
```

```python
def _query_model(generated_input_features: np.array, info: CalculateRequest) -> ModelResponse:
    """
    Helper function to query the model API using the generated input features,
    not the input features from the CalculateRequest object.

    Params:
    - generated_input : Input data to be sent to the model API
    - info : Information required to query the model API

    Returns:
    - response : Response from the model API
    """
    ...
    return response
```

Note that '\_query_model' is called multiple times in the '\_finite_difference_gradient_predictions', '\_finite_difference_gradient_confidence_scores' and 'lime_explanation' functions during their evaluation. This function sends the generated input data to the model API and returns the predicted response from the supplied model API.
