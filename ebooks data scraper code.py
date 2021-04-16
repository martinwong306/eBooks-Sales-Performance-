import requests
import time
import csv
import re
from bs4 import BeautifulSoup
from datetime import datetime


def write_to_csv(list_input):
    # The scraped info will be written to a CSV here.
    try:
        with open("kobo_books_more.csv", "a") as fopen:  # Open the csv file.
            csv_writer = csv.writer(fopen)
            csv_writer.writerow(list_input)
    except:
        return False
    
    
def scrape(source_url, soup):  # Takes the driver and the subdomain for concats as params
    # Find the elements of the article tag
    books = soup.find_all("div", class_="item-detail")

    # Iterate over each book article tag
    for each_book in books:
        info_url = source_url+"/"+each_book.find("a", class_='item-link-underlay')["href"]
        time.sleep(3)
        info_response = requests.get(info_url).text
        info_soup = BeautifulSoup(info_response, 'html.parser')

        title = info_soup.find('h2', 'title product-field').text.strip()
        author = info_soup.find('a', 'contributor-name').text.strip()
        rating = " ".join(list(info_soup.find('ul', 'category-rankings').stripped_strings))
        price = info_soup.find('div', class_='price-wrapper').text.strip().replace('\n\xa0CAD', '')
        available_date = info_soup.find('p', 'preorder-subtitle').text.strip()
        extract_date = datetime.today().strftime('%Y-%m-%d') 

        # Invoke the write_to_csv function
        write_to_csv([title, author, rating, price, available_date, extract_date])

def browse_and_scrape(seed_url, page_number=1):
    # Fetch the URL - We will be using this to append to images and info routes
    url_pat = re.compile(r"(https://www.*\.com)")
    source_url = url_pat.search(seed_url).group(0)

   # Page_number from the argument gets formatted in the URL & Fetched
    formatted_url = seed_url.format(str(page_number))

    try:
        html_text = requests.get(formatted_url).text
        # Prepare the soup
        soup = BeautifulSoup(html_text, "html.parser")
        print(f"Now Scraping - {formatted_url}")

        # This if clause stops the script when it hits an empty page
        if soup.find("a", class_="next") != None:
            scrape(source_url, soup)     # Invoke the scrape function
            # Be responsible by waiting before you hit again
            time.sleep(3)
            page_number += 1
            # Recursively invoke the same function with the increment
            browse_and_scrape(seed_url, page_number)
        else:
            scrape(source_url, soup)     # The script exits here
            return True
        return True
    except Exception as e:
        return e

if __name__ == "__main__":
    seed_url = "https://www.kobo.com//ca/en/list/popular-ebook-pre-orders/Rf1blLYRCU6GSugDQOD6Yg?pageNumber={}"
    print("Web scraping has begun")
    result = browse_and_scrape(seed_url)
    if result == True:
        print("Web scraping is now complete!")
    else:
        print(f"Oops, That doesn't seem right!!! - {result}")
