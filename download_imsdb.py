import os.path
import sys
from pprint import pprint

from requests_html import HTMLSession
import json

from tqdm import tqdm

SCRIPT_LIST_URL = "https://imsdb.com/all-scripts.html"
SCRIPT_INFO_URL = "https://imsdb.com/Movie Scripts"

MAIN_URL = "http://www.imsdb.com"
GENRE_URI = "/genre/"
SCRIPT_URI = "/scripts/"

SCRIPT_INFO_CLASS = ".script-details"
SCRIPT_SRC_CLASS = ".scrtext"

SCRIPTS_INFO_FILENAME = "scripts_info.json"

save_path = "./scripts"

session = HTMLSession()
try:
	r = session.get(SCRIPT_LIST_URL)
except:
	sys.exit("failed to get script list")

# get all links on script list page
links = r.html.absolute_links
script_titles = []

# get script names from link urls
for link_url in links:
	if SCRIPT_INFO_URL in link_url:
		# take away script info url and ".html" at end
		script_titles.append(link_url[len(SCRIPT_INFO_URL):-5])

print("found {} scripts, downloading...".format(len(script_titles)))

scripts_info = {}
failed_urls = []

for url_endpoint in tqdm(script_titles):
	pretty_title = url_endpoint.replace(", The Script", "").replace(" Script", "")
	if os.path.exists(save_path + pretty_title + ".txt"):
		continue

	# get info page
	try:
		r_info = session.get(SCRIPT_INFO_URL + url_endpoint + ".html")

		info_links = r_info.html.find(SCRIPT_INFO_CLASS, first=True).links

		# get genres and script url
		genres = []
		script_url = MAIN_URL + SCRIPT_URI + url_endpoint
		for link_url in info_links:
			if GENRE_URI in link_url:
				genres.append(link_url[len(GENRE_URI):])
			elif SCRIPT_URI in link_url:
				script_url = MAIN_URL + link_url

		# get script page
		r_script = session.get(script_url)

		script_src = r_script.html.find(SCRIPT_SRC_CLASS, first=True)

		if script_src is None or script_src.full_text is None:
			continue

		formatted_script = script_src.full_text

		with open(save_path + pretty_title + ".txt", "w") as f:
			f.write(formatted_script)

		# add script info
		scripts_info[pretty_title] = {"filename": pretty_title + ".txt", "genres": genres}
	except:
		failed_urls.append(url_endpoint)

print("done, failed:")
pprint(failed_urls)

# save script info
scripts_info_file = open(save_path + SCRIPTS_INFO_FILENAME, "w")
json.dump(scripts_info, scripts_info_file)
scripts_info_file.close()
