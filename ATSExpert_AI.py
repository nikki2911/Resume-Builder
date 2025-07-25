# Free Tier
# Requests per minute (RPM)
# Requests per day (RPD)
# Tokens per minute (TPM)
# Tokens per day (TPD)

# Model	                RPM	        TPM	            RPD
# Gemini 2.0 Flash	    15	        1,000,000	    1,500

import os
import streamlit as st
import logging
from google.genai import Client
from google.genai.types import Part, GenerationConfig, HarmCategory, HarmBlockThreshold, GenerateContentConfig
from dotenv import load_dotenv
from streamlit_extras.stylable_container import stylable_container
import plotly.express as px
import plotly.graph_objects as go
from st_copy_to_clipboard import st_copy_to_clipboard
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import date, timedelta, datetime, timezone
from generate_response import generatedResponse
import json
import base64

import requests

load_dotenv()

# GOOGLE_APPLICATION_CREDENTIALS = "resume-builder-460911-f564a03eaac0.json"

# Initialize Firebase Admin SDK (only once)
if not firebase_admin._apps:
    base64_creds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    json_str = base64.b64decode(base64_creds).decode("utf-8")
    creds_dict = json.loads(json_str)
    cred = credentials.Certificate(creds_dict)
    firebase_admin.initialize_app(cred)
    # Check if the app is already initialized to avoid re-initialization errors
    # When running locally, use the service account key file:
    # cred = credentials.Certificate(GOOGLE_APPLICATION_CREDENTIALS)
    # firebase_admin.initialize_app(cred)
    # When deployed on Google Cloud, use default credentials:
    # firebase_admin.initialize_app()

db = firestore.client()


# Now you can use the 'db' object to interact with Firestore
# Example:

def get_daily_response_count(user_id):
    """
    Counts the number of history items of a specific type created by a user today (UTC).
    """
    if not user_id:
        return 0

    history_ref = db.collection('users').document(user_id).collection('history')

    # Get the start and end of the current UTC day
    # It's crucial to use UTC to avoid issues with timezones and daily resets
    now_utc = datetime.now(timezone.utc)
    today_start_utc = now_utc.replace(hour=0, minute=0, second=0, microsecond=0)
    # End of day is slightly before next day's start to ensure inclusivity
    today_end_utc = today_start_utc + timedelta(days=1) - timedelta(microseconds=1)

    # Query for documents within today's range and of the specific type
    query = history_ref \
        .where('timestamp', '>=', today_start_utc) \
        .where('timestamp', '<=', today_end_utc) \
        .where('type', '==', "generated_data")  # Assuming your Gemini responses fall under a specific type

    docs = query.stream()
    count = 0
    for doc in docs:
        count += 1
    return count


def add_data(user_id, de_dulpicate_key, data):
    history_ref = db.collection('users').document(user_id).collection('history')
    query = history_ref.where(f'data.overall_enhanced_resume_sections.{de_dulpicate_key}', '==',
                              data["overall_enhanced_resume_sections"][de_dulpicate_key])
    existing_docs = query.limit(1).get()
    if len(existing_docs) > 0:
        print("exist")
        return

    history_ref.add({
        'timestamp': firestore.SERVER_TIMESTAMP,  # Use server timestamp for accuracy
        'data': data,
        'type': "generated_data"
    })


st.set_page_config(
    page_title="ATSExpert AI",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
    # menu_items={
    #     'Get Help': 'https://www.extremelycoolapp.com/help',
    #     'Report a bug': "https://www.extremelycoolapp.com/bug",
    #     'About': "# This is a header. This is an *extremely* cool app!",
    # }
)


# def login_screen():
#     st.header("This app is private.")
#     st.subheader("Please log in.")
#     with stylable_container(
#             key="login_button",
#             css_styles="""
#                 button {
#                     background-color: #3683ff;
#                     color: white;
#                     border-radius: 4px;
#                     border: None;
#                 }
#                 button:hover {
#                     background-color: #003891;
#                     color: white !important;
#                     border: None;
#                 }
#                 button:focus {
#                     background-color: #003891 !important;
#                     color: white !important;
#                     border: None;
#                 }
#                 """,
#     ):
#         st.button("Log in with Google", on_click=st.login)


