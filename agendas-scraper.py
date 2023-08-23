import csv
import glob
import re
import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from sys import stderr, exit
from weasyprint import HTML

CSV = "./agendas.csv"
BASE_URL = "https://www.iab.org/"


def save_content(url, filename):
    """Save content as markdown. If image is present, save the PDF as well."""

    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    # clean up content
    jump_links = soup.find_all("a", {"class": "mw-jump-link"})
    for jump_link in jump_links:
        jump_link.decompose()
    jump_nav = soup.find("div", {"id": "jump-to-nav"})
    if jump_nav:
        jump_nav.decompose()
    noprints = soup.find_all("div", {"class": "noprint"})
    for noprint in noprints:
        noprint.decompose()
    print_footer = soup.find('div', {'class': 'printfooter'})
    if print_footer:
        print_footer.decompose()

    # find the main content of the page
    main_content = soup.find("div", {"id": "content"})

    # save markdown
    markdown = md(str(main_content))

    # write to markdown file
    with open(f"{filename}.md", "w") as file:
        file.write(markdown)
        print(f"saved to {filename}.md")

    # check if images are present
    if len(main_content.find_all("img")) > 0:
        # save PDF file
        style = "<style>img { max-width: 100%; }</style>"
        html = f"<html><head>{style}</head><body>{main_content}</body></html>"
        HTML(string=html, base_url=BASE_URL).write_pdf(f"{filename}.pdf")
        print(f"saved to {filename}.pdf")


with open(CSV, newline="") as csvfile:
    reader = csv.reader(csvfile, delimiter=",")

    # ignore header
    next(reader)

    # go through agendas
    for row in reader:
        date = row[0]
        match = re.search(r"\d{4}-\d{2}-\d{2}", date)
        if match:
            date = match.group()
        else:
            stderr.write(f"Can not determine meeting date from {row[0]}")
            exit(1)

        increment = 0
        original_date = date
        while glob.glob(f"{date}.*"):
            increment += 1
            date = f"{original_date}-{increment}"

        print(f"processing agenda on {date}")

        url = row[1]
        save_content(url, date)
