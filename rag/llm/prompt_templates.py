"""
Prompt templates

"""

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

    QUERY_TRANSFORMATION="""
                    Analiza la intención del usuario y conviértela en un query estructurado.

                    Debes extraer:
                    1. mood (emociones deseadas)
                    2. publico_objetivo (familia, amigos, amigas, enamorada, enamorado, etc.)
                    3. categoria (categoría de evento)
                    4. ubicación (ciudad)

                    Moods permitidos:
                    {allowed_moods}

                    RESTRICCIÓN IMPORTANTE:
                    - El mood "íntimo" SOLO puede usarse cuando se activa la REGLA PRIORITARIA (intención sexual explícita).
                    - NO usar "íntimo" para citas románticas normales, salidas en pareja o contextos románticos generales.
                    - Para citas románticas estándar, usar únicamente "romántico" u otros moods apropiados.

                    REGLA PRIORITARIA (CRÍTICA):
                    - Si el input del usuario contiene intención explícita de actividad sexual (por ejemplo: "sex", "tener sexo", "tener relaciones sexuales", "noche íntima", "detonar"):
                        - Asigna EXACTAMENTE lo siguiente:
                            Moods: romántico, íntimo
                            Público objetivo: pareja
                            Categoría: hotel
                        - Ignora cualquier otra inferencia
                        - Continúa completando ubicación normalmente

                    REGLAS GENERALES:
                    - Selecciona entre 1 y 3 moods como máximo.
                    - Usa exactamente los valores en minúsculas como aparecen en la lista.
                    - Si el usuario no menciona moods explícitos, infiere los más probables según el contexto.
                    - No inventes moods fuera de la lista.

                    - publico_objetivo debe ser una descripción corta (ej: "parejas", "amigos", "familia", "solo").
                    - Si no es claro, infiere el más probable.

                    - categoria debe ser un tipo de evento o establecimiento (ej: "teatro", "concierto", "fiesta", "gastronomía", "cultural","comedia","restaurante", "bar","rooftop", etc.).
                    - DEBES inferir una categoría probable basada en el contexto del usuario.
                    - SOLO devuelve null si no existe absolutamente ninguna pista en el input.
                    - Si no encuentras la ubicación entonces asume que es de la ciudad de Lima

                    Salida:
                    - Responde solo en formato texto según el ejemplo.
                    - No agregues texto adicional.

                    Formato exacto:

                    "
                    Moods: mood_1, mood_2, mood_3, ...
                    Moods: mood_1, mood_2, mood_3, ...

                    Tags clave: tag1, tag2, tag3, ...

                    Público objetivo: pareja, amigos, familia, etc.

                    Categoría: valor

                    Ubicación: ciudad
                    "

                    Input del usuario:
                    "{user_query}"
                    """

    RECOMMENDATION_PROMPT = """"
        Eres un sistema experto en recomendación de eventos basado en la intención del usuario.

        OBJETIVO:
        Seleccionar únicamente los eventos del contexto que mejor coincidan con la solicitud del usuario.


        FUENTE DE VERDAD:
        - Debes basarte PRINCIPALMENTE en el query estructurado proporcionado.
        - NO reinterpretar el lenguaje original del usuario.
        - Usa los campos (moods, categoría, público objetivo) como criterios de filtrado.

        REGLA PRIORITARIA:
        - Si el query estructurado contiene:
            Moods: romantico, intimo
            Categoría: hotel
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


        Ejemplo de respuesta:
        '
        [
            {{
                "titulo": "string",
                "descripcion":"string",
                "url": "string",
                "direccion":"string",
                "categoria": "string",
                "precio": 0,
                "moneda": "string"
            }},
            {{
                "titulo": "string",
                "descripcion":"string",
                "url": "string",
                "direccion":"string",
                "categoria": "string",
                "precio": 0,
                "moneda": "string"
            }},
            ...
        ]
        '

        Contexto:
        {context_for_llm}

        Evento que quiere el usuario:
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