# --- 2. Google OAuth Credentials from st.secrets ---
# These will come from .streamlit/secrets.toml locally,
# and from environment variables (AUTH_GOOGLE_CLIENT_ID etc.) on Cloud Run.
# try:
#     # Accessing secrets using the section name 'auth' and key names
#     GOOGLE_CLIENT_ID = os.getenv("AUTH_GOOGLE_CLIENT_ID")
#     GOOGLE_CLIENT_SECRET = os.getenv("AUTH_GOOGLE_CLIENT_SECRET")
#     # IMPORTANT: The REDIRECT_URI must match exactly what you set in Google Cloud Console
#     # For local: http://localhost:8501/oauth2callback
#     # For Cloud Run: https://YOUR_CLOUD_RUN_URL/oauth2callback
#     REDIRECT_URI = os.getenv("AUTH_REDIRECT_URI")
# except AttributeError as e:
#     st.error(f"Authentication secrets are missing or malformed in "
#              f".streamlit/secrets.toml (local) or environment variables (Cloud Run). Error: {e}")
#     st.info("Please ensure your secrets.toml has a [auth] section with "
#             "google_client_id, google_client_secret, and redirect_uri.")
#     st.stop()
#
# if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET or not REDIRECT_URI:
#     st.error("Google OAuth credentials (Client ID, Client Secret, or Redirect URI) are not fully set.")
#     st.stop()


# --- 3. Google OAuth Flow Functions ---


# if "user" not in st.session_state:
#     st.session_state.user = None
# if "credentials" not in st.session_state:
#     st.session_state.credentials = None
#
#
# def login_callback():
#     credentials = get_user_credentials(
#         scopes=[
#             "openid",
#             "https://www.googleapis.com/auth/userinfo.email",
#             "https://www.googleapis.com/auth/userinfo.profile",
#         ],
#         client_id=GOOGLE_CLIENT_ID,
#         client_secret=GOOGLE_CLIENT_SECRET,
#         # limit redirect URI server to http://localhost:9000
#         redirect_uri=REDIRECT_URI
#     )
#     id_info = id_token.verify_token(
#         credentials.id_token,
#         requests.Request(),
#     )
#     st.session_state.credentials = credentials
#     st.session_state.user = id_info


# if st.sidebar.button("Logout", type="primary"):
#     st.session_state["user"] = None
#     st.session_state["credentials"] = None
#     st.rerun()


# def get_google_auth_url():
#     """Generates the Google OAuth authorization URL."""
#     return (
#         f"https://accounts.google.com/o/oauth2/auth?"
#         f"client_id={GOOGLE_CLIENT_ID}&"
#         f"redirect_uri={REDIRECT_URI}&"
#         f"response_type=code&"
#         f"scope=email%20profile%20openid&"  # Request basic user info (email, name)
#         f"access_type=offline&"  # Optional: to get refresh token for long-lived access
#         f"prompt=consent"  # Optional: force consent screen each time
#     )
#
#
#
# def exchange_code_for_tokens(auth_code):
#     """Exchanges authorization code for access and ID tokens."""
#     token_url = "https://oauth2.googleapis.com/token"
#     payload = {
#         "code": auth_code,
#         "client_id": GOOGLE_CLIENT_ID,
#         "client_secret": GOOGLE_CLIENT_SECRET,
#         "redirect_uri": REDIRECT_URI,
#         "grant_type": "authorization_code",
#     }
#     headers = {"Content-Type": "application/x-www-form-urlencoded"}
#     response = requests.post(token_url, data=payload, headers=headers)
#     response.raise_for_status()  # Raise an exception for HTTP errors (e.g., 400 Bad Request)
#     return response.json()


