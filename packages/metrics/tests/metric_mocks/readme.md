# What is the purpose of `metric_mocks` directory?

Some metrics require querying the model. In order to test these metrics, we need to provide a model endpoint and api keys. This folder contains mocks of the model endpoint used to hardcode model output values to ensure metrics are computed as expected.

However, the mocks used for testing metrics should be consistent with the general mock interface even if it changes. As such, additional integration tests are required checking functionality of metrics in conjunction with these mock interfaces (done in other packages which directly enforce this interaction).
