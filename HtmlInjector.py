from bs4 import BeautifulSoup as Soup
from xml.etree import ElementTree as ET

import json
import logging
import sys

logger = logging.getLogger(__name__)
logging.basicConfig()
logger.setLevel(logging.INFO)


def read_config():
	try:
		with open("config.json") as config:
			return json.load(config)
	except FileNotFoundError:
		logging.error("Config file not found! Aborting!")
		sys.exit(1)


def generate_html():
	config_data = read_config()
	generated_html = {}
	for key in config_data:
		example_div = ET.Element("div", attrib={"id": "dynamic"})
		example_p = ET.Element("p")
		example_p.text = config_data[key]

		example_div.append(example_p)

		generated_html[key] = ET.tostring(example_div, encoding="unicode", method="html")

	return generated_html


def insert_html(generated_html):
	with open("web/index.html", "r") as file:
		main_soup = Soup(file.read(), "html.parser")

	div = main_soup.find("div")

	for key in generated_html:
		generated_html[key] = Soup(generated_html[key], "html.parser")
		div.append(generated_html[key])

	with open("web/index.html", "w") as file:
		file.write(main_soup.prettify())


def remove_html():
	with open("web/index.html", "r") as file:
		soup = Soup(file.read(), "html.parser")

	[x.extract() for x in soup.find_all("div", {"id": "dynamic"})]

	with open("web/index.html", "w") as file:
		file.write(soup.prettify())
