import requests
import json
from bs4 import BeautifulSoup

class Crawler:
    def get_html(self, url):
        try:
            response = requests.get(url)

            if response.status_code == 200:
                return response.text
            else:
                print(f'Failed to retrieve HTML. Status code: {response.status_code}')
                return None
        except Exception as e:
            print(f'An error occurred: {str(e)}')
            return None

    def parse_page(self, url, urls):
        page_data = {}
        page_data['page_url'] = url

        html = self.get_html(url)

        if html == None:
            print('Unable to get the content of the page!')
            return

        soup = BeautifulSoup(html, 'html.parser')
        root = soup.find('div')

        page_data['contents'] = {}

        if 'sections-page' in root['class']:
            sections = []

            for h in root.find_all(class_='section-name'):
                section = {}
                section['name'] = h.find('a').text[2:]
                section['href'] = h.find('a')['href']
                
                urls.append(section['href'])

                sections.append(section)

            page_data['contents']['sectons_refs'] = sections
        elif 'simple-section-page' in root['class']:
            page_data['contents']['message'] = root.find('p').text
        elif 'catalog-page' in root['class']:
            products = []

            for div in root.find_all('div'):
                product = {}
                product['name'] = div.find('a').text
                product['href'] = div.find('a')['href']

                urls.append(product['href'])

                products.append(product)

            page_data['contents']['products-refs'] = products
        elif 'product-page' in root['class']:
            product = {}

            keys = root.find_all(class_='key')
            values = root.find_all(class_='value')

            for i in range(len(keys)):
                product[keys[i].text] = values[i].text

            page_data['contents']['product_info'] = product

        return page_data

    def parse_website(self, urls, data):
        pages = []

        while(len(urls) > 0):
            pages.append(self.parse_page(urls[0], urls))
            urls.pop(0)

        data['pages'] = pages

if __name__ == '__main__':
    crawler = Crawler()
    urls = ['http://127.0.0.1:8080/']
    data = {}
    crawler.parse_website(urls, data)

    with open("contents.json", "w") as json_file:
        json.dump(data, json_file, indent=4)