# def get_user_info(access_token):
#     """Fetches user profile information using the access token."""
#     userinfo_url = "https://www.googleapis.com/oauth2/v3/userinfo"
#     headers = {"Authorization": f"Bearer {access_token}"}
#     response = requests.get(userinfo_url, headers=headers)
#     response.raise_for_status()  # Raise an exception for HTTP errors
#     return response.json()


def login_google_button_ui():
    """Displays the styled 'Log in with Google' button."""
    st.header("This app is private.")
    st.subheader("Please log in.")
    st.button(
        "🔑 Login with Google",
        on_click=st.login
    )
    # Your custom styling for the button
    # with st.container():  # Use st.container for general styling context
    #     st.markdown(
    #         f"""
    #         <style>
    #         .stButton > button {{
    #             background-color: #3683ff;
    #             color: white;
    #             border-radius: 4px;
    #             border: None;
    #             padding: 10px 20px;
    #             font-size: 16px;
    #             cursor: pointer;
    #         }}
    #         .stButton > button:hover {{
    #             background-color: #003891;
    #             color: white !important; /* Ensure hover color applies */
    #             border: None;
    #         }}
    #         .stButton > button:focus:not(:active) {{ /* Apply focus style only when not active */
    #             background-color: #003891 !important;
    #             color: white !important;
    #             border: None;
    #             box-shadow: 0 0 0 2px #3683ff; /* Example focus ring */
    #         }}
    #         </style>
    #         """,
    #         unsafe_allow_html=True
    #     )
    #     # Display the link which will redirect to Google's auth page
    #     auth_url = get_google_auth_url()
    #     print(auth_url)
    #     st.markdown(f'<a href="{auth_url}" target="_self" style="text-decoration: none;">'
    #                 '<button>'
    #                 'Log in with Google'
    #                 '</button>'
    #                 '</a>', unsafe_allow_html=True)


# --- 4. Main Streamlit App Logic (Authentication & Content Display) ---


# Initialize session state variables if they don't exist
# This manages the login state across reruns
# if "logged_in" not in st.session_state:
#     st.session_state["logged_in"] = False
# if "user_info" not in st.session_state:
#     st.session_state["user_info"] = None
# if "access_token" not in st.session_state:
#     st.session_state["access_token"] = None

# Check for authorization code in URL parameters (after redirect from Google)
# query_params = st.query_params
# auth_code = query_params.get("code")

# if auth_code:
#     # If we received an auth code, try to exchange it for tokens and get user info
#     try:
#         tokens = exchange_code_for_tokens(auth_code)
#         access_token = tokens.get("access_token")
#
#         user_info = get_user_info(access_token)
#
#         st.session_state["user_info"] = user_info
#         st.session_state["logged_in"] = True
#         st.session_state["access_token"] = access_token
#
#         st.success(f"Successfully logged in as {user_info.get('email', 'User')}!")
#
#         # Clear query parameters to prevent re-login loop on refresh
#         st.query_params.clear()
#         st.rerun()  # Re-run the app to reflect the new login state
#
#     except requests.exceptions.RequestException as e:
#         st.error(
#             f"Authentication failed during token exchange or user info fetch. Please check your credentials and network. Error: {e}")
#         st.session_state["logged_in"] = False
#         st.session_state["user_info"] = None
#         st.error("Please try logging in again.")
#         login_google_button_ui()  # Show login button again on failure
#     except Exception as e:
#         st.error(f"An unexpected error occurred during authentication: {e}")
#         st.session_state["logged_in"] = False
#         st.session_state["user_info"] = None
#         st.error("Please try logging in again.")
#         login_google_button_ui()  # Show login button again on failure
# @st.cache_resource
# def load_models():
#     text_model_flash = "gemini-2.0-flash-001"
#     return text_model_flash
#
#
# def get_gemini_flash_text_response(
#     model,
#     contents: str,
#     generation_config: GenerationConfig,
#     stream: bool = True,
# ):
#     safety_settings = {
#         HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
#         HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
#         HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
#         HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
#     }
#
#     responses = model.generate_content(
#         prompt,
#         generation_config=generation_config,
#         safety_settings=safety_settings,
#         stream=stream,
#     )
#
#
#     final_response = []
#     for response in responses:
#         try:
#             # st.write(response.text)
#             final_response.append(response.text)
#         except IndexError:
#             # st.write(response)
#             final_response.append("")
#             continue
#     return " ".join(final_response)
# if not st.session_state.user:
#     login_google_button_ui()
#     st.stop()
# elif not st.session_state["logged_in"]:
#     # User is not logged in and no auth code present, show login button UI
#     login_google_button_ui()

