# AIgnostic

A framework and tool for auditing and compliance/legislation adherence for black box models.
The product comes in two forms:
- a scalable web application, hosted at https://aignostic.docsoc.co.uk
- a local environment (getting started guide below)

## Getting Started
To use the web application, go to https://aignostic.docsoc.co.uk.
Click the 'Getting Started' button to go to our docs page containing information on how to:
- Set up your model and dataset APIs to interface with our product
- Add your own metrics
- ...and a lot more information about how you can get the most out of AIgnostic

To get started with the local environment (runs a Docker Compose under the hood to run the services in containers locally):
- Clone the repo into your desired location within your home directory
- run ```./aignostic.py run```
- ...and you're done! It should all start running out-of-box
- navigate to http://localhost:4200 and you should see the AIgnostic landing page (should look the same as the interface on our prod server, linked above)

## Contact
If you run into any issues or face any bugs that require troubleshooting, feel free to reach out to us via the Discussions section of the AIgnostic repo. We will get back to you at earliest convenience.

## PRs and Extending AIgnostic
AIgnostic is designed as a free open-source tool. Our vision is to encourage research into AI explainability and accountability, and make it easier to evaluate models before putting them into production, to make advancements in AI as safe-to-use as possible. We welcome PRs and our team will aim to get the reviewed at earliest convenience.


## Acknowledgements
A huge thanks to Matthew Wicker, our supervisor, for proposing the idea, for facilitating the whole process and providing all of the resources we needed for implementing the metrics etc. - for making this all possible basically!

Thanks to the folks at the Turing Institute for their valuable feedback that shaped this journey.

Thanks to the Department of Computing at Imperial, and SEGP module leaders, for their insights that helped finetune the initial scope of the product.
