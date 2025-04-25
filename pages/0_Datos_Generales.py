import streamlit as st
import pandas as pd
import os

st.title("# Datos Generales de Operación")

FILE = "datos_generales.csv"

def load_defaults():
    if os.path.exists(FILE):
        return pd.read_csv(FILE).set_index("Parametro").to_dict()["Valor"]
    else:
        return {
            "Rendimiento Camion": 2.5,
            "Costo Diesel": 24,
            "Horas Termo": 0,
            "Rendimiento Termo": 3,
            "Bono ISR IMSS": 462.66,
            "Sueldo Operador": 2100,
        }

def save_defaults(valores):
    df = pd.DataFrame(valores.items(), columns=["Parametro", "Valor"])
    df.to_csv(FILE, index=False)

valores = load_defaults()

st.subheader("Valores Editables")

for key in valores:
    valores[key] = st.number_input(key, value=float(valores[key]), step=0.1)

if st.button("Guardar Datos Generales"):
    save_defaults(valores)
    st.success("Datos guardados correctamente.")
