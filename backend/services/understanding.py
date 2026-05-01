"""
LLM wrapper for returning a structured query.

"""

#Local modules
from rag.llm.prompt_templates import build_query


class QueryUnderstandingService:
    def __init__(self,llm_client):
        self.llm_client = llm_client
    
    def parse(self, query: str) -> dict:
        # call LLM
        llm = self.llm_client

        ALLOWED_MOODS = ["romántico","energético","relajado","misterioso","divertido","cultural",
            "artistico","nocturno","familiar","intenso","fiesta","educativo","fiestero","espontáneo",
            "elegante","underground","deportivo","gastronómico","urbano","desconexión","aire-libre",
            "natural","aventurero","foodie","casual","buen-ambiente","extremo","íntimo"]

        prompt = build_query(query,ALLOWED_MOODS)

        structured_query = llm.invoke(prompt)

        return structured_query