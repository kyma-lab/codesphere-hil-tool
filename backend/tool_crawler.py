import requests
import xml.etree.ElementTree as ET
from zipfile import ZipFile
from io import BytesIO
import json
from bs4 import BeautifulSoup  #


def extract_full_content(element):
    # Recursively concatenate text content of the element and its children
    content = ""
    for child in element:
        content += extract_full_content(child)
    if element.text:
        content += element.text
    return content


def clean_html(content):
    soup = BeautifulSoup(content, "html.parser")
    return soup.get_text()


def crawl_laws(xml_url):
    # Send a GET request to the URL and get the XML content
    response = requests.get(xml_url)
    if response.status_code == 200:
        # Parse the XML content
        root = ET.fromstring(response.content)

        # Initialize a list to store information for each item
        items_data = []

        # Iterate through each 'item' in the XML
        for item in root.findall(".//item"):
            try:
                # Extract title and link
                title = item.find("title").text.strip()
                zip_link = item.find("link").text.strip()

                # Strip the last part from the link
                link_stripped = zip_link.rsplit("/", 1)[0]

                # Print or store title and link
                print(f"Title: {title}")
                print(f"ZIP Link: {zip_link}")

                # Send a GET request to the ZIP file URL
                zip_response = requests.get(zip_link)
                if zip_response.status_code == 200:
                    try:
                        # Extract XML content from the ZIP file
                        with ZipFile(BytesIO(zip_response.content)) as zip_file:
                            # Find XML files in the ZIP archive
                            xml_file_names = [
                                name
                                for name in zip_file.namelist()
                                if name.endswith(".xml")
                            ]
                            if not xml_file_names:
                                raise ValueError(
                                    "Im ZIP-Archiv wurden keine XML-Dateien gefunden"
                                )

                            # Assuming there's only one XML file in the ZIP (you may need to handle multiple files differently)
                            xml_file_name = xml_file_names[0]

                            xml_content = zip_file.read(xml_file_name).decode("utf-8")

                        # Parse the law XML content
                        law_root = ET.fromstring(xml_content)

                        # Initialize a list to store information for each norm
                        norms_data = []

                        # Find all 'norm' elements
                        for norm in law_root.findall(".//norm"):
                            try:
                                # Extract relevant information
                                jurabk_element = norm.find("./metadaten/jurabk")
                                enbez_element = norm.find("./metadaten/enbez")
                                title_element = norm.find("./metadaten/titel")
                                content_element = norm.find("./textdaten/text/Content")

                                content = (
                                    extract_full_content(content_element)
                                    if content_element is not None
                                    else ""
                                )
                                print(content)
                                # Check if elements are not None before accessing their text attribute
                                jurabk = (
                                    jurabk_element.text.strip()
                                    if jurabk_element is not None
                                    else "N/A"
                                )

                                # Check if enbez_element is not None before accessing its text attribute
                                enbez = (
                                    enbez_element.text.strip()
                                    if enbez_element is not None
                                    else "N/A"
                                )

                                # Check if title_element is not None before accessing its text attribute
                                title_norm = (
                                    title_element.text.strip()
                                    if title_element is not None
                                    else "N/A"
                                )
                                # Store the information for the norm in a dictionary
                                norm_data = {
                                    "jurabk": jurabk,
                                    "enbez": enbez,
                                    "title": title_norm,
                                    "content": content,
                                    "link": link_stripped,  # Use the stripped link
                                }

                                # Append the norm data to the list of norms
                                if content != "":
                                    norms_data.append(norm_data)
                            except Exception as e:
                                print(f"Fehlerverarbeitungsnorm: {e}")

                        # Append the item data with norms to the list of items
                        item_data = {
                            "title": title,
                            "link": link_stripped,  # Use the stripped link
                            "norms": norms_data,
                        }
                        items_data.append(item_data)
                    except (ET.ParseError, Exception) as e:
                        print(f"Fehler beim Umgang mit der ZIP-Datei: {e}")

                else:
                    print(
                        f"Der Inhalt der ZIP-Datei konnte nicht abgerufen werden. Statuscode: {zip_response.status_code}"
                    )

            except Exception as e:
                print(f"Fehler beim Bearbeiten des Artikels: {e}")
        # Convert the list of items to JSON
        json_data = clean_html(json.dumps(items_data, indent=2))
        print(clean_html(json_data))
        # Write the JSON data to a file
        with open("final_laws_from_xml.json", "w", encoding="utf-8") as json_file:
            json_file.write(json_data)

        print("\nJSON Data has been written to 'final_laws_from_xml.json'.")

    else:
        print(f"XML-Inhalt konnte nicht abgerufen werden. Statuscode: {response.status_code}")


if __name__ == "__main__":
    xml_url = "https://www.gesetze-im-internet.de/gii-toc.xml"
    crawl_laws(xml_url)
    # Load your original JSON data
    with open("final_laws_from_xml.json", "r", encoding="utf-8") as file:
        original_data = json.load(file)

    # Extract norms from each element
    norms_data = []
    for element in original_data:
        norms_data.extend(element.get("norms", []))

    # Create a new JSON structure with just the norms
    new_json_data = {"norms": norms_data}

    # Write the new JSON data to a file
    with open("norms_only.json", "w", encoding="utf-8") as new_file:
        json.dump(new_json_data, new_file, ensure_ascii=False, indent=2)

    print("Neue JSON-Datei mit nur erstellten Normen: norms_only.json")
