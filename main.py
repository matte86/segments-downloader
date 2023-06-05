import argparse
import wget
import os
from mpd import MPD

def main():
    parser = argparse.ArgumentParser(
        description='DASH Segments Downloader')
    parser.add_argument('-m', '--mpd', dest='mpd_url', help="URL for DASH MPD", required=True)
    parser.add_argument('-o', '--output', dest='out_path', help="Output folder", required=True)
    args = parser.parse_args()

    mpd_name = args.mpd_url[args.mpd_url.rindex('/')+1:]
    if os.path.exists(args.out_path + mpd_name):
        os.remove(args.out_path + "/" + mpd_name) # if exist, remove it directly

    wget.download(args.mpd_url, args.out_path)

    mpd = MPD(args.out_path, args.mpd_url)

if __name__ == "__main__":
    main()
