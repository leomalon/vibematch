"""
Ingestion pipeline script.

Adds semantic moods to the events, converts the events into embeddings
and stores them in a vector database.

"""

#Standar modules
import os
from pathlib import Path
import json

#Local modules
from  .loaders.web_scraper import page_scraping, event_page_scraping
from .embeddings import create_vector_db

#Third-party modules
# from langchain_openai import ChatOpenAI
from ollama import Client
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import html

# ==========================================
# 1. CONFIGURATION & PATHS
# ==========================================

# Always resolve from root
BASE_DIR = Path(__file__).resolve().parent.parent.parent

#Config paths
config_path = BASE_DIR / "config" / "url_categories.json"
web_page_config = BASE_DIR/"config"/"web_page.json"

#Data paths
raw_data_path = BASE_DIR/"data"/"raw"/"raw.json"
events_path = BASE_DIR/"data"/"processed"/"events.json"
semantic_events_path = BASE_DIR / "data" / "processed" / "semantic_events.json"

#Vector DB path
# persistent_db_path = BASE_DIR / "data" / "chroma_db"
persistent_db_path = "C:/chroma_db"


# ==========================================
# 2. HELPER FUNCTIONS
# ==========================================

def load_json_data(data_path: str | Path):
    with open(data_path, "r", encoding="utf-8") as f:
        content = f.read().strip()

        if not content:
            return []

        return json.loads(content)

def write_json_data(data_path:str|Path,raw_data:str|list|dict):
    with open(data_path,mode="w",encoding="utf-8") as f:
        json.dump(raw_data or [], f, ensure_ascii=False, indent=4)

def clean_html_description(raw_html: str) -> str:
    # Parse HTML
    soup = BeautifulSoup(raw_html, "html.parser")

    # Extract text (preserves spacing between blocks)
    text = soup.get_text(separator="\n")

    # Decode HTML entities (&nbsp;, etc.)
    text = html.unescape(text)

    # Normalize whitespace
    text = "\n".join(line.strip() for line in text.splitlines() if line.strip())

    return text


# ==========================================
# 3. DATA SCRAPING (ETL)
# ==========================================

# Web page variables
web_page = load_json_data(web_page_config)

origin_page = web_page[0]["origin"]
id_tag = web_page[0]["id_tag_data"]


#Links to scrape
url_categories = load_json_data(config_path)

#Raw data
data = load_json_data(raw_data_path)

#Event processed data
event_data = load_json_data(events_path)

#Event moods
semantic_data = load_json_data(semantic_events_path)


if not data:
    data = page_scraping(url_categories)

    write_json_data(raw_data_path,data)

if not event_data:
    event_data = event_page_scraping(data,origin_page,id_tag)

    write_json_data(events_path,event_data)

# ==========================================
# 4. LLM ENRICHMENT
# ==========================================
def define_price_range(currency: str, price, usd_to_pen: float = 3.7):
    """
    Classifies price into standardized ranges.

    Returns one of:
    ["gratis", "economico", "moderado", "caro", "premium"]
    """

    # --- Input validation ---
    try:
        price = float(price)
    except (TypeError, ValueError):
        return "sin rango precio"  # or "unknown"

    # --- Currency normalization ---
    if currency == "USD":
        pen_price = price * usd_to_pen
    else:
        pen_price = price

    # --- Classification ---
    if pen_price == 0:
        return "gratis"
    elif 0 < pen_price < 40:
        return "economico"
    elif 40 <= pen_price < 120:
        return "moderado"
    elif 120 <= pen_price < 300:
        return "caro"
    else:  # pen_price >= 300
        return "premium"

def extract_moods(events, llm_instance,provider:str):
    enriched = []

    for event in events:

        moneda = event["moneda"]
        precio = event["precio"]

        #Clean description
        event["descripcion"] = clean_html_description(event["descripcion"])

        #Add price range description
        event["precio_rango"] = define_price_range(moneda,precio)

        ALLOWED_MOODS = ["romántico","energético","relajado","misterioso","divertido","cultural",
            "artistico","nocturno","familiar","intenso","fiesta","educativo","fiestero","espontáneo",
            "elegante","underground","deportivo","gastronómico","urbano"]

        prompt = f"""
            Clasifica el evento en emociones (moods)

            Emociones permitidas:
            {ALLOWED_MOODS}

            Reglas:
            - Selecciona solo entre 2 y 4 emociones.
            - Usa exactamente los valores en minúsculas como aparecen en la lista.
            - Si no es claro, elige las emociones más probables sin salirte de la lista.
            - No repitas emociones.
            - Solo utiliza la lista de emociones permitida.
            - Responde SOLO en JSON válido, sin texto adicional.
            - Formato exacto:
                {{"emociones": ["emocion1","emocion2"]}}

            Evento:
            Titulo: {event["titulo"]}
            Descripción: {event["descripcion"]}
            Categoría: {event["categoria_espaniol"]}
            Tags: {event["tags"]}
            """
        
        if provider=="OpenAI":
            response = llm_instance.invoke(prompt)
            response = response.content
        
        elif provider=="Ollama-cloud":

            messages = [
            {
                'role': 'user',
                'content': prompt,
            }
            ]

            response = llm_instance.chat('gpt-oss:120b-cloud', messages=messages)
            response = response.message.content


        try:
            moods = json.loads(response)

            emociones = moods.get("emociones", [])

            #Clean moods in case adds a mood that is not allowed
            emociones = list(set([m for m in emociones if m in ALLOWED_MOODS]))[:4]
            print(emociones)

        except:
            emociones = []

        event["mood"] = emociones
        enriched.append(event)

    return enriched

load_dotenv()

llm = Client(
    host="https://ollama.com",
    headers={'Authorization': 'Bearer ' + os.environ.get('OLLAMA_API_KEY')}
)

if not semantic_data:
    events_data = load_json_data(events_path)
    
    events_with_moods = extract_moods(events_data,llm,"Ollama-cloud")

    write_json_data(semantic_events_path,events_with_moods)

# ==========================================
# 5. SEMANTIC REPRESENTATION
# ==========================================

def format_event_for_embedding(event: dict) -> str:
    return f"""
    Evento: {event['titulo']}
    Ciudad: {event['ciudad']}
    Categoría: {event['categoria_espaniol']}

    Descripción:
    {event['descripcion']}

    Mood: {", ".join(event['mood'])}

    Tags: {", ".join([tag.replace("#", "") for tag in event['tags']])}

    Precio: {event['precio_rango']}
    Ubicación: {event['direccion']}
    """

formatted_events = []

events = load_json_data(semantic_events_path)

for event in events:
    formatted_events.append(format_event_for_embedding(event=event))

# ==========================================
# 6. EMBEDDING GENERATION AND STORING
# ==========================================
collection = create_vector_db(persistent_db_path,"vibe_collection")

#Store vectors
collection.add(
    documents=formatted_events,
    ids=[f"id{i+1}" for i in range(len(formatted_events))]
)