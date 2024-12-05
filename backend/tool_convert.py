import os
import sys
import requests

def main():
    if len(sys.argv) != 3:
        print("Usage: python tool_convert.py <input_directory> <output_directory>")
        sys.exit(1)

    input_dir = sys.argv[1]
    output_dir = sys.argv[2]

    if not os.path.isdir(input_dir):
        print(f"Input directory {input_dir} does not exist.")
        sys.exit(1)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for filename in os.listdir(input_dir):
        if filename.endswith('.pdf'):
            pdf_path = os.path.join(input_dir, filename)
            with open(pdf_path, 'rb') as pdf_file:
                response = requests.post('http://127.0.0.1:8070/api/extract', files={'file1': pdf_file}, headers={'Authorization' : 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTcyMjQxMTMzOSwianRpIjoiMGI4MTlhMjUtMjNkYy00YmJjLWE4YTctZWEwNTRkOWQ1ZDNiIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6InRlc3R1c2VyIiwibmJmIjoxNzIyNDExMzM5LCJjc3JmIjoiMGM4ZWQ5YjItMzMyYy00MWU1LWFkOTQtNzY3NzQ3Y2Q4MmY2IiwiZXhwIjoxNzIyNDk3NzM5LCJyb2xlIjoiYWRtaW4ifQ.nRDkMRf8vmG3RBaHkMft8qLoawgSSQmJWFuPykzUvdg'})
                if response.status_code == 200:

                    # parse the json body
                    json_body = response.json()
                    txt = json_body['texts'][0]

                    txt_filename = os.path.splitext(filename)[0] + '.txt'
                    txt_path = os.path.join(output_dir, txt_filename)
                    with open(txt_path, 'w') as txt_file:
                        txt_file.write(txt)
                else:
                    print(f"Failed to convert {filename}: {response.status_code}")

if __name__ == "__main__":
    main()