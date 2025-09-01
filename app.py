import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np
import base64

from streamlit_folium import st_folium
import geopandas as gpd
import folium

st.set_page_config(layout="wide")

# ======= Encabezado con Logo =======

logo_path = "data/logo-blanco.png"  

st.markdown(
    f"""
    <div style="text-align: center;">
        <img src="data:image/png;base64,{base64.b64encode(open(logo_path, "rb").read()).decode()}" width="160"/>
        <h1 style="margin-top: 8px; color: #2F56A6;">Visualización y estimación de Sistemas Eléctricos de Distribución</h1>
    </div>
    """,
    unsafe_allow_html=True
)
    
# ======= Menú Horizontal =======
menu_options = {
    "Diagramas": "#diagramas",
    "Datos": "#datos",
    "Calculadora": "#calculadora"
}

st.markdown("""
    <style>
    .menu-container {
        display: flex;
        justify-content: center;
        gap: 50px;
        background-color: #2F56A6;
        padding: 10px;
        border-radius: 8px;
    }
    .menu-container a {
        text-decoration: none;
        font-weight: bold;
        color: white;
        font-size: 18px;
    }
    .menu-container a:hover {
        color: #F7C948;
    }
    </style>
    <div class="menu-container">
        <a href="#diagramas">Diagramas</a>
        <a href="#datos">Datos</a>
        <a href="#calculadora">Calculadora</a>
    </div>
""", unsafe_allow_html=True)

#FORMATO DE LA SELECCION DE CAJA

st.markdown("""
    <style>
    div[data-baseweb="select"] > div {
        background-color: #DFF5E1 !important;
        border-radius: 8px !important;
        border: 1px solid #74A84C !important;
    }
    </style>
""", unsafe_allow_html=True)

# ================== CARGA DE ARCHIVOS ==================
DATA_DIR = "data"
archivos_sed = [f for f in os.listdir(DATA_DIR) if f.endswith(".xlsx")]
sed_opciones = {archivo.replace(".xlsx", "").replace("_", " "): archivo for archivo in archivos_sed}
sed_seleccionada = st.selectbox("Selecciona la SED:", list(sed_opciones.keys()))
archivo_cargado = os.path.join(DATA_DIR, sed_opciones[sed_seleccionada])

df = pd.read_excel(archivo_cargado)
df['starttime'] = pd.to_datetime(df['starttime'])
df['Fecha'] = df['starttime'].dt.date
df['HoraMinuto'] = df['starttime'].dt.strftime('%H:%M')
df['I_Total'] = (df['I1Avg'] + df['I2Avg'] + df['I3Avg'])
df['I_Promedio'] = df['I_Total'] / 3
df['V_Total'] = (df['U1Avg'] + df['U2Avg'] + df['U3Avg']) / 3

def normalizar_dia(grupo):
    max_corriente = grupo['I_Total'].max()
    grupo['I_Norm'] = grupo['I_Total'] / max_corriente
    return grupo

df_norm = df.groupby('Fecha', group_keys=False).apply(normalizar_dia)

curva_promedio = df_norm.groupby('HoraMinuto')['I_Norm'].mean().reset_index()
curva_I_prom = df.groupby('HoraMinuto')['I_Total'].mean().reset_index()
curva_V_prom = df.groupby('HoraMinuto')['V_Total'].mean().reset_index()

# DIAGRAMAS

st.markdown('''
    <h2 id="calculadora" style="
        color: black; 
        background-color: #FFE45C; 
        padding: 14px 24px; 
        border-radius: 10px; 
        font-size: 18px;
    ">
        Diagramas
    </h2>
''', unsafe_allow_html=True)

# Curva normalizada principal

st.subheader("Curva normalizada")
fig1, ax1 = plt.subplots(figsize=(12, 5))
ax1.plot(curva_promedio['HoraMinuto'], curva_promedio['I_Norm'], label='Corriente Normalizada')
ax1.set_title('Factores normalizados')
ax1.set_xlabel('Hora')
ax1.set_ylabel('Corriente Normalizada')
ax1.grid(True)

