import streamlit as st
import pandas as pd
import datetime

# Configuration of the page
st.set_page_config(
    page_title="Informe Email Marketing",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Data Initialization
if 'campaign_data' not in st.session_state:
    st.session_state.campaign_data = pd.DataFrame(
        columns=['date', 'month', 'subject', 'enviados', 'aceptados', 'omitidos', 'tasa_aceptacion']
    )
    st.session_state.observations = {}
if 'company_name' not in st.session_state:
    st.session_state.company_name = "Fisiofitness Bilbao"
if 'logo_url' not in st.session_state:
    st.session_state.logo_url = "https://tugimnasioes.com/wp-content/uploads/MPG_logo-blanco-fondo-transparente-1-1.png"
if 'primary_color' not in st.session_state:
    st.session_state.primary_color = "#A58A73"

# Function to add new campaign data
def add_new_campaign(campaign_date, subject, aceptados, omitidos):
    # 'Enviados' is calculated by adding 'Aceptados' and 'Omitidos'
    enviados = aceptados + omitidos
    tasa_aceptacion = (aceptados / enviados) * 100 if enviados > 0 else 0
    new_campaign = {
        'date': campaign_date.strftime('%Y-%m-%d'),
        'month': campaign_date.strftime('%B').lower(),
        'subject': subject,
        'enviados': enviados,
        'aceptados': aceptados,
        'omitidos': omitidos,
        'tasa_aceptacion': round(tasa_aceptacion, 2)
    }
    st.session_state.campaign_data = pd.concat([st.session_state.campaign_data, pd.DataFrame([new_campaign])], ignore_index=True)
    if new_campaign['month'] not in st.session_state.observations:
        st.session_state.observations[new_campaign['month']] = ""

# Main Dashboard
st.sidebar.header("Opciones de Visualización")

# Dynamic Company and Logo Inputs
st.sidebar.subheader("Personalizar Informe")
st.session_state.company_name = st.sidebar.text_input("Nombre de la empresa", value=st.session_state.company_name)
st.session_state.logo_url = st.sidebar.text_input("URL del logo de la empresa", value=st.session_state.logo_url)
st.session_state.primary_color = st.sidebar.color_picker("Selecciona un color principal", value=st.session_state.primary_color)

# Dynamic month filter
unique_months = sorted(st.session_state.campaign_data['month'].unique())
selected_months = st.sidebar.multiselect(
    "Selecciona el(los) mes(es):",
    options=unique_months,
    default=unique_months
)
if not selected_months:
    st.warning("Selecciona al menos un mes para ver los datos.")
    filtered_df = pd.DataFrame()
else:
    filtered_df = st.session_state.campaign_data[st.session_state.campaign_data['month'].isin(selected_months)]

st.sidebar.header("Agregar Nueva Campaña")
with st.sidebar.form(key='add_campaign_form'):
    new_date = st.date_input("Fecha", datetime.date.today())
    new_subject = st.text_input("Asunto")
    new_aceptados = st.number_input("Aceptados", min_value=0, step=1)
    new_omitidos = st.number_input("Omitidos", min_value=0, step=1)
    submit_button = st.form_submit_button("Agregar Campaña")
    if submit_button:
        if new_subject:
            add_new_campaign(new_date, new_subject, new_aceptados, new_omitidos)
            st.success("Campaña agregada exitosamente!")
        else:
            st.error("El asunto de la campaña es obligatorio.")

# Dynamic Header
st.markdown(f"""
    <div style='text-align: center;'>
        <img src='{st.session_state.logo_url}' alt='Logo de la empresa' style='height: 100px; object-fit: contain; margin-bottom: 10px;'>
    </div>
    <h1 style='text-align: center;'>Informe Interactivo de Email Marketing</h1>
""", unsafe_allow_html=True)
date_range = ""
if not st.session_state.campaign_data.empty:
    first_month = st.session_state.campaign_data['month'].iloc[0].capitalize()
    last_month = st.session_state.campaign_data['month'].iloc[-1].capitalize()
    year = datetime.datetime.now().year
    if first_month == last_month:
        date_range = f"| {first_month} {year}"
    else:
        date_range = f"| {first_month} - {last_month} {year}"

st.markdown(f"<h3 style='text-align: center; color: {st.session_state.primary_color};'>{st.session_state.company_name} {date_range}</h3>", unsafe_allow_html=True)

# KPI section
st.header("Resumen del Período")
kpi_cols = st.columns(4)

total_campaigns = len(filtered_df)
total_enviados = filtered_df['enviados'].sum() if not filtered_df.empty else 0
total_aceptados = filtered_df['aceptados'].sum() if not filtered_df.empty else 0
avg_tasa_aceptacion = (total_aceptados / total_enviados) * 100 if total_enviados > 0 else 0

kpi_cols[0].metric("Campañas Enviadas", total_campaigns)
kpi_cols[1].metric("Emails Enviados", f"{total_enviados:,.0f}")
kpi_cols[2].metric("Emails Aceptados", f"{total_aceptados:,.0f}")
kpi_cols[3].metric("Tasa de Aceptación", f"{avg_tasa_aceptacion:.2f}%")

# Chart section
st.header("Análisis de Campañas")
st.markdown("Este gráfico compara el volumen de correos aceptados frente a los omitidos para cada campaña.")
if not filtered_df.empty:
    st.bar_chart(filtered_df.set_index('subject')[['aceptados', 'omitidos']])
else:
    st.info("Agrega datos de una campaña para ver el gráfico.")

# Detailed data table with edit/delete functionality
st.subheader("Datos Detallados de Campañas")
if not filtered_df.empty:
    edited_df = st.data_editor(filtered_df, num_rows="dynamic", use_container_width=True, column_config={
        "date": st.column_config.DateColumn("Fecha"),
        "subject": st.column_config.TextColumn("Asunto"),
        "enviados": st.column_config.NumberColumn("Enviados"),
        "aceptados": st.column_config.NumberColumn("Aceptados"),
        "omitidos": st.column_config.NumberColumn("Omitidos"),
        "tasa_aceptacion": st.column_config.NumberColumn("Tasa de Aceptación")
    })
    st.session_state.campaign_data = st.session_state.campaign_data[~st.session_state.campaign_data.index.isin(filtered_df.index)]
    st.session_state.campaign_data = pd.concat([st.session_state.campaign_data, edited_df], ignore_index=False)
    st.session_state.campaign_data.reset_index(drop=True, inplace=True)
else:
    st.info("No hay campañas para mostrar. Utiliza la barra lateral para agregar una nueva.")

st.header("Observaciones")
current_observations_value = st.session_state.observations.get(' '.join(selected_months), "")
st.text_area(
    "Escribe aquí las observaciones para el reporte actual:",
    value=current_observations_value,
    height=200,
    key="obs_textarea",
    on_change=lambda: st.session_state.observations.update({' '.join(selected_months): st.session_state.obs_textarea})
)
st.session_state.observations[' '.join(selected_months)] = st.session_state.obs_textarea

st.markdown("---")
st.header("Conclusión y Recomendaciones")
if not filtered_df.empty:
    st.markdown("Las campañas de email marketing de {st.session_state.company_name} han tenido un rendimiento excepcional en términos de entrega. Los altos porcentajes de correos electrónicos aceptan que la lista de contactos está saludable y bien mantenida, con un mínimo de direcciones inexistentes o inaccesibles.")
    st.markdown(f"""
    <p style="font-weight: 600; color: {st.session_state.primary_color};">Recomendaciones:</p>
    <ul style="list-style-type: disc; margin-left: 20px;">
        <li>Continuar con la segmentación de la audiencia para personalizar aún más el contenido.</li>
        <li>Analizar las métricas de apertura y clics para entender qué tipos de contenido generan mayor interacción.</li>
        <li>Mantener limpia lista de contactos para asegurar altas tasas de entrega a futuro.</li>
    </ul>
    """, unsafe_allow_html=True)
else:
    st.markdown("Carga tus datos de campaña para ver la conclusión y las recomendaciones.")
