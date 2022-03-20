import argparse
import os
from polls import check_files, get_files, get_links, baseDir, merge_data, process_data

### ARGPARSE ###
parser = argparse.ArgumentParser(prog='Bundestag Scraper')
parser.add_argument("-f", "--force", action='store_true',  help="force get links")
args = parser.parse_args()
### END ARGPARSE ###

if args.force:
    print("Getting Links...")
    get_links()

print("Checking Filesystem")
if not os.path.exists(baseDir + "/out/files"):  # download all files
    if not os.path.exists(f'{baseDir}out/polls_urls.txt'):  # check links exist
        get_links()
    get_files()

check_files()  # check files are in sync with links

print("Merge Data")
merge_data()  # merge xlsx files

print("Process Data")
process_data()  # process data

print("Done!")
