import plotly.express as px
import plotly.graph_objects as go
from st_copy_to_clipboard import st_copy_to_clipboard
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import date, timedelta,datetime, timezone
import os
import streamlit as st
from dotenv import load_dotenv
from streamlit_extras.stylable_container import stylable_container
from ATSExpert_AI import login_google_button_ui
from generate_response import generatedResponse
load_dotenv()

GOOGLE_APPLICATION_CREDENTIALS = "resume-builder-460911-f564a03eaac0.json"


if not firebase_admin._apps:
    # Check if the app is already initialized to avoid re-initialization errors
    # When running locally, use the service account key file:
    cred = credentials.Certificate(GOOGLE_APPLICATION_CREDENTIALS)
    firebase_admin.initialize_app(cred)
    # When deployed on Google Cloud, use default credentials:
    # firebase_admin.initialize_app()

db = firestore.client()

def get_user_history(user_id, limit=5):
    if not user_id:
        return []

    history_ref = db.collection('users').document(user_id).collection('history')
    # Order by timestamp descending to get most recent items first
    docs = history_ref.order_by('timestamp', direction=firestore.Query.DESCENDING).limit(limit).stream()
    history_items = []
    for doc in docs:
        item_data = doc.to_dict()
        # Convert Firestore Timestamp to readable format if needed for display

        if 'timestamp' in item_data:
             item_data['timestamp'] = item_data['timestamp'].astimezone().strftime("%Y-%m-%d %H:%M:%S")
        history_items.append(item_data)
    return history_items

def _get_display_name_for_history_item(item_data):
    """
    Generates a readable name for a history item based on its type and data.
    """
    item_type = item_data.get('type', 'Unknown Type')
    timestamp_str = item_data.get('timestamp', 'No Time') # Use the formatted string from get_user_history
    data = item_data.get('data', {})

    input_text = data.get('current_ats_score', 'No Score')
    generated_data = data["overall_enhanced_resume_sections"]["summary_or_objective"].get("suggested_text")
    name_parts =f"ATS Score: {input_text}... Generated : {generated_data[:50]}..." # Truncate for display


    return f"{name_parts} {timestamp_str}"


if not st.login:
    login_google_button_ui()
else:
    user_info = st.user
    user_id = user_info.get("sub")
    history_items = get_user_history(user_id)
    if history_items:
        # Create a list of display names for the selectbox
        display_options = [_get_display_name_for_history_item(item) for item in history_items]

        # Use st.selectbox to allow the user to pick a history item
        selected_option = st.selectbox(
            "Select a history item to view details:",
            options=display_options,
            index=0 # Default to the most recent item (first in the list)
        )

        # Find the actual history item object that was selected
        # We assume the order in display_options matches history_items
        selected_index = display_options.index(selected_option)
        selected_item = history_items[selected_index]

        st.subheader(f"Details for: {selected_option}")

# Format to show only date and time (YYYY-MM-DD HH:MM:SS)

        # Display the full data of the selected item
        st.caption(f"Timestamp: {selected_item.get('timestamp', 'N/A')}")
        generatedResponse(selected_item['data'])

    else:
        st.info("You don't have any history items yet.")