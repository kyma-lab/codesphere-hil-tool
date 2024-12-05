

# use: python tool_annotate.py ~/Videos/post_projs_miss_noconll ~/Videos/miss_predicted_xlm
# use: python tool_annotate.py ~/Videos/post_projs_citiz_noconll ~/Videos/citiz_predicted_xlm 

# for each file in a given directory, make a request to the /api/getpredictions endpoint 
# then save the returned annotated documents in a folder as defined and give the document the same name as the original document

import requests
import os
import json
import sys

# define the directory containing the documents to be annotated
# read the directory containing the documents to be annotated from command line argument
directory = sys.argv[1]

# read the directory where the annotated documents will be saved from command line argument
save_directory = sys.argv[2]

# make sure output directory exists, if not create it
if not os.path.exists(save_directory):
    os.makedirs(save_directory)

# define the url of the API endpoint
url = 'http://localhost:8070/api/getpredictions'

# define the headers
headers = {
    'Authorization'  : 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTcyNzgwMzg3NiwianRpIjoiZmExOTg1MzEtYWIwZC00NWE1LTk4NGMtMzljMWE3OTc0NjI3IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6InRlc3R1c2VyIiwibmJmIjoxNzI3ODAzODc2LCJjc3JmIjoiMWRlNzExNDQtMGM5OC00MzQ4LWJjZTEtMjhkNzBmMTQ3ZTcwIiwiZXhwIjoxNzI3ODkwMjc2LCJyb2xlIjoiYWRtaW4ifQ.EBjAXVjWQc2wA6fCOKjxgPKhxiPIm2PzugfcUkw2ivo',
    'Content-Type': 'application/json'
}

# loop through the files in the directory
for filename in os.listdir(directory):
    print(filename)
    if filename.endswith('.txt'):
        pdf_path = os.path.join(directory, filename)
        with open(pdf_path, 'rb') as txt_file:

            fileList = []
            fileList.append({
                'title': "bla",
                'content': txt_file.read().decode('utf-8'),
            })

            files = {'files': fileList, 'method': 'xlm_r'}

            response = requests.post(url, json=files, headers=headers)
            print(response.request.headers)
            print(response.request.body)



            if response.status_code == 200:
                # parse the json body
                json_body = response.json()
                annotated_doc = json_body['files'][0]['content']

                # save the annotated document
                annotated_filename = os.path.splitext(filename)[0] + '.txt'
                annotated_path = os.path.join(save_directory, annotated_filename)
                with open(annotated_path, 'wb') as annotated_file:
                    # Ensure annotated_doc is a bytes-like object
                    if isinstance(annotated_doc, str):
                        annotated_doc = annotated_doc.encode('utf-8')

                    annotated_file.write(annotated_doc)
            else:
                print(f"Failed to annotate {filename}: {response.status_code}")
                print(response.text)

