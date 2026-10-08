"""Accès au LLM (Groq). La configuration vient du fichier .env, jamais du code."""
import os

from dotenv import load_dotenv

load_dotenv()


class LLMError(Exception):
    """Erreur lors de l'appel au LLM (clé absente, réseau, quota...)."""


def get_llm():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise LLMError("GROQ_API_KEY est absente : renseigne-la dans le fichier .env")
    from langchain_groq import ChatGroq

    return ChatGroq(
        model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
        api_key=api_key,
        temperature=0.2,
    )


async def ask_llm(system: str, user: str) -> str:
    """Envoie un prompt système + utilisateur et retourne le texte de la réponse."""
    try:
        response = await get_llm().ainvoke([("system", system), ("human", user)])
    except LLMError:
        raise
    except Exception as exc:  # erreurs réseau / API
        raise LLMError(f"Appel au LLM impossible : {exc}") from exc
    return str(response.content).strip()
