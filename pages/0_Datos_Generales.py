import streamlit as st
import pandas as pd
import os

st.title("# Datos Generales de Operación")

FILE = "datos_generales.csv"

valores_por_defecto = {
    "Rendimiento Camion": 2.5,
    "Costo Diesel": 24,
    "Rendimiento Termo": 3,
    "Bono ISR IMSS": 462.66,
    "Pago x km IMPO": 2.10,
    "Pago x km EXPO": 2.50,
    "Pago fijo VACIO": 200.00,
    "Tipo de cambio USD": 17.5,
    "Tipo de cambio MXN": 1.0
}

def load_defaults():
    if os.path.exists(FILE):
        return pd.read_csv(FILE).set_index("Parametro").to_dict()["Valor"]
    else:
        return valores_por_defecto.copy()

def save_defaults(valores):
    df = pd.DataFrame(valores.items(), columns=["Parametro", "Valor"])
    df.to_csv(FILE, index=False)

valores = load_defaults()

st.subheader("Valores Editables")

for key in valores_por_defecto:
    valores[key] = st.number_input(key, value=float(valores.get(key, valores_por_defecto[key])), step=0.1)

if st.button("Guardar Datos Generales"):
    save_defaults(valores)
    st.success("Datos guardados correctamente.")


