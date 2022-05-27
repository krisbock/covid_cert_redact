# covid_cert_redact
Example of using Azure Cognitive Service Read API to redact IHI number from Covid certs.

It takes in a PDF, converts it to an image, and then uses the Read API to identify the bounding boxes of the IHI number.

PIL is used to fill in the bounding box and save the image.

This project uses dotenv to store Cognitive Service API keys.

Create the environment using requirements.txt
