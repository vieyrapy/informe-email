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
if 'conclusions' not in st.session_state:
    st.session_state.conclusions = ""
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
    # Set the new month as the default selection to show the latest data
    st.session_state.selected_months = [new_campaign['month']]

# Main Dashboard
st.sidebar.header("Opciones de Visualización")

# Dynamic Company and Logo Inputs
st.sidebar.subheader("Personalizar Informe")
st.session_state.company_name = st.sidebar.text_input("Nombre de la empresa", value=st.session_state.company_name)
st.session_state.logo_url = st.sidebar.text_input("URL del logo de la empresa", value=st.session_state.logo_url)
st.session_state.primary_color = st.sidebar.color_picker("Selecciona un color principal", value=st.session_state.primary_color)

# Dynamic month filter
unique_months = sorted(st.session_state.campaign_data['month'].unique())
if 'selected_months' not in st.session_state:
    st.session_state.selected_months = unique_months
selected_months = st.sidebar.multiselect(
    "Selecciona el(los) mes(es):",
    options=unique_months,
    default=st.session_state.selected_months
)
st.session_state.selected_months = selected_months

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
    filtered_data_for_title = st.session_state.campaign_data[st.session_state.campaign_data['month'].isin(selected_months)]
    if not filtered_data_for_title.empty:
        # Sort by date to get the first and last month correctly
        filtered_data_for_title = filtered_data_for_title.sort_values(by='date')
        first_month_name = datetime.datetime.strptime(filtered_data_for_title['month'].iloc[0], "%B").strftime("%B").capitalize()
        last_month_name = datetime.datetime.strptime(filtered_data_for_title['month'].iloc[-1], "%B").strftime("%B").capitalize()
        year = datetime.datetime.now().year
        if first_month_name == last_month_name:
            date_range = f"| {first_month_name} {year}"
        else:
            date_range = f"| {first_month_name} - {last_month_name} {year}"

st.markdown(f"<h3 style='text-align: center; color: {st.session_state.primary_color};'>{st.session_state.company_name} {date_range}</h3>", unsafe_allow_html=True)

# Filtering data based on selection
if not selected_months:
    st.warning("Selecciona al menos un mes para ver los datos.")
    filtered_df = pd.DataFrame()
else:
    filtered_df = st.session_state.campaign_data[st.session_state.campaign_data['month'].isin(selected_months)]

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
    # Convert 'date' column to datetime objects before displaying
    filtered_df['date'] = pd.to_datetime(filtered_df['date'])
    edited_df = st.data_editor(filtered_df, num_rows="dynamic", use_container_width=True, column_config={
        "date": st.column_config.DateColumn("Fecha"),
        "subject": st.column_config.TextColumn("Asunto"),
        "enviados": st.column_config.NumberColumn("Enviados"),
        "aceptados": st.column_config.NumberColumn("Aceptados"),
        "omitidos": st.column_config.NumberColumn("Omitidos"),
        "tasa_aceptacion": st.column_config.NumberColumn("Tasa de Aceptación")
    })
    # This block handles row additions, deletions, and edits
    new_data = st.session_state.campaign_data[~st.session_state.campaign_data.index.isin(filtered_df.index)]
    updated_data = pd.concat([new_data, edited_df], ignore_index=False)
    st.session_state.campaign_data = updated_data.reset_index(drop=True)
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
# Update observations in session state
st.session_state.observations[' '.join(selected_months)] = st.session_state.obs_textarea

# Conclusión and Recomendaciones section is now fully dynamic and editable
st.header("Conclusión y Recomendaciones")
current_conclusions_value = st.session_state.conclusions
st.text_area(
    "Escribe aquí la conclusión y las recomendaciones:",
    value=current_conclusions_value,
    height=200,
    key="conclusions_textarea",
    on_change=lambda: st.session_state.update({'conclusions': st.session_state.conclusions_textarea})
)
st.session_state.conclusions = st.session_state.conclusions_textarea
