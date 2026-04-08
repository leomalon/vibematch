"""
Prompt templates

"""

class PromptTemplates:
    EVENT_ENRICHMENT = """
            Clasifica el evento en emociones (moods) y genera un resumen breve del evento y que sensación daría, 
            además identifica el público objetivo al que va dirigido.

            Emociones permitidas:
            {moods}

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

    QUERY_TRANSFORMATION="""
                    Analiza la intención del usuario y conviértela en un query estructurado.

                    Debes extraer:
                    1. mood (emociones deseadas)
                    2. publico_objetivo (familia, amigos, amigas, enamorada, enamorado, etc.)
                    3. categoria (categoría de evento)
                    4. ubicación (ciudad)

                    Moods permitidos:
                    {allowed_moods}

                    Reglas:
                    - Selecciona entre 1 y 3 moods como máximo.
                    - Usa exactamente los valores en minúsculas como aparecen en la lista.
                    - Si el usuario no menciona moods explícitos, infiere los más probables según el contexto.
                    - No inventes moods fuera de la lista.

                    - publico_objetivo debe ser una descripción corta (ej: "parejas", "amigos", "familia", "solo", "jóvenes").
                    - Si no es claro, infiere el más probable.

                    - categoria debe ser un tipo de evento (ej: "teatro", "concierto", "fiesta", "gastronomía", "cultural").
                    - Si no es claro, devuelve null.
                    - Si no encuentras la ubicación entonces asume que es de la ciudad de Lima

                    Salida:
                    - Responde SOLO en JSON válido.
                    - No agregues texto adicional.

                    Formato exacto:
                    {{
                    "mood": ["mood1", "mood2"],
                    "publico_objetivo": "valor",
                    "categoria": "valor o null",
                    "ciudad":"ciudad",
                    }}

                    Input del usuario:
                    "{user_query}"
                    """

    RECOMMENDATION_PROMPT = """"
        Eres un sistema experto en recomendar eventos según la vibra y
        ambiente que solicita el usuario.

        Instrucciones:
        - Encuentra los eventos que más se ajusten a la descripción del usuario.
        - Si de los eventos enviados como contexto no encuentras ninguno, entonces recomienda el evento más cercano a lo solicitado.
        - En tu respuesta solo indica el título del evento y la descripción del evento.

        Ejemplo de respuesta: 
        'Según lo que quieres te recomiendo estos eventos:
        Evento 1: 
        Título: Titulo1
        Descripción: Descripción1

        Evento2: 
        Título: Título2
        Descripción: Descripción2
        ...
        '

        Contexto:
        {context_for_llm}

        Evento que quiere el usuario:
        {query_transformed}

        """

def build_event_classification(event: dict, allowed_moods: list[str]) -> str:
    return PromptTemplates.EVENT_QUERY.format(
        allowed_moods=", ".join(allowed_moods),
        titulo=event.get("titulo", ""),
        descripcion=event.get("descripcion", ""),
        categoria=event.get("categoria_espaniol", ""),
        tags=", ".join(event.get("tags", []))
    )

def build_query(query: str, allowed_moods: list[str]) -> str:
    return PromptTemplates.QUERY_TRANSFORMATION.format(
        allowed_moods=", ".join(allowed_moods),
        user_query=query
    )

def build_recommendation_query(context:str,query:str):
    return PromptTemplates.RECOMMENDATION_PROMPT.format(
        context_for_llm = context,
        query_transformed = query
    )