# Espaciado en el eje X
import numpy as np
xticks = curva_promedio['HoraMinuto'].iloc[::3]  # Mostrar cada hora
ax1.set_xticks(np.arange(len(curva_promedio))[::3])
ax1.set_xticklabels(xticks, rotation=45)

plt.xticks(rotation=90)
st.pyplot(fig1)

# Corriente promedio por hora y Voltaje promedio por hora juntos
col1, col2 = st.columns(2)

with col1:
    
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.plot(
        curva_I_prom['HoraMinuto'], 
        curva_I_prom['I_Total']/3, 
        color='#FF9800', linewidth=2.2, marker='o', markersize=3
    )

    # Estilo
    ax2.set_title('Corriente Promedio', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Corriente (A)', fontsize=12)

    ax2.grid(axis='y', linestyle='--', alpha=0.6)   # solo líneas horizontales
    ax2.set_facecolor("#fafafa")                    # fondo claro

    # Eje X cada 2 horas
    xticks_I = curva_I_prom['HoraMinuto'].iloc[::6]
    ax2.set_xticks(np.arange(len(curva_I_prom))[::6])
    ax2.set_xticklabels(xticks_I, rotation=45, ha='right')

    plt.tight_layout()
    st.pyplot(fig2)

with col2:
    st.subheader("Voltaje promedio por hora")
    fig3, ax3 = plt.subplots(figsize=(6, 4))
    ax3.plot(curva_V_prom['HoraMinuto'], curva_V_prom['V_Total'], color='green')
    ax3.set_title('Voltaje Promedio')
    ax3.set_xlabel('Hora')
    ax3.set_ylabel('Voltaje (V)')
    ax3.grid(True)

    xticks_V = curva_V_prom['HoraMinuto'].iloc[::6]  # cada hora
    ax3.set_xticks(np.arange(len(curva_V_prom))[::6])
    ax3.set_xticklabels(xticks_V, rotation=45)

    plt.tight_layout()
    st.pyplot(fig3)
# DATOS

st.markdown('''
    <h2 id="calculadora" style="
        color: black; 
        background-color: #FFE45C; 
        padding: 14px 24px; 
        border-radius: 10px; 
        font-size: 18px;
    ">
        Datos
    </h2>
''', unsafe_allow_html=True)

corriente_max_promedio = df['I_Promedio'].max()

curva_I_prom['I_Promedio'] = curva_I_prom['I_Total'] / 3
I_promedio_max = curva_I_prom['I_Promedio'].max()
umbral_pico = 0.92 * I_promedio_max
# Filtrar horas pico
horas_pico = curva_I_prom[curva_I_prom['I_Promedio'] >= umbral_pico]['HoraMinuto'].tolist()

st.markdown("<br>", unsafe_allow_html=True)
st.info("Corriente máxima promedio alcanzada")
st.write(f"{corriente_max_promedio:.2f} A")

# Función para agrupar en rangos [inicio – fin]
def agrupar_rangos(horas, intervalo=10):
    rangos = []
    if not horas:
        return rangos

    # Convertir a datetime y ordenar
    horas_dt = sorted([pd.to_datetime(h, format="%H:%M") for h in horas])

    inicio = horas_dt[0]
    fin = horas_dt[0]

    for i in range(1, len(horas_dt)):
        # Diferencia en minutos con el anterior
        diff = (horas_dt[i] - horas_dt[i-1]).seconds / 60
        if diff == intervalo:  # sigue siendo consecutivo
            fin = horas_dt[i]
        else:
            # cerrar el rango anterior
            rangos.append(f"[{inicio.strftime('%H:%M')} – {fin.strftime('%H:%M')}]")
            # nuevo rango
            inicio = horas_dt[i]
            fin = horas_dt[i]

    # Agregar el último rango
    rangos.append(f"[{inicio.strftime('%H:%M')} – {fin.strftime('%H:%M')}]")
    return rangos

if horas_pico:
    rangos = agrupar_rangos(horas_pico, intervalo=10)  # ⬅️ aquí pones 5, 10, 15 según tu data
    st.info("Rangos de horas pico:")
    st.write(", ".join(rangos))
else:
    st.warning("No se encontraron horas pico con corriente promedio ≥ 90% del valor máximo.")
# CALCULADORA

st.markdown('''
    <h2 id="calculadora" style="
        color: black; 
        background-color: #FFE45C; 
        padding: 14px 24px; 
        border-radius: 10px; 
        font-size: 18px;
    ">
        Calculadora
    </h2>
''', unsafe_allow_html=True)

from scipy import stats

hora_medida = st.text_input("Hora de medición (formato HH:MM)", value="09:00")
corriente_medida = st.number_input("Corriente medida en esa hora (A)", value=100.0)
hora_objetivo = st.text_input("Hora a estimar la corriente (formato HH:MM)", value="19:00")

try:
    # extraer valores normalizados de los 7 días para ambas horas
    valores_medida = df_norm[df_norm['HoraMinuto'] == hora_medida].sort_values('Fecha')['I_Norm'].values
    valores_objetivo = df_norm[df_norm['HoraMinuto'] == hora_objetivo].sort_values('Fecha')['I_Norm'].values

    if len(valores_medida) == 0 or len(valores_objetivo) == 0:
        raise IndexError

    # ratios diarios (objetivo / medida)
    ratios = valores_objetivo / valores_medida

    # media y desviación estándar
    media_ratio = np.mean(ratios)
    desv_std = np.std(ratios, ddof=1)
    n = len(ratios)

    # intervalo de confianza con t-student
    t_val = stats.t.ppf(0.975, n-1)
    ic_inf = media_ratio - t_val * (desv_std / np.sqrt(n))
    ic_sup = media_ratio + t_val * (desv_std / np.sqrt(n))

    # aplicar al valor medido
    I_estimado = corriente_medida * media_ratio
    I_estimado_inf = corriente_medida * ic_inf
    I_estimado_sup = corriente_medida * ic_sup

    # resultados
    st.success(f"Estimación de corriente a las {hora_objetivo}: **{I_estimado:.2f} A**")
    st.info(f"Intervalo de confianza 95%: [{I_estimado_inf:.2f}, {I_estimado_sup:.2f}] A")

except IndexError:
    st.error("Una de las horas ingresadas no se encuentra en los datos.")


# ================== CLASIFICACIÓN POR FORMA DE CURVA (HEURÍSTICO) ==================
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('''
    <h2 id="clasificacion" style="
        color: black; 
        background-color: #FFE45C; 
        padding: 14px 24px; 
        border-radius: 10px; 
        font-size: 18px;
    ">
        Clasificación por forma de curva
    </h2>
''', unsafe_allow_html=True)

# Asegurar orden por hora
curva_ord = curva_promedio.sort_values("HoraMinuto").reset_index(drop=True)
serie = curva_ord["I_Norm"].values
horas = curva_ord["HoraMinuto"].values

# Helpers para promedios por franja horaria
def mean_range(df_horas, df_vals, h_ini, h_fin):
    h = pd.to_datetime(df_horas, format="%H:%M").time
    t_ini = pd.to_datetime(h_ini, format="%H:%M").time()
    t_fin = pd.to_datetime(h_fin, format="%H:%M").time()
    mask = (pd.Series(h) >= t_ini) & (pd.Series(h) <= t_fin)
    if mask.sum() == 0:
        return np.nan
    return float(np.nanmean(np.where(mask, df_vals, np.nan)))

mean_all = float(np.mean(serie))             # promedio del día normalizado
max_val = float(np.max(serie))               # pico normalizado (≈1)
peak_idx = int(np.argmax(serie))
peak_hour = horas[peak_idx]

# Features por franjas (ajusta rangos si tus datos cambian)
mean_madrugada = mean_range(horas, serie, "00:00", "05:59")
mean_maniana   = mean_range(horas, serie, "06:00", "10:59")
mean_laboral   = mean_range(horas, serie, "09:00", "17:59")
mean_tarde     = mean_range(horas, serie, "15:00", "17:59")
mean_noche     = mean_range(horas, serie, "18:00", "22:59")

# Indicadores de forma
load_factor   = mean_all / max_val if max_val > 0 else np.nan   # qué tan "plana" es la curva
std_shape     = float(np.std(serie))                             # dispersión/peakedness
ratio_noche   = mean_noche / mean_all if mean_all > 0 else np.nan
ratio_madrug  = mean_madrugada / mean_all if mean_all > 0 else np.nan
ratio_laboral = mean_laboral / mean_all if mean_all > 0 else np.nan
ratio_maniana = mean_maniana / mean_all if mean_all > 0 else np.nan

# Heurística de reglas (umbral ajustables según tu red/SED)
def clasificar_por_curva(peak_hour, load_factor, std_shape, r_noche, r_madrug, r_laboral, r_maniana):
    # Industrial: curva plana, actividad 24h (madrugada ~ diurna), poco pico
    if (load_factor >= 0.80) and (r_madrug >= 0.75) and (std_shape <= 0.12):
        return "Industrial"

    # Comercial: fuerte en horario laboral, bajo en noche/madrugada, pico diurno
    peak_h = pd.to_datetime(peak_hour, format="%H:%M").hour
    if (9 <= peak_h <= 17) and (r_laboral >= 1.10) and (r_madrug <= 0.70) and (load_factor >= 0.60):
        return "Comercial"

    # Residencial: pico vespertino/nocturno, baja madrugada, load factor más bajo
    if (18 <= peak_h <= 22) and (r_noche >= 1.15) and (r_madrug <= 0.65) and (load_factor <= 0.70):
        return "Residencial"

    # Si no encaja perfecto, decide por el mayor "ratio" dominante
    scores = {
        "Residencial": (r_noche or 0) - (r_madrug or 0),
        "Comercial": (r_laboral or 0) - (r_madrug or 0),
        "Industrial": load_factor - (std_shape or 0)
    }
    return max(scores, key=scores.get)

categoria = clasificar_por_curva(
    peak_hour, load_factor, std_shape, ratio_noche, ratio_madrug, ratio_laboral, ratio_maniana
)

# Mostrar resultados

colA, colB, colC = st.columns(3)

with colA:
    st.markdown(
        f"""
        <div style="background:#f9f9f9; padding:12px; border-radius:10px; text-align:center;">
            <h4 style="margin:0; color:#444;">Categoría</h4>
            <p style="font-size:20px; font-weight:bold; color:#2c7;">{categoria}</p>
        </div>
        """, unsafe_allow_html=True
    )

with colB:
    st.markdown(
        f"""
        <div style="background:#f9f9f9; padding:12px; border-radius:10px; text-align:center;">
            <h4 style="margin:0; color:#444;">Hora pico</h4>
            <p style="font-size:20px; font-weight:bold; color:#2c7;">{peak_hour}</p>
        </div>
        """, unsafe_allow_html=True
    )

with colC:
    st.markdown(
        f"""
        <div style="background:#f9f9f9; padding:12px; border-radius:10px; text-align:center;">
            <h4 style="margin:0; color:#444;">Factor de carga</h4>
            <p style="font-size:20px; font-weight:bold; color:#2c7;">{load_factor:.2f}</p>
        </div>
        """, unsafe_allow_html=True
    )
# ===== Ratios visuales =====
st.write("### Ratios por franja horaria")

st.progress(min(ratio_noche/2, 1.0))
st.caption(f"Noche/Media: {ratio_noche:.2f}")

st.progress(min(ratio_laboral/2, 1.0))
st.caption(f"Laboral/Media: {ratio_laboral:.2f}")

st.progress(min(ratio_madrug/2, 1.0))
st.caption(f"Madrugada/Media: {ratio_madrug:.2f}")

st.progress(min(std_shape/0.5, 1.0))
st.caption(f"Desviación forma: {std_shape:.2f}")

# ===== Nota informativa =====
st.markdown(
    """
    <div style="
        background-color:#e8f5e9;
        border-left: 6px solid #43a047;
        padding: 10px;
        border-radius:8px;
        margin-top:15px;
    ">
        <strong>Metodología usada:</strong><br>
        • <b>Residencial</b> → pico noche y baja madrugada <br>
        • <b>Comercial</b> → fuerte en 9–18 <br>
        • <b>Industrial</b> → curva plana con actividad 24h
    </div>
    """,
    unsafe_allow_html=True
)