if not st.user.is_logged_in:
    login_google_button_ui()
else:
    user_info = st.user
    user_id = user_info.get("sub")  # This is the unique Google user ID
    user_name = user_info.get("name")  # User's display name

    DAILY_RESPONSE_LIMIT = 3
    col1, col2 = st.columns([7, 1])
    with col1:
        st.subheader(f"Welcome, {user_name}")

    with col2:
        st.button("Log out", on_click=st.logout)
    st.header("ATSExpert AI", divider="gray")
    # text_model_flash = load_models()

    st.markdown("**Unlock the ATS, Unlock your Career!**")
    # st.button("Log out", on_click=st.logout)
    # --- Check Daily Limit Here ---
    current_daily_count = get_daily_response_count(user_id)
    st.info(f"You have generated {current_daily_count} of {DAILY_RESPONSE_LIMIT} responses today.")

    if current_daily_count >= DAILY_RESPONSE_LIMIT:
        st.warning("You have reached your daily limit for responses. Please try again tomorrow!")
        can_generate_response = False
    else:
        can_generate_response = True

    if can_generate_response:

        jd, r_col = st.columns(2)
        with jd:

            job_description = st.text_area(
                "Enter Job Description:  \n\n", key="job_description", value=""
            )
        with r_col:
            resume = st.file_uploader("Upload Your Resume Here", accept_multiple_files=False)
        resume_bytes_data = ""
        if resume is not None:
            # To read file as bytes:
            resume_bytes_data = resume.getvalue()

        # Task 2.5
        # Complete Streamlit framework code for the user interface, add the wine preference radio button to the interface.
        # https://docs.streamlit.io/library/api-reference/widgets/st.radio

        # wine = st.radio( "Select the wine: \n\n",
        #         ["Red", "White", "None"],
        #         key="wine",
        #         horizontal=True,)

        max_output_tokens = 1500

        # Task 2.6
        # Modify this prompt with the custom chef prompt.
        prompt = f""""I need to optimize my resume to maximize its ATS (Applicant Tracking System) 
        compatibility for a given job description.
        Please perform the following:
        Calculate my current ATS score by comparing my provided resume against the given job description.
        Identify specific areas for improvement in my resume's content, focusing on keywords, phrasing, 
        and alignment with the job description.
        For each identified area, provide the exact rephrased or new sentences that would 
        enhance my resume and boost the ATS score.
        """
        response_schema = {
            "type": "OBJECT",
            "properties": {
                "current_ats_score": {
                    "type": "INTEGER",
                    "description": "The ATS compatibility score of the current resume against the job description (e.g., 0-100%)."
                },
                "overall_enhanced_resume_sections": {
                    "type": "OBJECT",
                    "description": "A collection of key resume sections with their enhanced content.",
                    "properties": {
                        "summary_or_objective": {
                            "type": "OBJECT",
                            "description": "original text and enhanced text of objectives",
                            "properties": {
                                "original_text": {
                                    "type": "STRING",
                                    "description": "An example snippet from the original resume text that needs improvement."
                                },
                                "suggested_text": {
                                    "type": "STRING",
                                    "description": "The enhanced summary or objective statement."
                                }
                            }

                        },
                        "experience": {
                            "type": "ARRAY",
                            "description": "An array of original and enhanced job experiences.",
                            "items": {
                                "type": "OBJECT",
                                "properties": {
                                    "original_text": {
                                        "type": "STRING",
                                        "description": "An example snippet of experience from the original resume text that needs improvement."
                                    },
                                    "suggested_text": {
                                        "type": "STRING",
                                        "description": "The enhanced snippet of experience."
                                    }
                                },
                                "required": ["original_text", "suggested_text"]
                            }
                        },
                        "skills": {
                            "type": "ARRAY",
                            "description": "An array of original and enhanced skill bullet points.",
                            "items": {
                                "type": "OBJECT",
                                "properties": {
                                    "original_text": {
                                        "type": "STRING",
                                        "description": "An example snippet of skills from the original resume text that needs improvement."
                                    },
                                    "suggested_text": {
                                        "type": "STRING",
                                        "description": "The enhanced snippet of skills."
                                    }
                                },
                                "required": ["original_text", "suggested_text"]
                            }
                        },
                        "projects": {
                            "type": "ARRAY",
                            "description": "An array of original and enhanced project descriptions, each as a string.",
                            "items": {
                                "type": "OBJECT",
                                "properties": {
                                    "original_text": {
                                        "type": "STRING",
                                        "description": "An example snippet of projects from the original resume text that needs improvement."
                                    },
                                    "suggested_text": {
                                        "type": "STRING",
                                        "description": "The enhanced snippet of projects."
                                    }
                                },
                                "required": ["original_text", "suggested_text"]
                            }
                        }
                    },
                    "required": ["summary_or_objective", "experience", "skills", "projects"]
                }
            },
            "required": ["current_ats_score", "overall_enhanced_resume_sections"]
        }

        with stylable_container(
                key="green_button",
                css_styles="""
                button {
                    background-color: #3683ff;
                    color: white;
                    border-radius: 4px;
                    border: None;
                    margin-bottom: 7px !important;
                }
                button:hover {
                    background-color: #003891 !important;
                    color: white !important;
                    border: None;
                }
                button:focus {
                    background-color: #003891 !important;
                    color: white !important;
                    border: None;
                }
                """,
        ):
            generate_t2t = st.button("Generate Response", key="generate_t2t")

        if (generate_t2t
                and prompt and resume_bytes_data and job_description):
            # st.write(prompt)
            with st.spinner("Generating response using Gemini..."):
                # first_tab1, first_tab2 = st.tabs(["Recipes", "Prompt"])
                # with first_tab1:
                client = Client(api_key=os.getenv("API_KEY"))
                # tokens = client.models.count_tokens(model="gemini-2.0-flash-001", contents=[
                #     Part.from_bytes(data=resume_bytes_data, mime_type="application/pdf"),
                #     job_description,
                #     prompt
                # ])
                # print("tokens", tokens)
                response = client.models.generate_content(model="gemini-2.0-flash-001", contents=[
                    Part.from_bytes(data=resume_bytes_data, mime_type="application/pdf"),
                    job_description,
                    prompt
                ],
                                                          config=GenerateContentConfig(
                                                              response_mime_type="application/json",
                                                              response_schema=response_schema,
                                                              max_output_tokens=1500,
                                                              temperature=0.2
                                                          ))

                if response:
                    st.markdown(":green[Response Generated!:white_check_mark:]")

                    response = json.loads(response.text)  # dict
                    # # response1 = json.dumps(json_response, indent=2)
                    # st.text(response)
                    # print(type(response1))
                    de_dulpicate_key = generatedResponse(response)
                    # st.write("Objectives : ", response['overall_enhanced_resume_sections']['projects'])
                    add_data(user_id, de_dulpicate_key, response)
                    logging.info(response)

                # with first_tab2:
                #     st.text(prompt)
        else:
            st.warning("Please Enter Resume and Job Description to Proceed.")
