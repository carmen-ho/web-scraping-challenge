# import libraries
from splinter import Browser
from bs4 import BeautifulSoup as bs
import pandas as pd
from webdriver_manager.chrome import ChromeDriverManager

def scrape():

    # Set up Splinter
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=False)

    news_title, news_p = news(browser)

    mars_data = {
        "news_title": news_title,
        "news_paragraph": news_p,
        "featured_image": featured_image(browser),
        "facts_data": facts_data(),
        "hemisphere": hemisphere(browser)     
    }   

    browser.quit()
    return mars_data

def news(browser):
    #open browser in chrome
    url = "https://mars.nasa.gov/news/?page=0&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest"
    browser.visit(url)

    #convert html to soup object
    html = browser.html
    mars_news_soup = bs(html, "html.parser")

    #find content box and title
    box = mars_news_soup.select_one("div.list_text")
    news_title = box.find("div", class_="content_title").get_text()

    #get text of news article
    news_p = box.find("div", class_="article_teaser_body").get_text()
    return news_title, news_p

def featured_image(browser):

    #set up url for featured image
    featured_url = "https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/index.html"
    browser.visit(featured_url)

    #set up featured button to click for full image
    featured_button = browser.find_by_css("button.btn.btn-outline-light")
    featured_button.click()

    #parse through html for the image soup
    html = browser.html
    featured_image_soup = bs(html, "html.parser")

    #create relative path
    image_url = featured_image_soup.find("img", class_="fancybox-image").get("src")
  

    #create actual path
    featured_image_url = "https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/" + image_url
    return featured_image_url

def facts_data():

    #open browser in chrome
    #mars_url = "https://space-facts.com/mars/"
    #browser.visit(mars_url)

    #read html file in panda and get first table
    mars_fact = pd.read_html("https://space-facts.com/mars/")[0]
    

    mars_fact = mars_fact.rename(columns={0:"Description", 1:"Data"})
    

    mars_fact.set_index("Description",inplace=True)

    return mars_fact.to_html()

def hemisphere(browser):

    #open browser in chrome
    marshem_url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    browser.visit(marshem_url)

    hemisphere_image_urls = []

    hemisphere_list = browser.find_by_css("div.description a.itemLink.product-item")

    for i in range(len(hemisphere_list)):
        hem_dict = {}
        browser.find_by_css("div.description a.itemLink.product-item")[i].click()
        hem_dict["title"] = browser.find_by_css("h2.title").text
        hem_sample_button = browser.find_by_text("Sample")
        hem_sample_button.click()
        hem_dict["img_url"] = hem_sample_button['href']
        hemisphere_image_urls.append(hem_dict)
        browser.back()

    return hemisphere_image_urls

if __name__ == "__main__":

    print(scrape())
