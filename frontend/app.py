"""Interface Streamlit : 4 écrans (cas, questions, revue médecin, rapport)."""
import os

import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="Orientation clinique simulée", page_icon="🩺")
st.title("🩺 Orientation clinique simulée")
st.warning("Exercice académique. Ce système ne remplace pas une consultation médicale.")


def call_api(method: str, path: str, **kwargs):
    try:
        response = requests.request(method, f"{API_URL}{path}", timeout=120, **kwargs)
        response.raise_for_status()
        return response.json()
    except requests.HTTPError as exc:
        st.error(f"Erreur API : {exc.response.text}")
    except requests.RequestException as exc:
        st.error(f"API injoignable : {exc}")
    return None


def send(value: str):
    data = call_api(
        "POST",
        "/consultation/resume",
        json={"thread_id": st.session_state.thread_id, "value": value},
    )
    if data:
        st.session_state.data = data
        st.rerun()


data = st.session_state.get("data")

# Écran 1 : cas initial
if data is None:
    st.header("1. Cas initial du patient (fictif)")
    case = st.text_area("Décris les symptômes", placeholder="Toux et fièvre depuis 2 jours")
    if st.button("Démarrer la consultation") and case.strip():
        session = call_api("POST", "/sessions/start")
        if session:
            st.session_state.thread_id = session["thread_id"]
            started = call_api(
                "POST",
                "/consultation/start",
                json={"thread_id": session["thread_id"], "patient_case": case},
            )
            if started:
                st.session_state.data = started
                st.rerun()

# Écran 2 : questions au patient
elif data["status"] == "waiting_patient":
    n = data["question_count"] + 1
    st.header(f"2. Question {n} / 5")
    st.progress(data["question_count"] / 5)
    st.info(data["question"])
    answer = st.text_input("Réponse du patient", key=f"answer_{n}")
    if st.button("Envoyer") and answer.strip():
        send(answer)

# Écran 3 : revue du médecin
elif data["status"] == "waiting_physician":
    st.header("3. Revue du médecin traitant")
    if data["red_flags"]:
        st.error("Signaux d'alerte : " + ", ".join(data["red_flags"]))
    st.subheader("Synthèse clinique préliminaire")
    st.write(data["diagnostic_summary"])
    st.subheader("Recommandation intermédiaire")
    st.write(data["interim_care"])
    treatment = st.text_area("Traitement ou conduite à tenir proposée par le médecin")
    if st.button("Valider") and treatment.strip():
        send(treatment)

# Écran 4 : rapport final
elif data["status"] == "completed":
    st.header("4. Rapport final")
    st.markdown(data["final_report"])
    if st.button("Nouvelle consultation"):
        st.session_state.clear()
        st.rerun()
