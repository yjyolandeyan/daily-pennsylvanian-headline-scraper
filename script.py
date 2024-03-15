"""
Scrapes a headline from The Daily Pennsylvanian website and saves it to a 
JSON file that tracks headlines over time.
"""

import os
import sys

import daily_event_monitor

import bs4
import requests
import loguru


def scrape_data_point():
    """
    Scrapes the main headline from The Daily Pennsylvanian home page.

    Returns:
        str: The headline text if found, otherwise an empty string.
    """
    # req = requests.get("https://www.thedp.com")
    # loguru.logger.info(f"Request URL: {req.url}")
    # loguru.logger.info(f"Request status code: {req.status_code}")

    # if req.ok:
    #     soup = bs4.BeautifulSoup(req.text, "html.parser")
    #     target_element = soup.find("a", class_="frontpage-link")
    #     data_point = "" if target_element is None else target_element.text
    #     loguru.logger.info(f"Data point: {data_point}")
    #     return data_point

    req = requests.get("https://www.thedp.com")
    loguru.logger.info(f"Request URL: {req.url}")
    loguru.logger.info(f"Request status code: {req.status_code}")
    headlines = {'Main': '', 'News': '', 'Sports': '', 'Opinion': '', 'Multimedia': ''}
    
    if req.ok:
        soup = bs4.BeautifulSoup(req.text, "html.parser")
        # Scrape the main headline
        main_headline_element = soup.find("a", class_="frontpage-link")
        if main_headline_element:
            headlines['Main'] = main_headline_element.get_text(strip=True)
            
        # Scrape the news headline
            news_headline_element = soup.select_one("div.col-sm-6.section-news a.frontpage-link")
            if news_headline_element:
                headlines['News'] = news_headline_element.get_text(strip=True)

        # Scrape the sports headline
        sports_section = soup.find('h3', class_='frontpage-section', text='Sports')
        if sports_section:
            sports_headline_element = sports_section.find_next_sibling('div', class_='article-summary').find('a', class_='frontpage-link')
            if sports_headline_element:
                headlines['Sports'] = sports_headline_element.get_text(strip=True)
                    
        # Scrape the opinion headline
        opinion_section = soup.find('h3', class_='frontpage-section', text='Opinion')
        if opinion_section:
            opinion_headline_element = opinion_section.find_next_sibling('div', class_='article-summary').find('a', class_='frontpage-link')
            if opinion_headline_element:
                headlines['Opinion'] = opinion_headline_element.get_text(strip=True)

        # Scrape the multimedia headline
        multimedia_headline_element = soup.select_one("div.section-multimedia h3.frontpage-section a.medium-link")
            if multimedia_headline_element:
                headlines['Multimedia'] = multimedia_headline_element.get_text(strip=True)
        
        loguru.logger.info(f"Scraped headlines: {headlines}")
    return headlines

if __name__ == "__main__":

    # Setup logger to track runtime
    loguru.logger.add("scrape.log", rotation="1 day")

    # Create data dir if needed
    loguru.logger.info("Creating data directory if it does not exist")
    try:
        os.makedirs("data", exist_ok=True)
    except Exception as e:
        loguru.logger.error(f"Failed to create data directory: {e}")
        sys.exit(1)

    # Load daily event monitor
    loguru.logger.info("Loading daily event monitor")
    dem = daily_event_monitor.DailyEventMonitor(
        "data/daily_pennsylvanian_headlines.json"
    )

    # Run scrape
    loguru.logger.info("Starting scrape")
    try:
        data_point = scrape_data_point()
    except Exception as e:
        loguru.logger.error(f"Failed to scrape data point: {e}")
        data_point = None

    # Save data
    if data_point is not None:
        dem.add_today(data_point)
        dem.save()
        loguru.logger.info("Saved daily event monitor")

    def print_tree(directory, ignore_dirs=[".git", "__pycache__"]):
        loguru.logger.info(f"Printing tree of files/dirs at {directory}")
        for root, dirs, files in os.walk(directory):
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            level = root.replace(directory, "").count(os.sep)
            indent = " " * 4 * (level)
            loguru.logger.info(f"{indent}+--{os.path.basename(root)}/")
            sub_indent = " " * 4 * (level + 1)
            for file in files:
                loguru.logger.info(f"{sub_indent}+--{file}")

    print_tree(os.getcwd())

    loguru.logger.info("Printing contents of data file {}".format(dem.file_path))
    with open(dem.file_path, "r") as f:
        loguru.logger.info(f.read())

    # Finish
    loguru.logger.info("Scrape complete")
    loguru.logger.info("Exiting")
