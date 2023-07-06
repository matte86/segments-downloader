import os
import requests
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom

class ISML:
    def __init__(self, out_path, manifest_url, num_segments):
        self.out_path = out_path
        self.manifest_url = manifest_url
        self.num_segments = num_segments

        self.download_segments_and_manifest()
    
    def compute_segment_start_times(self, c_elements):
        start_times = []
        current_start_time = int(c_elements[0].get("t"))
        
        for c_element in c_elements:
            start_times.append(current_start_time)
            duration = int(c_element.get("d"))
            current_start_time += duration
        
        return start_times

    def write_xml_to_file(self, root, output_file):
        # Create a string buffer to hold the XML content
        xml_content = ET.tostring(root, encoding="utf-8")
        
        # Parse the XML content with minidom for pretty-printing
        parsed_xml = minidom.parseString(xml_content)
        
        # Format the parsed XML with indentation and newlines
        formatted_xml = parsed_xml.toprettyxml(indent="  ")
        
        # Write the formatted XML to the output file
        with open(output_file, "w") as file:
            file.write(formatted_xml)

    def download_segments_and_manifest(self):
        # Create the output directory if it doesn't exist
        os.makedirs(self.out_path, exist_ok=True)
        
        # Send a GET request to retrieve the manifest file
        manifest_response = requests.get(self.manifest_url)
        
        # Check if the request was successful
        if manifest_response.status_code != 200:
            print("Failed to retrieve the manifest file.")
            return
        
        # Parse the manifest content as XML
        manifest_content = manifest_response.content.decode("utf-8")
        manifest_root = ET.fromstring(manifest_content)
        
        # Save the manifest to a file
        manifest_filename = "manifest.ism"
        manifest_output_path = self.out_path + "/" + manifest_filename
        self.write_xml_to_file(manifest_root, manifest_output_path)
        
        print(f"Downloaded manifest: {manifest_filename}")

        # Find all StreamIndex elements in the manifest
        stream_indexes = manifest_root.findall(".//StreamIndex")
        
        # Download media segments for each StreamIndex
        for stream_index in stream_indexes:
            # Get the StreamIndex attributes
            stream_index_url = stream_index.get("Url")
            stream_name = stream_index.get("Name")

            print(f"Downloading stream: {stream_index_url}")
            
            # Find all QualityLevel elements within the StreamIndex
            quality_levels = stream_index.findall(".//QualityLevel")
            
            # Download media segments for each QualityLevel
            for quality_level in quality_levels:
                # Get the QualityLevel attributes
                bitrate = quality_level.get("Bitrate")
                
                print(f"Downloading segments for quality: {bitrate}")
                
                # Build media segments timeline
                timestamps = self.compute_segment_start_times(stream_index.findall(".//c"))
                
                # Download each media segment
                idx = 1
                for timestamp in timestamps:
                    # Construct the full URL for the segment
                    segment_name = stream_index_url.replace("{bitrate}", bitrate).replace("{start time}", str(timestamp))
                    full_url = self.manifest_url[:self.manifest_url.rindex("/") + 1] + segment_name
                    
                    # Send a GET request to download the segment
                    segment_response = requests.get(full_url)
                    
                    # Check if the request was successful
                    if segment_response.status_code != 200:
                        print(f"Failed to download segment: {timestamp}")
                        continue
                    
                    # Save the segment to a file
                    output_path = self.out_path + f"/{stream_name}/{bitrate}/"
                    os.makedirs(output_path, exist_ok=True)
                    
                    with open(output_path + str(timestamp), "wb") as file:
                        file.write(segment_response.content)
                    
                    print(f"Downloaded segment: {timestamp}")

                    if idx >= self.num_segments:
                        break
                    idx += 1
