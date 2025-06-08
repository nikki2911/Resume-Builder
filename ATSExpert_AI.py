
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
from datetime import date, timedelta,datetime, timezone
from generate_response import generatedResponse
import json

load_dotenv()

GOOGLE_APPLICATION_CREDENTIALS = "resume-builder-460911-f564a03eaac0.json"

# Initialize Firebase Admin SDK (only once)
if not firebase_admin._apps:
    # Check if the app is already initialized to avoid re-initialization errors
    # When running locally, use the service account key file:
    cred = credentials.Certificate(GOOGLE_APPLICATION_CREDENTIALS)
    firebase_admin.initialize_app(cred)
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
        .where('type', '==', "generated_data") # Assuming your Gemini responses fall under a specific type

    docs = query.stream()
    count = 0
    for doc in docs:
        count += 1
    return count

def add_data(user_id,de_dulpicate_key, data):
    history_ref = db.collection('users').document(user_id).collection('history')
    query = history_ref.where(f'data.overall_enhanced_resume_sections.{de_dulpicate_key}', '==', data["overall_enhanced_resume_sections"][de_dulpicate_key])
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
def login_screen():
    st.header("This app is private.")
    st.subheader("Please log in.")
    with stylable_container(
            key="login_button",
            css_styles="""
                button {
                    background-color: #3683ff;
                    color: white;
                    border-radius: 4px;
                    border: None;
                }
                button:hover {
                    background-color: #003891;
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
        st.button("Log in with Google", on_click=st.login)

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

if not st.user.is_logged_in:
    login_screen()
else:
    DAILY_RESPONSE_LIMIT = 3
    col1, col2 = st.columns([7,1])
    with col1:
        st.subheader(f"Welcome, {st.user.name}")

    with col2:
        st.button("Log out", on_click=st.logout)
    st.header("ATSExpert AI", divider="gray")
    # text_model_flash = load_models()

    st.markdown("**Unlock the ATS, Unlock your Career!**")
    # st.button("Log out", on_click=st.logout)
    # --- Check Daily Limit Here ---
    current_daily_count = get_daily_response_count(st.user.sub)
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
                                    "original_text":{
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
                                    "original_text":{
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
                                    "original_text":{
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
                client = Client(api_key=os.environ.get("API_KEY"))
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
                # response = {'current_ats_score': 65,
                #             'overall_enhanced_resume_sections':
                #                 {'summary_or_objective':
                #                      {'original_text': 'Python Developer with 1 year of experience in web '
                #                                        'development and Al-powered solutions using Django and ChatGPT '
                #                                        'API. Passionate about web development, automation, and Al.',
                #                       'suggested_text': 'Proficient Python Developer with 1 year of experience in '
                #                                         'developing and maintaining ML/CV pipelines and applications. '
                #                                         'Solid understanding of Machine Learning concepts and experience '
                #                                         'with ML frameworks (e.g., TensorFlow, PyTorch, scikit-learn). '
                #                                         'Practical experience in Computer Vision, including techniques such '
                #                                         'as image segmentation, feature extraction, object detection, '
                #                                         'and recognition.'},
                #                  'experience': [
                #                      {'original_text': 'Developed an Al-powered Applicant Tracking System (ATS) using Django.',
                #                       'suggested_text': 'Developed and maintained Python-based ML/CV pipelines and applications '
                #                                         'using Django, enhancing the Applicant Tracking System (ATS).'},
                #                      {'original_text': 'Integrated Azure for cloud deployment to ensure scalability and '
                #                                        'reliability.',
                #                       'suggested_text': 'Deployed models into production environments using Azure, '
                #                                         'ensuring scalability and reliability.'}],
                #                  'skills': [
                #                      {'original_text': 'Al & Data Analysis: ChatGPT API, Data Visualization, NLP (SpaCy), Pandas',
                #                       'suggested_text': 'Machine Learning: TensorFlow, PyTorch, scikit-learn. Computer Vision: Image'
                #                                         ' segmentation, feature extraction, object detection, and recognition.'},
                #                      {'original_text': 'Cloud & Deployment: Azure',
                #                       'suggested_text': 'Cloud Platforms: Azure. Containerization: Docker.'},
                #                      {'original_text': 'Programming Languages : Python, C, MATLAB, Verilog HDL',
                #                       'suggested_text': 'Programming Languages: Python, NumPy, OpenCV, Pandas.'}],
                #                  'projects': [
                #                      {'original_text': 'Integrated ChatGPT API for candidate analysis reports with interactive '
                #                                        'data visualization.',
                #                       'suggested_text': 'Designed and implemented computer vision algorithms for tasks like '
                #                                         'object detection, tracking, image classification, OCR, etc. '
                #                                         'Integrated ChatGPT API for candidate analysis reports with '
                #                                         'interactive data visualization.'}]}}

                if response:
                    st.markdown(":green[Response Generated!:white_check_mark:]")


                    response = json.loads(response.text)  # dict
                    # # response1 = json.dumps(json_response, indent=2)
                    # st.text(response)
                    # print(type(response1))
                    de_dulpicate_key = generatedResponse(response)
                        # st.write("Objectives : ", response['overall_enhanced_resume_sections']['projects'])
                    add_data(st.user.sub,de_dulpicate_key, response)
                    logging.info(response)


                # with first_tab2:
                #     st.text(prompt)
        else :
            st.warning("Please Enter Resume and Job Description to Proceed.")