import streamlit as st
import pandas as pd
import numpy as np

# Cargar datos desde Excel
@st.cache_data
def cargar_datos():
    df = pd.read_excel("SED 01980S.xlsx")
    df["Hora"] = pd.to_datetime(df["Starttime"]).dt.time
    df["I_Avg"] = df[["I1Avg", "I2Avg", "I3Avg"]].mean(axis=1)
    df["I_Norm"] = df["I_Avg"] / df["I_Avg"].max()
    return df

df = cargar_datos()

# Interfaz
st.title("Simulador de Corriente Promedio")
hora = st.time_input("Selecciona una hora de medición:")
corriente = st.number_input("Corriente medida en esa hora (A):", min_value=0.0)

# Buscar y calcular factor
if st.button("Estimar corriente en otra hora"):
    fila = df[df["Hora"] == hora]
    if not fila.empty:
        factor = fila["I_Norm"].values[0]
        st.success(f"Factor de la hora seleccionada: {factor:.2f}")
        nueva_hora = st.time_input("Selecciona otra hora:")
        fila_nueva = df[df["Hora"] == nueva_hora]
        if not fila_nueva.empty:
            factor_nuevo = fila_nueva["I_Norm"].values[0]
            corriente_estim = corriente * (factor_nuevo / factor)
            st.info(f"Corriente estimada en {nueva_hora}: {corriente_estim:.2f} A")
    else:
        st.warning("Hora no encontrada en los datos")

# Mostrar rango de horas pico
umbral = 0.9 * df["I_Norm"].max()
horas_pico = df[df["I_Norm"] >= umbral]
st.subheader("Rango de horas pico (≥ 90% de la corriente máxima):")
st.dataframe(horas_pico[["Hora", "I_Avg"]])
