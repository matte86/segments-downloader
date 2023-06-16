import os
import requests
from urllib.parse import urljoin, urlparse

def download_hls_master_playlist(master_url, output_dir):
    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Fetch the master playlist file
    response = requests.get(master_url)
    response.raise_for_status()
    master_playlist_content = response.text

    # Save the master playlist
    master_playlist_filename = os.path.join(output_dir, "master_playlist.m3u8")
    with open(master_playlist_filename, 'w') as f:
        f.write(master_playlist_content)

    # Parse the master playlist and extract stream playlists
    stream_playlists = []
    stream_folders = []
    lines = master_playlist_content.splitlines()
    for line in lines:
        if "#EXT-X-MEDIA:TYPE=AUDIO" in line:
            # Audio stream playlists are handled a bit differently
            relative_url = line.split("URI=")[1].replace('"', '').replace("'", '')
            stream_playlist_url = urljoin(master_url, relative_url)
            stream_playlists.append(stream_playlist_url)
            stream_folders.append(relative_url.replace("/","_").replace(".","_"))
            continue
        if not line.startswith('#'):
            # These are the Variant Streams for the different renditions
            relative_url = line.strip()
            stream_playlist_url = urljoin(master_url, relative_url)
            stream_playlists.append(stream_playlist_url)
            stream_folders.append(relative_url.replace("/","_").replace(".","_"))

    # Download each stream playlist and its media segments
    for i, stream_playlist_url in enumerate(stream_playlists):
        stream_output_dir = os.path.join(output_dir, stream_folders[i])
        os.makedirs(stream_output_dir, exist_ok=True)
        download_hls_stream(stream_playlist_url, stream_output_dir)

    print("All streams downloaded successfully.")

def download_hls_stream(stream_url, output_dir):
    # Fetch the stream playlist file
    response = requests.get(stream_url)
    response.raise_for_status()
    stream_playlist_content = response.text

    # Save the stream playlist
    stream_playlist_filename = os.path.join(output_dir, "stream_playlist.m3u8")
    with open(stream_playlist_filename, 'w') as f:
        f.write(stream_playlist_content)

    # Parse the stream playlist and extract segment URLs
    segment_urls = []
    lines = stream_playlist_content.splitlines()
    for line in lines:
        if "#EXT-X-MAP:URI=" in line:
            # This is the init segment
            init_segment = line.split("=")[1].replace('"', '').replace("'", '')
            init_segment_url = urljoin(stream_url, init_segment)
            segment_urls.append(init_segment_url)
            continue
        if line.startswith('#'):
            continue
        segment_url = urljoin(stream_url, line.strip())
        segment_urls.append(segment_url)

    # Download each segment
    for i, segment_url in enumerate(segment_urls):
        response = requests.get(segment_url)
        response.raise_for_status()
        file_name = urlparse(segment_url).path.split("/")[-1]
        segment_filename = os.path.join(output_dir, file_name)
        with open(segment_filename, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded segment {i+1}/{len(segment_urls)} in {output_dir}")

    print(f"All segments downloaded successfully for {output_dir}.")

class M3U8:
  def __init__(self, out_path, master_playlist_url):
    self.out_path = out_path
    self.master_playlist_url = master_playlist_url

    download_hls_master_playlist(self.master_playlist_url, self.out_path)
