import streamlit as st
import pandas as pd
import datetime

# Configuration of the page
st.set_page_config(
    page_title="Informe Email Marketing",
    layout="wide",
    initial_sidebar_state="expanded"
)

# App Title and Header with Logo
st.markdown("<h1 style='text-align: center;'>Informe Interactivo de Email Marketing</h1>", unsafe_allow_html=True)
logo_url = "https://tugimnasioes.com/wp-content/uploads/MPG_logo-blanco-fondo-transparente-1-1.png"
st.markdown(f"<div style='text-align: center;'><img src='{logo_url}' alt='Logo' style='height: 100px;'></div>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #A58A73;'>Fisiofitness Bilbao | Julio - Agosto 2025</h3>", unsafe_allow_html=True)

# Data Initialization
if 'campaign_data' not in st.session_state:
    st.session_state.campaign_data = pd.DataFrame(
        columns=['month', 'date', 'updatedOn', 'subject', 'total', 'accepted', 'skipped', 'accepted_rate']
    )
    st.session_state.observations = {}

# Function to add new campaign data
def add_new_campaign(subject, accepted, skipped):
    total = accepted + skipped
    accepted_rate = (accepted / total) * 100 if total > 0 else 0
    new_campaign = {
        'month': datetime.datetime.now().strftime('%B').lower(),
        'date': datetime.datetime.now().strftime('%d-%m-%Y'),
        'updatedOn': datetime.datetime.now().strftime('%b %d, %Y %I:%M %p'),
        'subject': subject,
        'total': total,
        'accepted': accepted,
        'skipped': skipped,
        'accepted_rate': round(accepted_rate, 2)
    }
    st.session_state.campaign_data = pd.concat([st.session_state.campaign_data, pd.DataFrame([new_campaign])], ignore_index=True)
    if new_campaign['month'] not in st.session_state.observations:
        st.session_state.observations[new_campaign['month']] = ""

# Main Dashboard
st.sidebar.header("Opciones de Visualización")
# Dynamic month filter
unique_months = sorted(st.session_state.campaign_data['month'].unique())
month_options = ['ambos'] + unique_months
month_filter = st.sidebar.selectbox(
    "Selecciona el mes:",
    month_options,
    index=0
)

st.sidebar.header("Agregar Nueva Campaña")
with st.sidebar.form(key='add_campaign_form'):
    new_subject = st.text_input("Asunto de la campaña")
    new_accepted = st.number_input("Emails Aceptados", min_value=0, step=1)
    new_skipped = st.number_input("Emails Saltados", min_value=0, step=1)
    submit_button = st.form_submit_button("Agregar Campaña")
    if submit_button:
        if new_subject:
            add_new_campaign(new_subject, new_accepted, new_skipped)
            st.success("Campaña agregada exitosamente!")
        else:
            st.error("El asunto de la campaña es obligatorio.")

st.sidebar.header("Observaciones")
current_observations_value = st.session_state.observations.get(month_filter, "")
current_observations = st.text_area(
    "Escribe aquí las observaciones para el reporte actual:",
    value=current_observations_value,
    height=200,
    key=f"obs_textarea_{month_filter}"
)
if current_observations != current_observations_value:
    st.session_state.observations[month_filter] = current_observations


# Filtering data based on selection
if month_filter == 'ambos':
    filtered_df = st.session_state.campaign_data
else:
    filtered_df = st.session_state.campaign_data[st.session_state.campaign_data['month'] == month_filter]

# KPI section
st.header("Resumen del Período")
kpi_cols = st.columns(4)

total_campaigns = len(filtered_df)
total_emails = filtered_df['total'].sum() if not filtered_df.empty else 0
total_accepted = filtered_df['accepted'].sum() if not filtered_df.empty else 0
avg_acceptance_rate = (total_accepted / total_emails) * 100 if total_emails > 0 else 0

kpi_cols[0].metric("Campañas Enviadas", total_campaigns)
kpi_cols[1].metric("Emails Totales", f"{total_emails:,.0f}")
kpi_cols[2].metric("Emails Aceptados", f"{total_accepted:,.0f}")
kpi_cols[3].metric("Tasa de Aceptación", f"{avg_acceptance_rate:.2f}%")

# Chart section
st.header("Análisis de Campañas")
st.markdown("Este gráfico compara el volumen de correos aceptados frente a los saltados para cada campaña.")
if not filtered_df.empty:
    st.bar_chart(filtered_df.set_index('subject')[['accepted', 'skipped']])
else:
    st.info("Agrega datos de una campaña para ver el gráfico.")

# Detailed data table with edit/delete functionality
st.subheader("Datos Detallados de Campañas")
edited_df = st.data_editor(filtered_df, num_rows="dynamic", use_container_width=True)
st.session_state.campaign_data = st.session_state.campaign_data[~st.session_state.campaign_data.index.isin(filtered_df.index)]
st.session_state.campaign_data = pd.concat([st.session_state.campaign_data, edited_df], ignore_index=False)
st.session_state.campaign_data.reset_index(drop=True, inplace=True)

st.header("Observaciones")
st.write(current_observations)

st.markdown("---")
st.header("Conclusión y Recomendaciones")
if not filtered_df.empty:
    st.markdown("Las campañas de email marketing de Fisiofitness Bilbao han tenido un rendimiento excepcional en términos de entrega. Los altos porcentajes de correos electrónicos aceptados demuestran que la lista de contactos está saludable y bien mantenida, con un mínimo de direcciones inexistentes o inaccesibles.")
else:
    st.markdown("Carga tus datos de campaña para ver la conclusión y las recomendaciones.")
