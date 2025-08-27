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
    st.session_state.campaign_data = pd.DataFrame([
        {'month': 'julio', 'date': '07-07-2025', 'updatedOn': 'Jul 16, 2025 12:23 PM', 'subject': 'Te torciste el tobillo...', 'total': 4016, 'accepted': 3995, 'skipped': 21, 'accepted_rate': 84.44},
        {'month': 'julio', 'date': '17-07-2025', 'updatedOn': 'Jul 29, 2025 08:21 AM', 'subject': '¿Y si pruebas una forma distinta de entrenar?', 'total': 4016, 'accepted': 3930, 'skipped': 86, 'accepted_rate': 97.63},
        {'month': 'julio', 'date': '23-07-2025', 'updatedOn': 'Jul 24, 2025 07:47 AM', 'subject': 'Este verano, toca desconectar...', 'total': 4016, 'accepted': 3925, 'skipped': 91, 'accepted_rate': 97.44},
        {'month': 'julio', 'date': '24-07-2025', 'updatedOn': 'Jul 29, 2025 08:21 AM', 'subject': '¿Tienes fibromialgia?', 'total': 4015, 'accepted': 3922, 'skipped': 93, 'accepted_rate': 97.38},
        {'month': 'agosto', 'date': '08-08-2025', 'updatedOn': 'Aug 13, 2025 09:37 AM', 'subject': '¿Tu rodilla aún no está al 100%?', 'total': 4015, 'accepted': 3866, 'skipped': 149, 'accepted_rate': 95.99},
        {'month': 'agosto', 'date': '18-08-2025', 'updatedOn': 'Aug 27, 2025 06:31 AM', 'subject': '¿Sin dolor? Tu cuerpo está pidiendo atención', 'total': 4016, 'accepted': 3853, 'skipped': 163, 'accepted_rate': 95.69},
    ])
    st.session_state.observations = {
        'julio': """Durante julio, se realizaron cuatro envíos. La tasa de aceptación promedio fue muy alta, superando el 95% en la mayoría de los casos.

Dato relevante:
La campaña del 7 de julio tuvo la tasa de aceptación más baja (84.44%). Sería recomendable analizar su contenido, aunque el resultado sigue siendo muy positivo.

En general, los resultados de julio indican una excelente calidad en la lista de contactos, con una tasa de éxito de entrega consistentemente alta.""",
        'agosto': """En agosto se continuó con los envíos, manteniendo un rendimiento sólido en términos de entrega.

Las campañas de agosto mostraron una alta tasa de aceptación, lo que confirma la efectividad en la entrega y la calidad de la lista de contactos.

Las tasas de "saltados" se mantuvieron en niveles bajos y controlados.""",
        'ambos': """El rendimiento general en ambos meses ha sido excepcional. Los altos porcentajes de correos aceptados demuestran que la lista de contactos está saludable y bien mantenida.

Las tasas de "saltados" se mantuvieron en niveles bajos y controlados durante todo el período.

---

Recomendaciones:
- Continuar con la segmentación de la audiencia para personalizar aún más el contenido.
- Analizar las métricas de apertura y clics para entender qué tipos de contenido generan mayor interacción.
- Mantener limpia lista de contactos para asegurar altas tasas de entrega a futuro."""
    }

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

# Main Dashboard
st.sidebar.header("Opciones de Visualización")
month_filter = st.sidebar.selectbox(
    "Selecciona el mes:",
    ("ambos", "julio", "agosto"),
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
current_observations = st.text_area(
    "Escribe aquí las observaciones para el reporte actual:",
    value=st.session_state.observations.get(month_filter, ""),
    height=200
)

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
st.bar_chart(filtered_df.set_index('subject')[['accepted', 'skipped']])

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
st.markdown("Las campañas de email marketing de Fisiofitness Bilbao durante julio y agosto han tenido un rendimiento excepcional en términos de entrega. Los altos porcentajes de correos electrónicos aceptados demuestran que la lista de contactos está saludable y bien mantenida, con un mínimo de direcciones inexistentes o inaccesibles.")
