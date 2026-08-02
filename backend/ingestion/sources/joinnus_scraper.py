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

#Utility modules
from backend.ingestion.sources.utilities import clean, extract_date_hour


class JoinnusScraper():

    def __init__(self,origin,categories:list,id_tag,static_tag):
        self.origin = origin
        self.categories = categories
        self.id_tag = id_tag
        self.static_tag = static_tag

    def scrape_webpage(self):
 
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
            
            browser = p.chromium.launch(headless=False)

            context = browser.new_context()
            page = context.new_page()
            
            for category in self.categories:

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
                                "currency":event["_source"]["currency"],
                                "title":event["_source"]["title"],
                                "description":"",
                                "mood":[],
                                "tags":[],

                            }

                            category_data[category["category_request"]].append(event_data)


                raw_data.append(category_data)

            #We close the context for promart
            context.close()
            browser.close()
        
        return raw_data

    def scrape_events(self,events):

        total_events = []
        
        def build_event_url(event):
            base_url = self.origin
            full_event_url = base_url + "/events/" + str(event["category_url"]) + "/" +str(event["url_sufix"]) + "-" + str(event["id"])

            return full_event_url

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)

            context = browser.new_context()
            page = context.new_page()

            for main_category in events:
                for key in main_category:
                    category_events=[]
                    print(key)
                    for event in main_category[key]:
                        for i in range(3):
                            try:
                                time.sleep(random.uniform(7,12))

                                page.goto(build_event_url(event),wait_until="domcontentloaded",timeout=10000)

                                html = page.content()

                                soup_object = BeautifulSoup(html, "html.parser")
                                
                                event_complete_data = soup_object.find("script", id=self.id_tag)
                                aditional_event_data = soup_object.find("script",type="application/ld+json")
                                

                                if not event_complete_data:
                                    break
                                
                                json_str = event_complete_data.text[38:-10]
                                aditional_str = aditional_event_data.text

                                #Event str info
                                event_json = json.loads(json_str)["activity"]
                                aditional_json = json.loads(aditional_str)

                                #Fields
                                title = event["title"]
                                category_spanish = event["category_spanish"]
                                description = clean(event_json["description"])
                                location_country = event_json["country"]
                                location_city = event_json["city"]
                                location_street =  event_json["address"]
                                location_latitud = event_json["addressLat"]
                                location_longitud = event_json["addressLng"]
                                organization = event_json["organization"]["name"]
                                category_english = event["category_url"]
                                url_event = build_event_url(event)

                                min_price = aditional_json["offers"]["lowPrice"]
                                max_price = aditional_json["offers"]["highPrice"]
                                currency = event["currency"]

                                #Date
                                start_date,start_hour = extract_date_hour(aditional_json["startDate"])
                                end_date,end_hour = extract_date_hour(aditional_json["endDate"])

                                
                                #Extract tags
                                tags = []
                                for tag in event_json["tags"]:
                                    tags.append(tag["name"])

                                category_events.append({
                                    "categoria_ingles":category_english,
                                    "categoria_espaniol":category_spanish,
                                    "pais":location_country,
                                    "ciudad":location_city,
                                    "direccion":location_street,
                                    "distrito":"",
                                    "latitud":location_latitud,
                                    "longitud":location_longitud,
                                    "organizador":organization,
                                    "fecha_inicio":start_date,
                                    "fecha_fin":end_date,
                                    "hora_inicio":start_hour,
                                    "hora_fin":end_hour,
                                    "precio_min":min_price,
                                    "precio_max":max_price,
                                    "moneda":currency,
                                    "titulo":title,
                                    "descripcion":description,
                                    "mood":[],
                                    "tags":tags,
                                    "publico":[],
                                    "url_evento":url_event,
                                    "negocio":1,
                                    "tipo_experiencia":1,
                                    "es_permanente":False
                                })
                                print(len(category_events))
                                break

                            except Exception as e:
                                print(f"Retry {i+1}/3 failed: {e}")
                                time.sleep(2)
                    
                    print(f"Saved {len(category_events)} events from category {key}")
                    print(category_events)
                total_events.extend(category_events)

            context.close()
            browser.close()
        
        return total_events

