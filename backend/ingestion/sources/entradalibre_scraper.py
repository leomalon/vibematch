"""
entradalibre_scraper.py

Python script to extract events from a web page.

"""
#Python built-in modules
import time
import random

#Python third-party modules
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

#Utility modules
from backend.ingestion.sources.utilities import parse_spanish_date,parse_time_range,parse_location
from backend.geocoding.geopy_provider import GeopyGeocoder

geocoder = GeopyGeocoder()

class EntradaLibreScraper():

    def __init__(self,origin,web_parameters:dict,web_categories:dict):
        self.origin = origin
        self.parameters = web_parameters
        self.categories = web_categories

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

        event_container = self.parameters["event_class"]
        title_event = self.parameters["event_title_tag"]

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

                    page_url = category["url"]+"page"+"/"+str(current_page)+"/"

                    #We wait some random time
                    time.sleep(random.uniform(2,4))

                    #We start the navigation
                    page.goto(page_url, wait_until="domcontentloaded", timeout=40000)

                    html = page.content()

                    soup_object = BeautifulSoup(html, "html.parser")
                                    
                    list_events = soup_object.find_all("li",class_=event_container)
                    
                    for div_event in list_events:
                        h2_title_container = div_event.find("h2",title_event)
                        title_text = h2_title_container.get_text(strip=True)
                        event_url = h2_title_container.find("a",class_="second_font" ).get("href")

                        event_data = {
                            "title":title_text,
                            "url_event":event_url,
                            "category_url":category["url"],
                            "category_spanish":category["nombre"]
                        }

                        category_data[category["category_request"]].append(event_data)

                raw_data.append(category_data)

            #We close the context for promart
            context.close()
            browser.close()
        
        return raw_data


    def scrape_events(self,events):

        total_events = []

        event_start_date = self.parameters["event_start_date"]
        event_end_date = self.parameters["event_end_date"]
        event_time = self.parameters["event_time"]
        event_address = self.parameters["event_full_address"]
        full_event_description = self.parameters["description_content"]


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
                                time.sleep(random.uniform(3,6))

                                page.goto(event["url_event"],wait_until="domcontentloaded",timeout=10000)

                                html = page.content()

                                soup_object = BeautifulSoup(html, "html.parser")

                                start_date_tag = soup_object.find("span", class_=event_start_date)
                                end_date_tag = soup_object.find("span", class_=event_end_date)
                                time_tag = soup_object.find("span", class_=event_time)
                                place_tag = soup_object.find("span", class_=event_address)
                                description_div = soup_object.find("div", class_=full_event_description)

                                print("Entrada libre extraction dates")
                                print(start_date_tag)
                                print(end_date_tag)
                                print(time_tag)
                                print(place_tag)
                                start_date = start_date_tag.get_text(strip=True) if start_date_tag else None
                                end_date = end_date_tag.get_text(strip=True) if end_date_tag else None
                                time_event = time_tag.get_text(strip=True) if time_tag else None
                                event_place = parse_location(place_tag.get_text(strip=True) if place_tag else None)
                                
                                #Description paragraphs
                                full_event_description = description_div.get_text(strip=True,separator=" ")
                                event_descripion = full_event_description.split("Fecha")[0].strip()
                                
                                #Fields
                                title = event["title"]
                                category_spanish = event["category_spanish"]
                                description = event_descripion
                                location_country = event_place["country"]
                                location_city = event_place["city"]
                                location_street =  event_place["address"]
                                location_district =  event_place["district"]
                                organization = None
                                category_english = event["category_spanish"]
                                url_event = event["url_event"]
                                min_price = 0
                                max_price = 0
                                currency = "PEN"

                                #Date parsing
                                start_date = parse_spanish_date(start_date)
                                end_date = parse_spanish_date(end_date)
                                start_hour,end_hour = parse_time_range(time_event)

                                #Latitud and longitud
                                full_adress_str = f"{location_street},{location_district}, {location_city}, {location_country}"
                                geocode_location = geocoder.geocode(full_adress_str)
                                location_latitud = geocode_location.get("latitude")
                                location_longitud = geocode_location.get("longitude")


                                category_events.append({
                                    "categoria_ingles":category_english,
                                    "categoria_espaniol":category_spanish,
                                    "pais":location_country,
                                    "ciudad":location_city,
                                    "direccion":location_street,
                                    "distrito":location_district,
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
                                    "tags":[],
                                    "publico":[],
                                    "url_evento":url_event,
                                    "negocio":2,
                                    "tipo_experiencia":1,
                                    "es_permanente":False
                                })

                                print(category_events)

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
