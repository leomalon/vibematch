"""
web_scraper.py

Python script to extract events from a web page.

"""
#Python built-in modules
import time
import random
import json
import requests as rq

#Python third-party modules
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright


# ==========================================
# 1. SCRAPING FUNCTIONS
# ==========================================

def page_scraping(categories:list): 
    """
    Initialize Playwright and start the scraping process for multiple category URLs.

    Parameters
    ----------
    links : list of str
        A list of category URLs to be scraped.

    Returns
    -------
    raw_data: list of dict
        This function returns a list of events with the specified attributes.

    Notes
    -----
    - Uses Playwright to launch a browser instance.
    - Iterates over each link and scrapes its content.
    - Assumes links are valid and reachable URLs.
    """

    raw_data = []

    with sync_playwright() as p:
        
        browser = p.chromium.launch(headless=True)

        context = browser.new_context()
        page = context.new_page()
        
        for category in categories:

            if not category["active"]:
                continue
            
            category_data = {category["category_request"]:[]}

            total_number_pages = int(category["pages"])+1

            for current_page in range(1,total_number_pages):

                #We wait some random time
                time.sleep(random.uniform(2,7))

                # Playwright will pause here until a request matches your condition
                # page.expect_request() returns a special context manager object
                with page.expect_request(lambda req: category["data_api"] in req.url, timeout=60000) as req_info:
                    #We start the navigation
                    page.goto(category["url"], wait_until="domcontentloaded", timeout=60000)

                #Get the entire api url and headers
                request = req_info.value
                api_url = request.url
                headers = dict(request.headers)

                #Build entire headers
                headers = {
                    "accept":"application/json",
                    "accept-encoding":"gzip, deflate, br, zstd",
                    "accept-language":"es-ES,es;q=0.9,en;q=0.8,fr;q=0.7",
                    "authorization":headers["authorization"],
                    "content-type":"application/json",
                    "origin":category["origin"],
                    "priority":"u=1, i",
                    "referer":category["origin"],
                    "sec-ch-ua":headers["sec-ch-ua"],
                    "sec-ch-ua-mobile":headers["sec-ch-ua-mobile"],
                    "sec-ch-ua-platform":headers["sec-ch-ua-platform"],
                    "sec-fetch-dest":"empty",
                    "sec-fetch-mode":"cors",
                    "sec-fetch-site":"same-site",
                    "user-agent":headers["user-agent"],
                }

                #We call the API collected to get the info
                payload = {
                    "categories": [category["category_request"]],
                    "order": "latest",
                    "page":current_page,
                    "size":20
                }

                try:
                    response_category = rq.post(url=api_url,json=payload,headers=headers,timeout=9000)
                except IndexError as e:
                    raise IndexError("Error en la llamada de API") from e
                


                if response_category.status_code in (200,206) and response_category.json()["data"]:

                    events = response_category.json()["data"]["hits"]

                    #Build each event

                    for event in events:

                        event_data = {
                            "id":event["_source"]["activityId"],
                            "url_sufix":event["_source"]["activityUrl"],
                            "category_url":event["_source"]["activityCategory"],
                            "category_spanish":category["nombre"],
                            "location_city":"",
                            "location_street":"",
                            "price":event["_source"]["price"],
                            "currency":event["_source"]["currency"],
                            "title":event["_source"]["title"],
                            "description":"",
                            "date":str(event["_source"]["dateStart"])[0:-8].strip(),
                            "mood":[],
                            "tags":[],

                        }

                        category_data[category["category_request"]].append(event_data)


            raw_data.append(category_data)

        #We close the context for promart
        context.close()
        browser.close()
    
    return raw_data

def event_page_scraping(events:list,origin_page,id_tag):

    def build_event_url(event):
        base_url = origin_page
        full_event_url = base_url + "/events/" + str(event["category_url"]) + "/" +str(event["url_sufix"]) + "-" + str(event["id"])


        return full_event_url


    processed_events = []

    with sync_playwright() as p:
        browser = p.chromium.launch()

        context = browser.new_context()
        page = context.new_page()

        for main_category in events:
            for key in main_category:
                print(key)
                for event in main_category[key]:
                    for i in range(3):
                        try:
                            time.sleep(random.uniform(7,12))

                            page.goto(build_event_url(event),wait_until="domcontentloaded",timeout=10000)

                            html = page.content()

                            soup_object = BeautifulSoup(html, "html.parser")
                            
                            event_complete_data = soup_object.find("script", id=id_tag)

                            if not event_complete_data:
                                break
                            
                            json_str = event_complete_data.text[38:-10]

                            event_json = json.loads(json_str)["activity"]

                            description = event_json["description"]
                            location_city = event_json["city"]
                            location_street =  event_json["address"]
                            category_english = event["category_url"]
                            url_event = build_event_url(event)
                            
                            #Extract tags
                            tags = []
                            for tag in event_json["tags"]:
                                tags.append(tag["name"])

                            processed_events.append({
                                "categoria_ingles":category_english,
                                "categoria_espaniol":event["category_spanish"],
                                "ciudad":location_city,
                                "direccion":location_street,
                                "precio":event["price"],
                                "moneda":event["currency"],
                                "titulo":event["title"],
                                "descripcion":description,
                                "mood":[],
                                "tags":tags,
                                "url_evento":url_event
                            })
                            print(processed_events[-1])
                            break

                        except Exception as e:
                            print(f"Retry {i+1}/3 failed: {e}")
                            time.sleep(2)
        context.close()
        browser.close()
    
    return processed_events



