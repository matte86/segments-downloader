import argparse
from dash import MPD
from hls import M3U8
from mss import ISML

def main():
    parser = argparse.ArgumentParser(description='Segments Downloader')
    parser.add_argument('-u', '--url', dest='manifest_url', help="URL of the DASH or HLS manifest", required=True)
    parser.add_argument('-o', '--output', dest='out_path', help="Output folder", required=True)
    parser.add_argument('-n', '--num_segments', dest='num_segments', help="Max number of segments to be downloaded", required=True)
    args = parser.parse_args()

    manifest_name = args.manifest_url[args.manifest_url.rindex('/')+1:]
    
    if ".m3u8" in manifest_name:
        M3U8(args.out_path, args.manifest_url, int(args.num_segments))
    elif ".mpd" in manifest_name:
        MPD(args.out_path, args.manifest_url, int(args.num_segments))
    elif ".isml" in args.manifest_url:
        ISML(args.out_path, args.manifest_url, int(args.num_segments))

if __name__ == "__main__":
    main()
