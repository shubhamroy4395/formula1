#!/usr/bin/env python3
"""
Streamlit page to display Formula 1 circuit information.
Part of the F1 Paddock by Shubham app.
"""

import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import os
import json
from PIL import Image
from io import BytesIO

# Configure page
st.set_page_config(
    page_title="F1 Circuits | F1 Paddock by Shubham",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Current F1 Circuits for 2025 season based on Wikipedia data
CURRENT_CIRCUITS = [
    {"name": "Albert Park Circuit", "location": "Melbourne, Australia", "wiki_name": "Albert_Park_Circuit"},
    {"name": "Shanghai International Circuit", "location": "Shanghai, China", "wiki_name": "Shanghai_International_Circuit"},
    {"name": "Suzuka Circuit", "location": "Suzuka, Japan", "wiki_name": "Suzuka_Circuit"},
    {"name": "Bahrain International Circuit", "location": "Sakhir, Bahrain", "wiki_name": "Bahrain_International_Circuit"},
    {"name": "Jeddah Corniche Circuit", "location": "Jeddah, Saudi Arabia", "wiki_name": "Jeddah_Corniche_Circuit"},
    {"name": "Miami International Autodrome", "location": "Miami, USA", "wiki_name": "Miami_International_Autodrome"},
    {"name": "Imola Circuit", "location": "Imola, Italy", "wiki_name": "Imola_Circuit"},
    {"name": "Circuit de Monaco", "location": "Monte Carlo, Monaco", "wiki_name": "Circuit_de_Monaco"},
    {"name": "Circuit de Barcelona-Catalunya", "location": "Barcelona, Spain", "wiki_name": "Circuit_de_Barcelona-Catalunya"},
    {"name": "Circuit Gilles Villeneuve", "location": "Montreal, Canada", "wiki_name": "Circuit_Gilles_Villeneuve"},
    {"name": "Red Bull Ring", "location": "Spielberg, Austria", "wiki_name": "Red_Bull_Ring"},
    {"name": "Silverstone Circuit", "location": "Silverstone, UK", "wiki_name": "Silverstone_Circuit"},
    {"name": "Circuit de Spa-Francorchamps", "location": "Spa, Belgium", "wiki_name": "Circuit_de_Spa-Francorchamps"},
    {"name": "Hungaroring", "location": "Budapest, Hungary", "wiki_name": "Hungaroring"},
    {"name": "Circuit Zandvoort", "location": "Zandvoort, Netherlands", "wiki_name": "Circuit_Zandvoort"},
    {"name": "Monza Circuit", "location": "Monza, Italy", "wiki_name": "Monza_Circuit"},
    {"name": "Baku City Circuit", "location": "Baku, Azerbaijan", "wiki_name": "Baku_City_Circuit"},
    {"name": "Marina Bay Street Circuit", "location": "Singapore", "wiki_name": "Marina_Bay_Street_Circuit"},
    {"name": "Circuit of the Americas", "location": "Austin, USA", "wiki_name": "Circuit_of_the_Americas"},
    {"name": "Autódromo Hermanos Rodríguez", "location": "Mexico City, Mexico", "wiki_name": "Autódromo_Hermanos_Rodríguez"},
    {"name": "Interlagos Circuit", "location": "São Paulo, Brazil", "wiki_name": "Interlagos_Circuit"},
    {"name": "Las Vegas Strip Circuit", "location": "Las Vegas, USA", "wiki_name": "Las_Vegas_Strip_Circuit"},
    {"name": "Lusail International Circuit", "location": "Lusail, Qatar", "wiki_name": "Lusail_International_Circuit"},
    {"name": "Yas Marina Circuit", "location": "Abu Dhabi, UAE", "wiki_name": "Yas_Marina_Circuit"}
]

# Path for storing circuit data
CIRCUIT_DATA_DIR = "circuit_data"
os.makedirs(CIRCUIT_DATA_DIR, exist_ok=True)

# Apply Spotify-inspired dark theme CSS with F1 red accents
st.markdown("""
<style>
    /* Spotify-like dark mode theme */
    .stApp {
        background-color: #000000 !important;
        color: #FFFFFF !important;
    }
    
    /* F1 colors */
    :root {
        --f1-red: #FF1801;
    }
    
    /* Heading styling */
    h1 {
        color: #FFFFFF !important;
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        margin-bottom: 1.5rem !important;
        letter-spacing: -0.04em !important;
    }
    
    h1:after {
        content: "";
        display: block;
        width: 80px;
        height: 4px;
        background-color: var(--f1-red);
        margin-top: 8px;
    }
    
    h2 {
        color: #FFFFFF !important;
        font-size: 1.8rem !important;
        font-weight: 700 !important;
        margin-top: 2rem !important;
        margin-bottom: 1rem !important;
    }
    
    h3 {
        color: #FFFFFF !important;
        font-size: 1.5rem !important;
        font-weight: 700 !important;
    }
    
    /* Card styling */
    .circuit-card {
        background-color: #181818;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 16px;
        transition: background-color 0.3s ease;
        border: 1px solid #282828;
        cursor: pointer;
    }
    
    .circuit-card:hover {
        background-color: #282828;
        border-color: var(--f1-red);
    }
    
    /* Detail card */
    .circuit-detail-card {
        background-color: #181818;
        border-radius: 8px;
        padding: 20px;
        border: 1px solid #282828;
        margin-bottom: 20px;
    }
    
    /* Spotify-like section headers */
    .section-header {
        font-size: 1.1rem;
        color: #B3B3B3;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 12px;
    }
    
    /* Labels */
    .info-label {
        color: #B3B3B3;
        font-size: 0.9rem;
        margin-bottom: 4px;
    }
    
    /* Values */
    .info-value {
        color: white;
        font-size: 1rem;
        margin-bottom: 16px;
    }
    
    /* Red buttons */
    .stButton>button {
        background-color: var(--f1-red) !important;
        color: white !important;
        border: none !important;
        border-radius: 500px !important;
        padding: 8px 16px !important;
        font-weight: 600 !important;
    }
    
    /* Image styling */
    img {
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

def fetch_circuit_image(circuit_name):
    """Fetch circuit image from Wikipedia"""
    image_path = os.path.join(CIRCUIT_DATA_DIR, f"{circuit_name.replace(' ', '_')}.jpg")
    
    # If image already downloaded, use local file
    if os.path.exists(image_path):
        return Image.open(image_path)
        
    # Otherwise fetch from Wikipedia
    try:
        url = f"https://en.wikipedia.org/wiki/{circuit_name}"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the infobox image
        infobox = soup.find('table', {'class': 'infobox'})
        if infobox:
            img_tag = infobox.find('img')
            if img_tag and 'src' in img_tag.attrs:
                img_url = img_tag['src']
                if not img_url.startswith('http'):
                    img_url = f"https:{img_url}"
                
                # Download and save image
                img_response = requests.get(img_url)
                img = Image.open(BytesIO(img_response.content))
                img.save(image_path)
                return img
        
        # Fall back to a generic circuit image if not found
        return None
    except Exception as e:
        st.error(f"Error fetching image for {circuit_name}: {e}")
        return None

def fetch_circuit_data(circuit_wiki_name):
    """Fetch circuit data from Wikipedia"""
    data_path = os.path.join(CIRCUIT_DATA_DIR, f"{circuit_wiki_name}.json")
    
    # If data already downloaded, use local file
    if os.path.exists(data_path):
        with open(data_path, 'r') as f:
            return json.load(f)
    
    # Otherwise fetch from Wikipedia
    try:
        url = f"https://en.wikipedia.org/wiki/{circuit_wiki_name}"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract info from the infobox
        infobox = soup.find('table', {'class': 'infobox'})
        circuit_data = {
            "name": circuit_wiki_name.replace('_', ' '),
            "description": "",
            "location": "",
            "length": "",
            "turns": "",
            "lap_record": "",
            "opened": "",
            "capacity": "",
            "facts": []
        }
        
        if infobox:
            rows = infobox.find_all('tr')
            for row in rows:
                header = row.find('th')
                value = row.find('td')
                if header and value:
                    header_text = header.get_text().strip().lower()
                    value_text = value.get_text().strip()
                    
                    if 'length' in header_text:
                        circuit_data["length"] = value_text
                    elif 'opened' in header_text or 'built' in header_text:
                        circuit_data["opened"] = value_text
                    elif 'capacity' in header_text:
                        circuit_data["capacity"] = value_text
                    elif 'turns' in header_text or 'corners' in header_text:
                        circuit_data["turns"] = value_text
                    elif 'lap record' in header_text:
                        circuit_data["lap_record"] = value_text
                    elif 'location' in header_text:
                        circuit_data["location"] = value_text
        
        # Extract the main description
        content_div = soup.find('div', {'class': 'mw-parser-output'})
        if content_div:
            paragraphs = content_div.find_all('p')
            for p in paragraphs:
                text = p.get_text().strip()
                if text and len(text) > 100:  # Take the first substantial paragraph
                    circuit_data["description"] = text
                    break
        
        # Extract some interesting facts
        if content_div:
            list_items = content_div.find_all('li')
            facts = []
            for item in list_items:
                text = item.get_text().strip()
                if len(text) > 30 and len(text) < 200:  # Exclude too short or too long items
                    facts.append(text)
            circuit_data["facts"] = facts[:5]  # Take top 5 facts
        
        # Save data to file
        with open(data_path, 'w') as f:
            json.dump(circuit_data, f)
        
        return circuit_data
        
    except Exception as e:
        st.error(f"Error fetching data for {circuit_wiki_name}: {e}")
        return {
            "name": circuit_wiki_name.replace('_', ' '),
            "description": "Information not available at this time.",
            "facts": []
        }

def display_circuit_list():
    """Display the list of circuits"""
    st.title("Formula 1 Circuits")
    
    st.markdown("""
    <div style="background-color: #181818; border-radius: 8px; padding: 16px; margin-bottom: 20px; border: 1px solid #282828;">
        <p>Explore the current Formula 1 circuits for the 2025 season. Click on any circuit to learn more about its history, layout, and interesting facts.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create a 3-column layout for circuit cards
    cols = st.columns(3)
    
    for i, circuit in enumerate(CURRENT_CIRCUITS):
        col = cols[i % 3]
        with col:
            # Create a clickable card for each circuit
            st.markdown(f"""
            <div class="circuit-card" onclick="window.location.href='?circuit={circuit['wiki_name']}'">
                <h3>{circuit['name']}</h3>
                <p>{circuit['location']}</p>
            </div>
            """, unsafe_allow_html=True)

def display_circuit_detail(circuit_wiki_name):
    """Display detailed information about a specific circuit"""
    # Find the circuit in our list
    circuit = next((c for c in CURRENT_CIRCUITS if c['wiki_name'] == circuit_wiki_name), None)
    
    if not circuit:
        st.error("Circuit not found")
        return
    
    # Fetch detailed circuit data
    circuit_data = fetch_circuit_data(circuit_wiki_name)
    
    # Back button
    if st.button("← Back to all circuits"):
        st.experimental_set_query_params()
        st.experimental_rerun()
    
    # Header with circuit name
    st.title(circuit['name'])
    
    # Layout with columns for image and basic info
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Circuit image
        image = fetch_circuit_image(circuit_wiki_name)
        if image:
            st.image(image, use_column_width=True)
        else:
            st.info("Circuit image not available")
    
    with col2:
        # Circuit information card
        st.markdown("""
        <div class="section-header">Circuit Information</div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="circuit-detail-card">
            <div class="info-label">Location</div>
            <div class="info-value">{circuit_data.get('location', circuit['location'])}</div>
            
            <div class="info-label">Track Length</div>
            <div class="info-value">{circuit_data.get('length', 'Not available')}</div>
            
            <div class="info-label">Number of Turns</div>
            <div class="info-value">{circuit_data.get('turns', 'Not available')}</div>
            
            <div class="info-label">Lap Record</div>
            <div class="info-value">{circuit_data.get('lap_record', 'Not available')}</div>
            
            <div class="info-label">Opened</div>
            <div class="info-value">{circuit_data.get('opened', 'Not available')}</div>
            
            <div class="info-label">Capacity</div>
            <div class="info-value">{circuit_data.get('capacity', 'Not available')}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Circuit description
    st.markdown("""
    <div class="section-header">About</div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="circuit-detail-card">
        <p>{circuit_data.get('description', 'Information not available')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Interesting facts
    if circuit_data.get('facts'):
        st.markdown("""
        <div class="section-header">Interesting Facts</div>
        """, unsafe_allow_html=True)
        
        fact_html = "<div class='circuit-detail-card'><ul>"
        for fact in circuit_data.get('facts', []):
            fact_html += f"<li>{fact}</li>"
        fact_html += "</ul></div>"
        
        st.markdown(fact_html, unsafe_allow_html=True)

def main():
    # Get query parameters to see if a specific circuit is selected
    query_params = st.experimental_get_query_params()
    selected_circuit = query_params.get("circuit", [None])[0]
    
    if selected_circuit:
        display_circuit_detail(selected_circuit)
    else:
        display_circuit_list()

if __name__ == "__main__":
    main() 