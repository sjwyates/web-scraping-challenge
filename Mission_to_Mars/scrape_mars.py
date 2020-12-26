from splinter import Browser
from bs4 import BeautifulSoup as bs
import pandas as pd
import requests
import time
from webdriver_manager.chrome import ChromeDriverManager


def init_browser():
    executable_path = {'executable_path': ChromeDriverManager().install()}
    return Browser('chrome', **executable_path, headless=False)


def scrape_info():
    # oh the places you'll go...
    urls = {
        'nasa_news': 'https://mars.nasa.gov/news/',
        'nasa_jpl': { 'base': 'https://www.jpl.nasa.gov', 'query': '/spaceimages/?search=&category=Mars' },
        'mars_facts': 'https://space-facts.com/mars/',
        'astrogeology': { 'base': 'https://astrogeology.usgs.gov', 'query': '/search/results?q=hemisphere+enhanced&k1=target&v1=Mars' }
    }

    # helper function
    def visit_wait_return(url, wait):
        browser.visit(url)
        time.sleep(wait)
        html = browser.html
        return bs(html, 'html.parser')

    # open up a browser (to be used for everything)
    browser = init_browser()

    # first visit
    nasa_news_soup = visit_wait_return(urls['nasa_news'], 3)
    articles = nasa_news_soup.find_all('div', class_='image_and_description_container')
    article_1_title = articles[0].find('h3').get_text(strip=True)
    article_1_text = articles[0].find('div', class_='article_teaser_body').get_text(strip=True)

    # second visit
    nasa_jpl_soup = visit_wait_return(urls['nasa_jpl']['base'] + urls['nasa_jpl']['query'], 3)
    featured_img_url = urls['nasa_jpl']['base'] + nasa_jpl_soup.find('article', class_='carousel_item').attrs['style'].split("'")[1]

    # third visit
    mars_facts_df = pd.DataFrame(pd.read_html(urls['mars_facts'])[0]).rename(columns={0: 'Description', 1: 'Mars'})
    mars_facts_html = mars_facts_df.to_html(index=False, classes="table is-bordered is-striped is-hoverable is-full-width", justify="inherit")

    # fourth visit
    astrogeology_soup = visit_wait_return(urls['astrogeology']['base'] + urls['astrogeology']['query'], 1)
    items = astrogeology_soup.find_all('div', class_='item')
    links_to_results = []
    for item in items:
        link = item.find('a', class_='itemLink product-item')['href']
        title = item.find('h3').get_text(strip=True)
        links_to_results.append({ 'link': link, 'title': title })
    links_to_images = []
    for link in links_to_results:
        this_page_soup = visit_wait_return(urls['astrogeology']['base'] + link['link'], 0)
        img_url = this_page_soup.find('img', class_='wide-image')['src']
        links_to_images.append({ 'title': link['title'], 'img_url': urls['astrogeology']['base'] + img_url })

    browser.quit()

    return {
        'nasa_news': {
            'title': article_1_title,
            'text': article_1_text
        },
        'nasa_jpl': {
            'featured_img_url': featured_img_url,
        },
        'mars_facts': {
            'html': mars_facts_html
        },
        'astrogeology': {
            'img_urls': links_to_images
        }
    }