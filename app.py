import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

st.set_page_config(page_title="Estimador de Corriente", layout="wide")

st.title("🔌 Estimación de Corriente con Curva Normalizada")

# 📁 Subir archivo
uploaded_file = st.file_uploader("Sube tu archivo Excel", type=["xlsx"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    
    # Procesar columnas de tiempo
    df['Starttime'] = pd.to_datetime(df['Starttime'])
    df['Fecha'] = df['Starttime'].dt.date
    df['HoraMinuto'] = df['Starttime'].dt.strftime('%H:%M')

    # Corriente total
    df['I_Total'] = df['I1Avg'] + df['I2Avg'] + df['I3Avg']

    # Normalización por día
    def normalizar_dia(grupo):
        max_corriente = grupo['I_Total'].max()
        grupo['I_Norm'] = grupo['I_Total'] / max_corriente
        return grupo

    df_norm = df.groupby('Fecha', group_keys=False).apply(normalizar_dia)

    # Curva promedio
    curva_promedio = df_norm.groupby('HoraMinuto')['I_Norm'].mean().reset_index()

    # 📊 Mostrar gráfica
    st.subheader("📈 Curva Promedio Normalizada")
    fig, ax = plt.subplots(figsize=(12,5))
    ax.plot(curva_promedio['HoraMinuto'], curva_promedio['I_Norm'], color='green')
    ax.set_title('Curva promedio normalizada')
    ax.set_xlabel('Hora')
    ax.set_ylabel('Corriente normalizada')
    ax.tick_params(axis='x', rotation=90)
    ax.grid(True)
    st.pyplot(fig)

    # 🧮 Estimación
    st.subheader("⚙️ Estimación de Corriente")

    hora_medida = st.selectbox("Selecciona la hora de la medición conocida:", curva_promedio['HoraMinuto'])
    corriente_medida = st.number_input("Ingresa la corriente medida (en A):", min_value=0.0, value=100.0)

    hora_objetivo = st.selectbox("Selecciona la hora que quieres estimar:", curva_promedio['HoraMinuto'])

    try:
        R_medida = curva_promedio[curva_promedio['HoraMinuto'] == hora_medida]['I_Norm'].values[0]
        R_objetivo = curva_promedio[curva_promedio['HoraMinuto'] == hora_objetivo]['I_Norm'].values[0]

        I_pico = corriente_medida / R_medida
        I_estimado = I_pico * R_objetivo

        st.success(f"🔋 Corriente pico estimada: **{I_pico:.2f} A**")
        st.success(f"⏰ Corriente estimada a las {hora_objetivo}: **{I_estimado:.2f} A**")

    except IndexError:
        st.error("No se pudo encontrar la hora seleccionada.")

    # 🔍 Horas pico
    st.subheader("🔥 Rango de Horas Pico")

    umbral = 0.90 * curva_promedio['I_Norm'].max()
    horas_pico = curva_promedio[curva_promedio['I_Norm'] >= umbral]

    st.dataframe(horas_pico.rename(columns={'HoraMinuto': 'Hora', 'I_Norm': 'Corriente Normalizada'}))
