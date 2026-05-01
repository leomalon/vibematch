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
from  rag.ingestion.loaders.web_scraper import page_scraping, event_page_scraping

#Third-party modules
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import html

#Local modules
from rag.llm.ollama import ChatOllama
from rag.ingestion.embeddings import get_openai_embedding
from rag.llm.prompt_templates import build_event_classification
from rag.vectordb.chroma_db import Persistent_ChromaDB

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
ig_path = BASE_DIR/"data"/"processed"/"ig_data.json"

#Vector DB path
# persistent_db_path = BASE_DIR / "data" / "chroma_db"
persistent_db_path = "C:/chroma_db"


# ==========================================
# 2. HELPER FUNCTIONS
# ==========================================

def load_json_data(data_path: str | Path):

    
    if not data_path.exists():
        return []

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
raw_data = load_json_data(raw_data_path)

#Event processed data
raw_event_data = load_json_data(events_path)

#Ig data
ig_event_data = load_json_data(ig_path)

#Event moods
event_semantic_data = load_json_data(semantic_events_path)

#--- EVENT SCRAPING ---

if not raw_data:
    print("There is no raw data")
    raw_data = page_scraping(url_categories)

    write_json_data(raw_data_path,raw_data)

if not raw_event_data:
    print("There is no event data")
    raw_event_data = event_page_scraping(raw_data,origin_page,id_tag)

    write_json_data(events_path,raw_event_data)

# ==========================================
# 4. LLM ENRICHMENT
# ==========================================
def define_event_price_range(currency: str, price, usd_to_pen: float = 3.7):
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

def enrich_events_with_llm(events:list, llm_instance):
    enriched = []

    for event in events:

        moneda = event["moneda"]
        precio = event["precio"]

        #Clean description
        event["descripcion"] = clean_html_description(event["descripcion"])

        #Add price range description
        event["precio_rango"] = define_event_price_range(moneda,precio)

        ALLOWED_MOODS = ["romántico","energético","relajado","misterioso","divertido","cultural",
            "artistico","nocturno","familiar","intenso","fiesta","educativo","fiestero","espontáneo",
            "elegante","underground","deportivo","gastronómico","urbano","desconexión","aire-libre",
            "natural","aventurero","foodie","casual","buen-ambiente","extremo","íntimo"]

        prompt= build_event_classification(event,ALLOWED_MOODS)
        
        response = llm_instance.invoke(prompt)


        try:
            moods = json.loads(response)

            emociones = moods.get("emociones", [])
            descripcion_resumen = moods.get("resumen", [])
            publico = moods.get("publico", [])

            #Clean moods in case adds a mood that is not allowed
            emociones = list(set([m for m in emociones if m in ALLOWED_MOODS]))[:4]
            print(emociones)

        except:
            emociones = []

        event["mood"] = emociones
        event["descripcion"] = descripcion_resumen
        event["público"] = publico
        enriched.append(event)

    return enriched

load_dotenv()

llm = ChatOllama(os.environ.get("OLLAMA_API_KEY"))

if not event_semantic_data:
    events_data = load_json_data(events_path)
    
    events_with_moods = enrich_events_with_llm(events_data,llm)

    write_json_data(semantic_events_path,events_with_moods)

# ==========================================
# 5. SEMANTIC REPRESENTATION
# ==========================================

def format_event_for_embedding(event: dict) -> str:
    return f"""

    Moods: {", ".join(event['mood'])}
    Moods: {", ".join(event['mood'])}

    Tags clave: {", ".join([tag.replace("#", "") for tag in event['tags']])}

    Público objetivo: 
    {event["público"]}

    Descripción corta:
    {event['descripcion']}

    Categoría: {event['categoria_espaniol']}

    Ubicación: {event["ciudad"]}

    """

events = load_json_data(semantic_events_path)

formatted_events = [format_event_for_embedding(event=event) for event in events]
event_metadatas = []

for event in events:
    metadata = {
        "titulo": event.get("titulo"),
        "descripcion": event.get("descripcion"),
        "url": event.get("url_evento"),
        "direccion": event.get("direccion"),
        "categoria": event.get("categoria_espaniol"),
        "precio": event.get("precio"),
        "moneda": event.get("moneda"),
    }

    tags = event.get("tags")

    # Only add tags if valid and non-empty
    if isinstance(tags, list) and len(tags) > 0:
        metadata["tags"] = tags

    event_metadatas.append(metadata)


# ==========================================
# 6. EMBEDDING GENERATION AND STORING
# ==========================================

vector_db = Persistent_ChromaDB(persistent_db_path,get_openai_embedding("text-embedding-3-large"))

#Creates and stores vectors
vector_db.create_vector_db("vibe_collection",
                           formatted_events,
                           event_metadatas)