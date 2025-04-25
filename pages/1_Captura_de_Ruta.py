import streamlit as st
import pandas as pd
import os

st.title("# Captura de Nueva Ruta")

FILE = "rutas_guardadas.csv"
DATOS = "datos_generales.csv"

def load_datos_generales():
    if os.path.exists(DATOS):
        return pd.read_csv(DATOS).set_index("Parametro").to_dict()["Valor"]
    return {}

if os.path.exists(FILE):
    df = pd.read_csv(FILE)
else:
    df = pd.DataFrame(columns=[
        "Tipo", "Cliente", "Origen", "Destino", "KM", "Horas_Termo", "Casetas",
        "Lavado_Termo", "Movimiento_Local", "Puntualidad", "Pension", "Estancia",
        "Fianza_Termo", "Renta_Termo", "Moneda", "Ingreso_Original", "Ingreso_Total",
        "Moneda_Cruce", "Cruce_Original", "Cruce_Total",
        "Costo_Diesel", "Costo_Total"
    ])

datos = load_datos_generales()

st.subheader("Formulario para agregar nueva ruta")

tipo = st.selectbox("Tipo de Ruta", ["IMPO", "EXPO", "VACIO"])
cliente = st.text_input("Nombre del Cliente (opcional para VACIO)")
origen = st.text_input("Origen")
destino = st.text_input("Destino")
km = st.number_input("Kilómetros recorridos", min_value=0.0)
horas_termo = st.number_input("Horas de uso del Termo", min_value=0.0)
casetas = st.number_input("Costo de Casetas (MXN)", min_value=0.0)

# Ingreso
moneda = st.selectbox("Moneda del ingreso", ["MXN", "USD"])
ingreso_original = st.number_input(f"Ingreso en {moneda}", min_value=0.0)
tipo_cambio = float(datos.get(f"Tipo de cambio {moneda}", 1.0))
ingreso_total = ingreso_original * tipo_cambio

# Cruce
moneda_cruce = st.selectbox("Moneda del cruce", ["MXN", "USD"])
cruce_original = st.number_input(f"Costo de Cruce en {moneda_cruce}", min_value=0.0)
tipo_cambio_cruce = float(datos.get(f"Tipo de cambio {moneda_cruce}", 1.0))
cruce_total = cruce_original * tipo_cambio_cruce

# Campos opcionales
lavado_termo = st.number_input("Lavado Termo", min_value=0.0, value=0.0)
mov_local = st.number_input("Movimiento Local", min_value=0.0, value=0.0)
puntualidad = st.number_input("Puntualidad", min_value=0.0, value=0.0)
pension = st.number_input("Pensión", min_value=0.0, value=0.0)
estancia = st.number_input("Estancia", min_value=0.0, value=0.0)
fianza = st.number_input("Fianza Termo Rentado/Externo", min_value=0.0, value=0.0)
renta_termo = st.number_input("Renta de Termo", min_value=0.0, value=0.0)

# Diesel
rendimiento = float(datos.get("Rendimiento Camion", 2.5))
diesel = float(datos.get("Costo Diesel", 24))
costo_diesel = (km / rendimiento) * diesel if rendimiento > 0 else 0

# Total
costos_extra = sum([lavado_termo, mov_local, puntualidad, pension, estancia, fianza, renta_termo])
costo_total = costo_diesel + casetas + costos_extra + cruce_total

# Mostrar resumen
st.write(f"**Ingreso Convertido (MXN):** ${ingreso_total:,.2f}")
st.write(f"**Costo Diesel Estimado:** ${costo_diesel:,.2f}")
st.write(f"**Cruce Convertido (MXN):** ${cruce_total:,.2f}")
st.write(f"**Casetas:** ${casetas:,.2f}")
st.write(f"**Extras:** ${costos_extra:,.2f}")
st.write(f"**Costo Total Calculado:** ${costo_total:,.2f}")

if st.button("Guardar Ruta"):
    nueva_ruta = pd.DataFrame([{
        "Tipo": tipo,
        "Cliente": cliente,
        "Origen": origen,
        "Destino": destino,
        "KM": km,
        "Horas_Termo": horas_termo,
        "Casetas": casetas,
        "Lavado_Termo": lavado_termo,
        "Movimiento_Local": mov_local,
        "Puntualidad": puntualidad,
        "Pension": pension,
        "Estancia": estancia,
        "Fianza_Termo": fianza,
        "Renta_Termo": renta_termo,
        "Moneda": moneda,
        "Ingreso_Original": ingreso_original,
        "Ingreso_Total": ingreso_total,
        "Moneda_Cruce": moneda_cruce,
        "Cruce_Original": cruce_original,
        "Cruce_Total": cruce_total,
        "Costo_Diesel": costo_diesel,
        "Costo_Total": costo_total
    }])
    df = pd.concat([df, nueva_ruta], ignore_index=True)
    df.to_csv(FILE, index=False)
    st.success("✅ La ruta se guardó exitosamente.")
    st.rerun()



