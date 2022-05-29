from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials

from pdf2image import convert_from_path
import re
import os
from PIL import Image, ImageDraw
from dotenv import load_dotenv
import time

ROOT_DIR = os.getcwd()
env_path = os.path.join(ROOT_DIR, '.env')
load_dotenv(dotenv_path=env_path, verbose=True)
'''
Authenticate
Authenticates your credentials and creates a client.
'''
subscription_key = os.getenv('SUBSCRIPTION_KEY')
endpoint = os.getenv('ENDPOINT')

computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))
'''
END - Authenticate
'''

'''
OCR: Read File using the Read API, extract text - local
This example extracts text from a local image, then prints results.
This API call can also recognize remote image text (shown in next example, Read File - remote).
'''
# Get image path
images_folder = 'path to pdf'
pdf_path = os.path.join (images_folder, "PDF Name.pdf")
# convert pdf to image - use 1st element as convert returns a list
pdf_to_image = convert_from_path(pdf_path, 500)[0]
#pdf_image = pdf_image.convert('RGBA')
pdf_to_image.save('covid_cert.jpeg', format="JPEG")

# Open the image
with open('covid_cert.jpeg', "rb") as read_image:

    # Call API with image and raw response (allows you to get the operation location)
    read_response = computervision_client.read_in_stream(read_image, raw=True)
    # Get the operation location (URL with ID as last appendage)
    read_operation_location = read_response.headers["Operation-Location"]
    # Take the ID off and use to get results
    operation_id = read_operation_location.split("/")[-1]

    # Call the "GET" API and wait for the retrieval of the results
    while True:
        read_result = computervision_client.get_read_result(operation_id)
        if read_result.status.lower () not in ['notstarted', 'running']:
            break
        print ('Waiting for result...')
        time.sleep(10)

    # Print results, line by line
    if read_result.status == OperationStatusCodes.succeeded:
        for text_result in read_result.analyze_result.read_results:
            for line in text_result.lines:
                #if line.text == 'Individual Healthcare Identifier (IHI)':
                pattern = '^(?:\w{4} ){3}\w{4}$'
                result = re.match(pattern, line.text)
                if result:
                    ihi_bbox = line.bounding_box 
                    # open image in PIL
                    image = Image.open(read_image)
                    draw = ImageDraw.Draw(image)
                    # get coordinates
                    x0 = ihi_bbox[0]
                    y0 = ihi_bbox[1]
                    # we need to add the width and height of the bounding box
                    # using a max function to get maximum coverage
                    width = max(ihi_bbox[2], ihi_bbox[4]) - min(ihi_bbox[0], ihi_bbox[6])
                    height = max(ihi_bbox[5], ihi_bbox[7]) - min(ihi_bbox[1], ihi_bbox[3])
                    x1 = x0 + width
                    y1 = y0 + height
                    fill = (0, 0, 0)
                    draw.rectangle([x0, y0, x1, y1], fill=fill)
                    image.save('covid_redacted.jpeg', format="JPEG")

    print()
    '''
    END - Redacted
    '''

print("End of Computer Vision quickstart.")