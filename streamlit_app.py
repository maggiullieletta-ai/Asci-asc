import streamlit as st
import pandas as pd

st.set_page_config(page_title="Gestione Carichi Patologia", layout="centered")
st.title("🏥 Gestione Carichi Anatomia Patologica")

MEDICI = {
    "D’AMURI":   ["DERM", "NEURO"],
    "FASANO":    ["GI", "EMATO"],
    "OLLA":      ["URO", "GI"],
    "CASCARANO": ["GINECO", "BREAST"],
    "COLOSIMO":  ["NEURO", "DERM", "EMATO"],
    "CARBOTTA":  ["BREAST", "GINECO"],
    "NGUEFACK":  ["GI", "URO"],
    "DANGELO":   ["DERM", "BREAST", "GINECO"]
}

st.header("1. Effort e Arretrato del Giorno")
effort_data = {}
cols = st.columns(2)

for i, (medico, specs) in enumerate(MEDICI.items()):
    with cols[i % 2]:
        st.subheader(medico)
        st.caption(f"Spec: {', '.join(specs)}")
        presente = st.checkbox(f"Presente", value=True, key=f"pres_{medico}")
        ore = st.number_input(f"Ore lavoro", min_value=0.0, max_value=12.0, value=7.36 if presente else 0.0, step=0.5, key=f"ore_{medico}")
        arretrato = st.number_input(f"Arretrato (pt)", min_value=0.0, value=0.0, step=0.5, key=f"arr_{medico}")
        
        effort_data[medico] = {
            "pres": presente,
            "ore": ore,
            "arr": arretrato
        }

st.divider()

st.header("2. Esami del Giorno")
casi_input = st.text_area(
    "Formato: ID, CATEGORIA, PESO (uno per riga)",
    value="B01, DERM, 1.0\nB02, DERM, 4.5\nB03, GI, 5.0\nB04, GI, 2.0\nB05, URO, 5.5\nB06, BREAST, 4.5\nB07, GINECO, 5.0\nB08, EMATO, 3.0\nB09, NEURO, 6.0",
    height=150
)

if st.button("🚀 Calcola Assegnazione Equa", type="primary"):
    esami = []
    for line in casi_input.strip().split("\n"):
        if line.strip():
            parti = line.split(",")
            if len(parti) == 3:
                esami.append({
                    "id": parti[0].strip(),
                    "cat": parti[1].strip().upper(),
                    "peso": float(parti[2].strip())
                })
    
    stato = {}
    for m, specs in MEDICI.items():
        eff = effort_data[m]
        cap = (eff["ore"] / 7.36) if (eff["pres"] and eff["ore"] > 0) else 0.0
        stato[m] = {
            "specs": specs,
            "cap": cap,
            "arr": eff["arr"],
            "nuovo": 0.0,
            "casi": []
        }

    esami_ord = sorted(esami, key=lambda x: x["peso"], reverse=True)
    for e in esami_ord:
        cand = [m for m, d in stato.items() if d["cap"] > 0 and e["cat"] in d["specs"]]
        if not cand:
            cand = [m for m, d in stato.items() if d["cap"] > 0]
            
        if cand:
            scelto = min(cand, key=lambda m: (stato[m]["arr"] + stato[m]["nuovo"]) / stato[m]["cap"])
            stato[scelto]["nuovo"] += e["peso"]
            stato[scelto]["casi"].append(f"{e['id']} ({e['peso']}pt)")

    st.header("📊 Risultato Assegnazione")
    risultati = []
    for m, d in stato.items():
        if d["cap"] == 0:
            risultati.append({"Medico": m, "Stato": "ASSENTE", "Arretrato": "-", "Nuovo": "-", "Totale": "-", "Casi": "-"})
        else:
            risultati.append({
                "Medico": m,
                "Stato": "Presente",
                "Arretrato": f"{d['arr']:.1f}",
                "Nuovo": f"+{d['nuovo']:.1f}",
                "Totale": f"{d['arr'] + d['nuovo']:.1f}",
                "Casi": ", ".join(d["casi"]) if d["casi"] else "Nessuno"
            })
            
    st.dataframe(pd.DataFrame(risultati), use_container_width=True)
