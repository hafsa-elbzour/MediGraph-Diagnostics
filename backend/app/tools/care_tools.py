"""Tool de recommandation intermédiaire (prudente, jamais un diagnostic)."""
from app.llm import ask_llm

CARE_SYSTEM = (
    "Tu aides dans un exercice académique de simulation. Propose une recommandation "
    "intermédiaire GÉNÉRALE et prudente (repos, hydratation, surveillance, "
    "consultation rapide en cas d'aggravation). Ne donne aucun diagnostic définitif, "
    "aucun médicament ni dose. Réponds en français, en 4 lignes maximum."
)


async def recommend_interim_care(summary: str, red_flags: list[str]) -> str:
    alert = (
        f"Signaux d'alerte détectés : {', '.join(red_flags)}. "
        "Insiste sur la nécessité d'une consultation rapide."
        if red_flags
        else "Aucun signal d'alerte détecté."
    )
    return await ask_llm(CARE_SYSTEM, f"Synthèse clinique :\n{summary}\n\n{alert}")
