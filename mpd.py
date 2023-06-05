import xml.etree.ElementTree as ET
import os
import shutil
import requests

def create_directory(path):
    if os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(path)

def get_attribute_value(element, attribute_name):
    if attribute_name in element.attrib:
        return element.attrib[attribute_name]
    else:
        return None

def download_file(url, output_path):
    print(f"\t\tDownloading segment: " + output_path)
    response = requests.get(url)

    if response.status_code == 200:
        with open(output_path, 'wb') as file:
            file.write(response.content)
        print(f"\t\tFile downloaded successfully!")
    elif response.status_code == 404:
        print(f"\t\tFile not found. Skipping...")
    else:
        print(f"\t\tAn error occurred while downloading the file.")

class MPD:
  def __init__(self, out_path, mpd_url):
    self.out_path = out_path
    self.mpd_base_url = mpd_url[:mpd_url.rindex('/')]
    self.mpd_name = mpd_url[mpd_url.rindex('/')+1:]

    # Load the XML file
    tree = ET.parse(self.out_path + "/" + self.mpd_name)
    root = tree.getroot()

    for adaptationSet in root.findall(".//{urn:mpeg:dash:schema:mpd:2011}AdaptationSet"):
        print("\nFound AdaptationSet:")

        # Print list of attributes
        if adaptationSet.attrib:
            for attr, value in adaptationSet.attrib.items():
                print(f"\t{attr}: {value}")

        # Create folder
        mime_type = str(get_attribute_value(adaptationSet, "mimeType")).split("/")[0]
        if "application" in mime_type:
            lang = str(get_attribute_value(adaptationSet, "lang"))
            mime_type += "_" + lang
        create_directory(self.out_path + mime_type)

        # Find the SegmentTemplate element
        segment_template = adaptationSet.find(".//{urn:mpeg:dash:schema:mpd:2011}SegmentTemplate")

        # Extract relevant attributes from SegmentTemplate
        initialization = str(segment_template.get("initialization"))
        media_template = str(segment_template.get("media"))
        timescale = float(segment_template.get("timescale"))

        print(f"\tinitialization: " + initialization)
        print(f"\tmedia_template: " + media_template)
        print(f"\ttimescale: " + str(timescale))

        # Find the SegmentTimeline element
        segment_timeline = segment_template.find(".//{urn:mpeg:dash:schema:mpd:2011}SegmentTimeline")

        # Loop over each segment in the SegmentTimeline and create timeline
        timeline = []
        for s in segment_timeline.findall("{urn:mpeg:dash:schema:mpd:2011}S"):
            time = int(s.get("t"))
            duration = int(s.get("d"))
            repetitions = int(s.get("r", 0)) + 1

            timeline += [time + duration * i for i in range(repetitions)]

        # Create folders for representation and download segments
        for representation in adaptationSet.findall("{urn:mpeg:dash:schema:mpd:2011}Representation"):
            print(f"\tFound Representation:")
            # Print list of attributes
            if representation.attrib:
                for attr, value in representation.attrib.items():
                    print(f"\t\t{attr}: {value}")

            # Create folder
            output_path = self.out_path + mime_type
            if "audio" in mime_type or "video" in mime_type:
                bandwidth = str(get_attribute_value(representation, "bandwidth"))
                output_path += "/" + bandwidth
            create_directory(output_path)

            # Download init segment
            repId = str(get_attribute_value(representation, "id"))
            segment_name = initialization.replace("$RepresentationID$", repId)
            segment_url = self.mpd_base_url + "/" + segment_name

            # Download the init segment file
            download_file(segment_url, output_path + "/" + segment_name)

            # Download media segments
            for time in timeline:
                segment_name = media_template.replace("$RepresentationID$", repId).replace("$Time$", str(time))
                segment_url = self.mpd_base_url + "/" + segment_name

                # Download the media segment file
                download_file(segment_url, output_path + "/" + segment_name)
              