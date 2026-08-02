"""
Prompt templates

"""

import json

class PromptTemplates:
    EVENT_ENRICHMENT = """
            Clasifica el evento en emociones (moods) y genera un resumen breve del evento y que sensación daría, 
            además identifica el público objetivo al que va dirigido.

            Emociones permitidas:
            {allowed_moods}

            Reglas:
            - Selecciona solo entre 2 y 4 emociones.
            - Usa exactamente los valores en minúsculas como aparecen en la lista.
            - No repitas emociones.
            - Solo utiliza la lista de emociones permitida.
            - Si no es claro, elige las emociones más probables sin salirte de la lista.

            Resumen:
            - Genera un resumen claro y objetivo de máximo 2 líneas.
            - Elimina lenguaje promocional o redundante.
            - Enfócate en el tipo de evento, ambiente y experiencia.

            Público: 
            - Identifica claramente el público al que va dirigido: familia, amigos, amigas, enamorada, enamorado, etc.

            Salida:
            - Responde SOLO en JSON válido, sin texto adicional.
            - Formato exacto:
            {{
            "emociones": ["emocion1","emocion2"],
            "resumen": "texto breve aquí",
            "publico": "público al que apunta"
            }}

            Evento:
            Titulo: {titulo}
            Descripción: {descripcion}
            Categoría: {categoria}
            Tags: {tags}
            """

    JSON_BUILDER_PROMPT = """
            Eres un sistema experto en interpretar consultas de usuarios para buscar experiencias.

            Tu única tarea es convertir el texto del usuario en un JSON estructurado.

            NO respondas preguntas.
            NO recomiendes experiencias.
            NO expliques tu razonamiento.

            ----------------------------------------------------
            CATÁLOGOS
            ----------------------------------------------------

            Los siguientes son los únicos valores válidos para estos campos.

            {catalogs}

            Si el usuario menciona un valor equivalente o una variante ("resto", "restobar", "restaurant"), selecciona el valor más cercano del catálogo.

            Si ningún valor del catálogo aplica, devuelve null o [] según corresponda.

            ----------------------------------------------------
            OBJETIVO
            ----------------------------------------------------

            Extrae todos los filtros posibles de la consulta del usuario.

            Si un filtro no está presente o no puede inferirse con suficiente confianza, déjalo como null o [].

            ----------------------------------------------------
            REGLAS
            ----------------------------------------------------

            1. disponibilidad

            Extrae:

            - fecha_inicio
            - fecha_fin
            - hora_inicio
            - hora_fin

            Ejemplos:

            "hoy"

            "mañana"

            "este sábado"

            "este fin de semana"

            "del 15 al 20"

            "después de las 8"

            Si solo existe una fecha:

            fecha_inicio = fecha_fin

            Si solo existe una hora mínima:

            hora_inicio = valor
            hora_fin = null

            Las fechas deben devolverse en formato ISO:

            YYYY-MM-DD

            Las horas:

            HH:MM

            ----------------------------------------------------
            CONTEXTO TEMPORAL
            ----------------------------------------------------

            La fecha actual es: {date}

            La hora actual es: {time}

            Todas las referencias temporales relativas ("hoy", "mañana", "este fin de semana", etc.) deben calcularse usando esta fecha.

            ----------------------------------------------------

            2. ubicación

            Extrae:

            pais

            ciudad

            distrito

            Utiliza únicamente valores existentes en el catálogo.
            Cada elemento del catálogo incluye un id y un nombre. 
            Si identificas que la consulta corresponde a un elemento del catálogo, devuelve exactamente el objeto completo (id y nombre) del catálogo. 
            No inventes IDs, no modifiques nombres y no combines información de diferentes elementos. Si ningún elemento aplica, devuelve null o [] según corresponda."

            Si no se especifica ninguno:

            Asume que busca en Lima, Perú.

            ----------------------------------------------------

            3. preferencias

            Extrae:

            tipo experiencia

            categoria

            moods

            companias

            Utiliza únicamente valores del catálogo.

            Puedes devolver múltiples moods.

            Puedes devolver múltiples compañías.

            No inventes valores.

            Para tipo_experiencia (solo uno)

            Selecciona exactamente uno de los siguientes valores del catálogo:

            - evento:
            Actividades organizadas que ocurren en una fecha u horario determinado.
            Pueden requerir o no entrada.
            Ejemplos:
            - concierto
            - teatro
            - festival
            - feria
            - exposición temporal
            - campeonato
            - stand up
            - taller
            - curso
            - conferencia

            - point:
            Lugares físicos o establecimientos que una persona puede visitar en cualquier momento.
            No representan un evento puntual.
            Ejemplos:
            - restaurante
            - cafetería
            - bar
            - rooftop
            - playa
            - hotel
            - museo
            - parque
            - huarique

            - plan:
            Actividades que una persona puede realizar independientemente de un evento organizado o un local específico.
            Ejemplos:
            - trekking
            - caminar
            - paseo
            - ciclismo
            - correr
            - viajar
            - picnic
            - surf
            - camping

            Devuelve siempre uno de estos tres valores cuando exista suficiente información.
            Solo devuelve null si realmente no es posible inferir el tipo.

            Para moods:

            No solo extraigas moods mencionados literalmente.
            También puedes inferir moods implícitos a partir del contexto de la consulta.

            Ejemplos:

            "Quiero ir con mi enamorada a un restaurante"
            → moods: ["romántico"]

            "Una salida con mis hijos"
            → moods: ["familiar"]

            "Algo para celebrar un cumpleaños con amigos"
            → moods: ["fiesta", "divertido"]

            "Quiero desconectarme de la ciudad"
            → moods: ["relajado", "natural"]

            Solo agrega un mood inferido si existe una relación clara con la intención del usuario.
            No agregues moods por asociaciones débiles.


            ----------------------------------------------------

            4. presupuesto

            Extrae:

            precio_min

            precio_max

            Ejemplos:

            "menos de 100"

            ↓

            precio_max=100

            "entre 50 y 100"

            ↓

            50
            100

            "gratis"

            ↓

            0
            0

            ----------------------------------------------------

            5. tags

            Extrae únicamente conceptos importantes que describan la experiencia.

            NO utilices palabras vacías.

            Ejemplos

            karting

            cerámica

            sushi

            tributo

            running

            paintball

            escape room

            No tienen que existir en el catálogo.

            ----------------------------------------------------

            6. busqueda_texto

            Aquí coloca nombres propios o términos que probablemente aparecerán únicamente en el título o descripción de la experiencia solicitada.

            Ejemplos

            Arctic Monkeys

            Coldplay

            Harry Potter

            Marvel

            Si no existe ninguno:

            null

            ----------------------------------------------------
            SALIDA
            ----------------------------------------------------

            Devuelve EXCLUSIVAMENTE JSON válido.

            No utilices markdown.

            No utilices ```json.

            No agregues comentarios.

            El formato debe ser EXACTAMENTE:

            {{
            "disponibilidad": {{
                "fecha_inicio": null,
                "fecha_fin": null,
                "hora_inicio": null,
                "hora_fin": null
            }},
            "ubicacion": {{
                "pais": null,
                "ciudad": null,
                "distrito": null
            }},
            "preferencias": {{
                "tipo_experiencia": [],
                "categoria": [],
                "moods": [],
                "companias": []
            }},
            "presupuesto": {{
                "precio_min": null,
                "precio_max": null
            }},
            "tags": [],
            "busqueda_texto": []
            }}

            ----------------------------------------------------
            CONSULTA DEL USUARIO
            ----------------------------------------------------

            {user_query}
            """

    RECOMMENDATION_PROMPT = """
        Eres un sistema experto en recomendación de eventos y establecimientos basado en la intención del usuario.

        OBJETIVO:
        Seleccionar únicamente los eventos o establecimientos del contexto que mejor coincidan con la solicitud del usuario.


        FUENTE DE VERDAD:
        - Debes basarte PRINCIPALMENTE en la descripción brindada por el usuario.
        - NO reinterpretar la descripción brindada por el usuario.
        - Usa los campos (moods, categoría, público objetivo) como criterios de filtrado.
        - Si en la descripción el tipo de comida es específico haz caso a eso.
        - Ten en cuenta la categoría del establecimiento o evento que se indica.

        RESTRICCIÓN IMPORTANTE:
        - Si en la descripción del usuario no está explícitamente una intención de actividad sexual (por ejemplo: "sex", "tener sexo", "tener relaciones sexuales", "noche íntima", "detonar")
          no puedes recomendar un evento con la categoría "hotel".

        REGLA PRIORITARIA:
        - Si la descripción brindada por el usuario contiene intención explícita de actividad sexual (por ejemplo: "sex", "tener sexo", "tener relaciones sexuales", "noche íntima", "detonar").
        - Entonces:
            - SOLO selecciona eventos cuya categoría sea "hotel"
            - Prioriza eventos que impliquen privacidad, pareja o ambiente íntimo
            - Ignora eventos como restaurantes, conciertos, fiestas, etc.


        REGLAS:
        - Usa SOLO la información del contexto proporcionado.
        - NO inventes eventos.
        - Si ningún evento coincide, responde EXACTAMENTE con: []
        - Devuelve entre 1 y 8 eventos como máximo.

        FORMATO DE SALIDA:
        - Responde SOLO con JSON válido.
        - NO incluyas texto adicional.
        - NO incluyas explicaciones.
        - El JSON debe ser una lista de objetos.
        - NO uses markdown.
        - NO uses ```json.
        - NO agregues comentarios.
        - La respuesta debe comenzar con [ y terminar con ].


        FORMATO DE RESPUESTA OBLIGATORIO:

        [
        {{
            "titulo": "string",
            "descripcion": "string",
            "url": "string",
            "direccion": "string",
            "categoria": "string",
            "precio": 0,
            "moneda": "string"
        }}
        ]

        Contexto:
        {context_for_llm}

        Descripción brindada por el usuario:
        {query_transformed}

        """

def build_event_classification(event: dict, allowed_moods: list[str]) -> str:
    return PromptTemplates.EVENT_ENRICHMENT.format(
        allowed_moods=", ".join(allowed_moods),
        titulo=event.get("titulo", ""),
        descripcion=event.get("descripcion", ""),
        categoria=event.get("categoria_espaniol", ""),
        tags=", ".join(event.get("tags", []))
    )

def build_recommendation_query(context:str,query:str):
    return PromptTemplates.RECOMMENDATION_PROMPT.format(
        context_for_llm = context,
        query_transformed = query
    )

def build_prompt_json_filters(query: str, catalogs: dict,date,time) -> str:

    return PromptTemplates.JSON_BUILDER_PROMPT.format(
        catalogs=json.dumps(
            catalogs,
            ensure_ascii=False,
            indent=2
        ),
        date = date,
        time = time,
        user_query=query
    )