import streamlit as st
import pandas as pd
import os

RUTA_RUTAS = "rutas_guardadas.csv"

st.title("🔁 Simulador de Vuelta Redonda")

def safe_number(x):
    return 0 if (x is None or (isinstance(x, float) and pd.isna(x))) else x

if os.path.exists(RUTA_RUTAS):
    df = pd.read_csv(RUTA_RUTAS)

    impo_rutas = df[df["Tipo"] == "IMPO"].copy()
    expo_rutas = df[df["Tipo"] == "EXPO"].copy()
    vacio_rutas = df[df["Tipo"] == "VACIO"].copy()

    st.subheader("📌 Paso 1: Selecciona tipo de ruta principal")
    tipo_principal = st.selectbox("Tipo principal", ["IMPO", "EXPO"])

    ruta_principal = None
    ruta_vacio = None
    ruta_secundaria = None
    rutas_seleccionadas = []

    if tipo_principal == "IMPO":
        rutas_unicas = impo_rutas[["Origen", "Destino"]].drop_duplicates()
        opciones_ruta = list(rutas_unicas.itertuples(index=False, name=None))
        ruta_sel = st.selectbox("Selecciona ruta IMPO", opciones_ruta, format_func=lambda x: f"{x[0]} → {x[1]}")
        origen, destino = ruta_sel
        candidatas = impo_rutas[(impo_rutas["Origen"] == origen) & (impo_rutas["Destino"] == destino)].copy()
        candidatas["Utilidad"] = candidatas["Ingreso Total"] - candidatas["Costo_Total_Ruta"]
        candidatas["% Utilidad"] = (candidatas["Utilidad"] / candidatas["Ingreso Total"] * 100).round(2)
        candidatas = candidatas.sort_values(by="% Utilidad", ascending=False)
        sel = st.selectbox("Cliente (ordenado por % utilidad)", candidatas.index,
                           format_func=lambda x: f"{candidatas.loc[x, 'Cliente']} ({candidatas.loc[x, '% Utilidad']:.2f}%)")
        ruta_principal = candidatas.loc[sel]
        rutas_seleccionadas.append(ruta_principal)

        destino_ref = ruta_principal["Destino"]
        vacios = vacio_rutas[vacio_rutas["Origen"] == destino_ref].copy()
        st.markdown("---")
        st.subheader("📌 Paso 2: Ruta VACÍA sugerida (opcional)")
        if not vacios.empty:
            vacio_idx = st.selectbox("Ruta VACÍA (Origen = " + destino_ref + ")", vacios.index,
                                     format_func=lambda x: f"{vacios.loc[x, 'Origen']} → {vacios.loc[x, 'Destino']}")
            ruta_vacio = vacios.loc[vacio_idx]
            rutas_seleccionadas.append(ruta_vacio)

        st.markdown("---")
        st.subheader("📌 Paso 3: Ruta EXPO sugerida (opcional)")
        origen_expo = ruta_vacio["Destino"] if ruta_vacio is not None else destino_ref
        candidatos = expo_rutas[expo_rutas["Origen"] == origen_expo].copy()
        if not candidatos.empty:
            candidatos["Utilidad"] = candidatos["Ingreso Total"] - candidatos["Costo_Total_Ruta"]
            candidatos["% Utilidad"] = (candidatos["Utilidad"] / candidatos["Ingreso Total"] * 100).round(2)
            candidatos = candidatos.sort_values(by="% Utilidad", ascending=False)
            expo_idx = st.selectbox("Ruta EXPO sugerida", candidatos.index,
                                    format_func=lambda x: f"{candidatos.loc[x, 'Cliente']} - {candidatos.loc[x, 'Origen']} → {candidatos.loc[x, 'Destino']} ({candidatos.loc[x, '% Utilidad']:.2f}%)")
            ruta_secundaria = candidatos.loc[expo_idx]
            rutas_seleccionadas.append(ruta_secundaria)

    else:  # EXPO
        rutas_unicas = expo_rutas[["Origen", "Destino"]].drop_duplicates()
        opciones_ruta = list(rutas_unicas.itertuples(index=False, name=None))
        ruta_sel = st.selectbox("Selecciona ruta EXPO", opciones_ruta, format_func=lambda x: f"{x[0]} → {x[1]}")
        origen, destino = ruta_sel
        candidatas = expo_rutas[(expo_rutas["Origen"] == origen) & (expo_rutas["Destino"] == destino)].copy()
        candidatas["Utilidad"] = candidatas["Ingreso Total"] - candidatas["Costo_Total_Ruta"]
        candidatas["% Utilidad"] = (candidatas["Utilidad"] / candidatas["Ingreso Total"] * 100).round(2)
        candidatas = candidatas.sort_values(by="% Utilidad", ascending=False)
        sel = st.selectbox("Cliente (ordenado por % utilidad)", candidatas.index,
                           format_func=lambda x: f"{candidatas.loc[x, 'Cliente']} ({candidatas.loc[x, '% Utilidad']:.2f}%)")
        ruta_principal = candidatas.loc[sel]
        rutas_seleccionadas.append(ruta_principal)

        destino_ref = ruta_principal["Destino"]
        vacios = vacio_rutas[vacio_rutas["Origen"] == destino_ref].copy()
        st.markdown("---")
        st.subheader("📌 Paso 2: Ruta VACÍA sugerida (opcional)")
        if not vacios.empty:
            vacio_idx = st.selectbox("Ruta VACÍA (Origen = " + destino_ref + ")", vacios.index,
                                     format_func=lambda x: f"{vacios.loc[x, 'Origen']} → {vacios.loc[x, 'Destino']}")
            ruta_vacio = vacios.loc[vacio_idx]
            rutas_seleccionadas.append(ruta_vacio)

        st.markdown("---")
        st.subheader("📌 Paso 3: Ruta IMPO sugerida (opcional)")
        origen_impo = ruta_vacio["Destino"] if ruta_vacio is not None else destino_ref
        candidatos = impo_rutas[impo_rutas["Origen"] == origen_impo].copy()
        if not candidatos.empty:
            candidatos["Utilidad"] = candidatos["Ingreso Total"] - candidatos["Costo_Total_Ruta"]
            candidatos["% Utilidad"] = (candidatos["Utilidad"] / candidatos["Ingreso Total"] * 100).round(2)
            candidatos = candidatos.sort_values(by="% Utilidad", ascending=False)
            impo_idx = st.selectbox("Ruta IMPO sugerida", candidatos.index,
                                    format_func=lambda x: f"{candidatos.loc[x, 'Cliente']} - {candidatos.loc[x, 'Origen']} → {candidatos.loc[x, 'Destino']} ({candidatos.loc[x, '% Utilidad']:.2f}%)")
            ruta_secundaria = candidatos.loc[impo_idx]
            rutas_seleccionadas.append(ruta_secundaria)

    # 🔁 Simulación y visualización
    if st.button("🚛 Simular Vuelta Redonda"):
        ingreso_total = sum(safe_number(r.get("Ingreso Total", 0)) for r in rutas_seleccionadas)
        costo_total_general = sum(safe_number(r.get("Costo_Total_Ruta", 0)) for r in rutas_seleccionadas)

        utilidad_bruta = ingreso_total - costo_total_general
        costos_indirectos = ingreso_total * 0.35
        utilidad_neta = utilidad_bruta - costos_indirectos
        pct_bruta = (utilidad_bruta / ingreso_total * 100) if ingreso_total > 0 else 0
        pct_neta = (utilidad_neta / ingreso_total * 100) if ingreso_total > 0 else 0


       st.subheader("🧾 Detalle de Rutas")
        for ruta in rutas_seleccionadas:
            st.markdown(f"""
            **{ruta['Tipo']} — {ruta['Cliente']}**  
            - {ruta['Origen']} → {ruta['Destino']}  
            - Ingreso Total: ${safe_number(ruta['Ingreso Total']):,.2f}  
            - Costo Total Ruta: ${safe_number(ruta['Costo_Total_Ruta']):,.2f}
            """)

        utilidad_bruta = ingreso_total - costo_total_general
        costos_indirectos = ingreso_total * 0.35
        utilidad_neta = utilidad_bruta - costos_indirectos
        porcentaje_utilidad_bruta = (utilidad_bruta / ingreso_total * 100) if ingreso_total > 0 else 0
        porcentaje_utilidad_neta = (utilidad_neta / ingreso_total * 100) if ingreso_total > 0 else 0

        st.markdown("---")
        st.subheader("📊 Resultado General")

        st.markdown(f"<strong>Ingreso Total:</strong> <span style='font-weight:bold'>${ingreso_total:,.2f}</span>", unsafe_allow_html=True)
        st.markdown(f"<strong>Costo Total:</strong> <span style='font-weight:bold'>${costo_total_general:,.2f}</span>", unsafe_allow_html=True)

        color_utilidad_bruta = "green" if utilidad_bruta >= 0 else "red"
        st.markdown(f"<strong>Utilidad Bruta:</strong> <span style='color:{color_utilidad_bruta}; font-weight:bold'>${utilidad_bruta:,.2f}</span>", unsafe_allow_html=True)

        color_porcentaje_bruta = "green" if porcentaje_utilidad_bruta >= 50 else "red"
        st.markdown(f"<strong>% Utilidad Bruta:</strong> <span style='color:{color_porcentaje_bruta}; font-weight:bold'>{porcentaje_utilidad_bruta:.2f}%</span>", unsafe_allow_html=True)

        st.markdown(f"<strong>Costos Indirectos (35%):</strong> <span style='font-weight:bold'>${costos_indirectos:,.2f}</span>", unsafe_allow_html=True)

        color_utilidad_neta = "green" if utilidad_neta >= 0 else "red"
        st.markdown(f"<strong>Utilidad Neta:</strong> <span style='color:{color_utilidad_neta}; font-weight:bold'>${utilidad_neta:,.2f}</span>", unsafe_allow_html=True)

        color_porcentaje_neta = "green" if porcentaje_utilidad_neta >= 15 else "red"
        st.markdown(f"<strong>% Utilidad Neta:</strong> <span style='color:{color_porcentaje_neta}; font-weight:bold'>{porcentaje_utilidad_neta:.2f}%</span>", unsafe_allow_html=True)

        st.markdown("---")
        st.subheader("📋 Resumen de Rutas")

        col1, col2, col3 = st.columns(3)

        def resumen_ruta(r):
            return [
                f"KM: {safe_number(r.get('KM')):,.2f}",
                f"Diesel Camión: ${safe_number(r.get('Costo_Diesel_Camion')):,.2f}",
                f"Diesel Termo: ${safe_number(r.get('Costo_Diesel_Termo')):,.2f}",
                f"Sueldo: ${safe_number(r.get('Sueldo_Operador')):,.2f}",
                f"Casetas: ${safe_number(r.get('Casetas')):,.2f}",
                f"Costo Cruce Convertido: ${safe_number(r.get('Costo Cruce Convertido')):,.2f}",
                "**Extras detallados:**",
                f"Lavado Termo: ${safe_number(r.get('Lavado_Termo')):,.2f}",
                f"Movimiento Local: ${safe_number(r.get('Movimiento_Local')):,.2f}",
                f"Puntualidad: ${safe_number(r.get('Puntualidad')):,.2f}",
                f"Pensión: ${safe_number(r.get('Pension')):,.2f}",
                f"Estancia: ${safe_number(r.get('Estancia')):,.2f}",
                f"Fianza Termo: ${safe_number(r.get('Fianza_Termo')):,.2f}",
                f"Renta Termo: ${safe_number(r.get('Renta_Termo')):,.2f}"
            ]

        with col1:
            st.markdown("**IMPO**")
            for line in resumen_ruta(ruta_impo):
                st.write(line)

        with col2:
            st.markdown("**VACÍO**")
            if ruta_vacio is not None:
                for line in resumen_ruta(ruta_vacio):
                    st.write(line)
            else:
                st.write("No aplica")

        with col3:
            st.markdown("**EXPO**")
            for line in resumen_ruta(ruta_expo):
                st.write(line)

else:
    st.warning("⚠️ No hay rutas guardadas todavía.")
