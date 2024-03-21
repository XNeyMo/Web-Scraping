import re
import html
import requests
from bs4 import BeautifulSoup

class Reading:
    def __init__(self, category, title, content):
        self.category = category
        self.title = title
        self.content = content

categories_url = 'https://www.despertarsabiendo.com/categorias'
categories_result = requests.get(categories_url)
categories_content = categories_result.text

categories_pattern = r'https://despertarsabiendo.com/category/[\w-]*'
categories_links = re.findall(categories_pattern, str(categories_content))

readings = []
counter = 0

for category_link in categories_links:
    category_result = requests.get(category_link)
    category_content = category_result.text

    page_numbers_pattern = r'<span class="elementor-screen-only">Página<\/span>(\d+)'
    page_numbers = re.findall(page_numbers_pattern, category_content)

    if not page_numbers:
        break

    category_name = category_link.replace('https://despertarsabiendo.com/category/', '')
    category_parts = category_name.split("-")
    category = " ".join(part.capitalize() for part in category_parts)

    page_numbers_to_int = [int(number) for number in page_numbers]
    page_max = max(page_numbers_to_int)

    link_to_title = category_link.replace('https://despertarsabiendo.com/category/', 'https://www.despertarsabiendo.com/')

    for number in range(1, page_max + 1):
        page = f'{category_link}/page/{number}'
        page_result = requests.get(page)
        page_content = page_result.text

        titles_page_pattern = fr'{link_to_title}/[\w-]*'
        all_titles_page_links = re.findall(titles_page_pattern, str(page_content))
        titles_page_links_no_duplicates = list(set(all_titles_page_links))

        for title_page_link in titles_page_links_no_duplicates:
            title_page_result = requests.get(title_page_link)
            title_page_content = title_page_result.text

            soup = BeautifulSoup(title_page_content, 'html.parser')

            title_pattern = r'<div class="elementor-element elementor-element-.*? elementor-widget elementor-widget-theme-post-title elementor-page-title elementor-widget-heading".*?>\s*<div class="elementor-widget-container">\s*<h2 class="elementor-heading-title elementor-size-default">(.*?)</h2>\s*</div>\s*</div>'
            title = html.unescape(re.findall(title_pattern, str(title_page_content))[0])

            sections = soup.find_all('div', class_="elementor-widget-container")

            html_content = []

            for section in sections:
                section_paragraphs = section.find_all('p', class_=False)

                for paragraph in section_paragraphs:
                    html_content.append(paragraph)

            content = [p.get_text() for p in html_content]
            content = '\n'.join(content)

            new_reading = Reading(category, title, content)
            readings.append(new_reading)

    counter += 1

for reading in readings:
    print(f'{reading.category} - {reading.title}')
