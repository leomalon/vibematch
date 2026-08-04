"""
ranking_service.py

Ranks the experiences returned by the structured search.

Scoring is a transparent weighted sum: an experience gains points for every
filter it satisfies (mood, categoria, compania, tag, free text, budget fit).
Mood matches are weighted by the number of matched moods; title matches count
more than description matches.
"""


class RankingService:

    WEIGHTS = {
        "mood": 2.0,          # per matched mood
        "categoria": 1.5,
        "compania": 1.5,
        "tag": 1.0,           # per matched tag
        "texto_titulo": 3.0,
        "texto_descripcion": 1.0,
        "presupuesto": 0.5,
    }

    @classmethod
    def rank(cls, experiencias: list, resolved) -> list:
        scored = [(cls._score(exp, resolved), exp) for exp in experiencias]
        scored.sort(key=lambda item: item[0], reverse=True)
        return [exp for _, exp in scored]

    @classmethod
    def _score(cls, exp, resolved) -> float:
        score = 0.0

        if resolved.categoria_id:
            ids = {c.id for c in exp.categorias}
            if ids.intersection(resolved.categoria_id):
                score += cls.WEIGHTS["categoria"]

        if resolved.moods_id:
            ids = {em.mood_id for em in exp.experiencia_moods}
            matched = ids.intersection(resolved.moods_id)
            score += cls.WEIGHTS["mood"] * len(matched)

        if resolved.compania_id:
            ids = {c.id for c in exp.companias}
            if ids.intersection(resolved.compania_id):
                score += cls.WEIGHTS["compania"]

        if resolved.tags:
            exp_tags = {t.nombre for t in exp.tags}
            score += cls.WEIGHTS["tag"] * len(set(resolved.tags) & exp_tags)

        if resolved.busqueda_texto:
            titulo = (exp.titulo or "").lower()
            descripcion = (exp.descripcion or "").lower()
            for term in resolved.busqueda_texto:
                term = term.lower()
                if term in titulo:
                    score += cls.WEIGHTS["texto_titulo"]
                elif term in descripcion:
                    score += cls.WEIGHTS["texto_descripcion"]

        # Budget fit: reward rows whose representative price fits the budget.
        if resolved.precio_min is not None or resolved.precio_max is not None:
            precio = exp.precio_min or exp.precio_max
            if precio is not None:
                pmin = float(resolved.precio_min) if resolved.precio_min is not None else 0.0
                pmax = float(resolved.precio_max) if resolved.precio_max is not None else float("inf")
                if pmin <= float(precio) <= pmax:
                    score += cls.WEIGHTS["presupuesto"]

        return score
