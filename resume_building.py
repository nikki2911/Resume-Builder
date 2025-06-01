
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

from datetime import (
    date,
    timedelta,
)
load_dotenv()

st.set_page_config(
    page_title="Ex-stream-ly Cool App",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "# This is a header. This is an *extremely* cool app!",
    }
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
    col1, col2 = st.columns([7,1])
    with col1:
        st.header(f"Welcome, {st.user.name}")

    with col2:
        st.button("Log out", on_click=st.logout)
    st.header("Enhance Resume with Gemini", divider="gray")
    # text_model_flash = load_models()

    st.write("Using Gemini Flash - Text only model")
    st.subheader("AI Resume Enhancer")
    # st.button("Log out", on_click=st.logout)

    # cuisine = st.selectbox(
    #     "What cuisine do you desire?",
    #     ("American", "Chinese", "French", "Indian", "Italian", "Japanese", "Mexican", "Turkish"),
    #     index=None,
    #     placeholder="Select your desired cuisine."
    # )
    #
    # dietary_preference = st.selectbox(
    #     "Do you have any dietary preferences?",
    #     ("Diabetese", "Glueten free", "Halal", "Keto", "Kosher", "Lactose Intolerance", "Paleo", "Vegan", "Vegetarian", "None"),
    #     index=None,
    #     placeholder="Select your desired dietary preference."
    # )

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

    if generate_t2t :
            # and prompt and resume_bytes_data and job_description):
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
            # response = client.models.generate_content(model="gemini-2.0-flash-001", contents=[
            #     Part.from_bytes(data=resume_bytes_data, mime_type="application/pdf"),
            #     job_description,
            #     prompt
            #     ],
            #     config=GenerateContentConfig(
            #         response_mime_type="application/json",
            #         response_schema=response_schema,
            #         max_output_tokens=1500,
            #         temperature=0.2
            #     ))
            response = {'current_ats_score': 65,
                        'overall_enhanced_resume_sections':
                            {'summary_or_objective':
                                 {'original_text': 'Python Developer with 1 year of experience in web '
                                                   'development and Al-powered solutions using Django and ChatGPT '
                                                   'API. Passionate about web development, automation, and Al.',
                                  'suggested_text': 'Proficient Python Developer with 1 year of experience in '
                                                    'developing and maintaining ML/CV pipelines and applications. '
                                                    'Solid understanding of Machine Learning concepts and experience '
                                                    'with ML frameworks (e.g., TensorFlow, PyTorch, scikit-learn). '
                                                    'Practical experience in Computer Vision, including techniques such '
                                                    'as image segmentation, feature extraction, object detection, '
                                                    'and recognition.'},
                             'experience': [
                                 {'original_text': 'Developed an Al-powered Applicant Tracking System (ATS) using Django.',
                                  'suggested_text': 'Developed and maintained Python-based ML/CV pipelines and applications '
                                                    'using Django, enhancing the Applicant Tracking System (ATS).'},
                                 {'original_text': 'Integrated Azure for cloud deployment to ensure scalability and '
                                                   'reliability.',
                                  'suggested_text': 'Deployed models into production environments using Azure, '
                                                    'ensuring scalability and reliability.'}],
                             'skills': [
                                 {'original_text': 'Al & Data Analysis: ChatGPT API, Data Visualization, NLP (SpaCy), Pandas',
                                  'suggested_text': 'Machine Learning: TensorFlow, PyTorch, scikit-learn. Computer Vision: Image'
                                                    ' segmentation, feature extraction, object detection, and recognition.'},
                                 {'original_text': 'Cloud & Deployment: Azure',
                                  'suggested_text': 'Cloud Platforms: Azure. Containerization: Docker.'},
                                 {'original_text': 'Programming Languages : Python, C, MATLAB, Verilog HDL',
                                  'suggested_text': 'Programming Languages: Python, NumPy, OpenCV, Pandas.'}],
                             'projects': [
                                 {'original_text': 'Integrated ChatGPT API for candidate analysis reports with interactive '
                                                   'data visualization.',
                                  'suggested_text': 'Designed and implemented computer vision algorithms for tasks like '
                                                    'object detection, tracking, image classification, OCR, etc. '
                                                    'Integrated ChatGPT API for candidate analysis reports with '
                                                    'interactive data visualization.'}]}}

            # response = { "current_ats_score": 35, "overall_enhanced_resume_sections":
            #     { "summary_or_objective": "Highly motivated Python Developer with 1 year of experience in web development and AI-powered solutions using Django and ChatGPT API. Seeking to leverage expertise in data science, machine learning, and cloud platforms (Azure) to contribute to large-scale data processing pipelines and innovative machine learning algorithm development.",
            #       "experience": [ "Developed and maintained an AI-powered Applicant Tracking System (ATS) using Django, optimizing it for large-scale data processing and seamless integration with cloud platforms like Azure.", "Guided a junior developer in creating an internal attendance system, ensuring code quality through rigorous code reviews and adherence to Python best practices.", "Led a team of 2 developers to build a resume-making website, implementing practical solutions for debugging and troubleshooting Python-related queries.", "Integrated Azure for cloud deployment to ensure scalability and reliability, utilizing a working understanding of cloud platforms to create robust and efficient systems." ],
            #       "skills": [ "Programming Languages: Python (Expert), C, MATLAB, Verilog HDL", "Web Development: Django, Flask, Pyramid, JavaScript, HTML, CSS, Bootstrap", "AI & Data Analysis: ChatGPT API, Data Visualization, NLP (SpaCy), Pandas, scikit-learn", "Cloud & Deployment: Azure, AWS, Google Cloud", "Databases: PostgreSQL, SQLite", "Embedded Systems: Microcontrollers (ARM, AVR), Raspberry Pi", "Communication Protocols: UART, SPI, I2C", "Software Development Tools: Pycharm, MATLAB, Arduino IDE, Thonny, Xilinx ISE Design Suite", "Version Control: Git" ],
            #       "projects": [ "AI-Powered Applicant Tracking System (ATS): Built an ATS using Django to streamline recruitment workflows and create large-scale data processing pipelines. Integrated ChatGPT API for candidate analysis reports with interactive data visualization, enhancing the system's ability to build and train novel machine learning algorithms.", "Line Following Robot: Built a two-wheel robot using Arduino Nano, IR sensors, and an L293D motor driver.", "Pi Pico Retrogaming Gameboy: Designed a Raspberry Pi-based retro gaming console to emulate classic games." ] } }
            if response:
                st.markdown(":green[Response Generated!:white_check_mark:]")

                import json

                # response = json.loads(response.text)  # dict
                # # response1 = json.dumps(json_response, indent=2)
                # st.text(response)
                # print(type(response1))
                st.markdown("""
                <style>
                
                /* Target the Plotly chart container directly if it has a consistent class */
                .js-plotly-plot .plotly .user-select-none { /* This is a common class for Plotly charts in Streamlit */
                    height: 200px !important; /* Remove bottom margin of the chart container */
                    width: 300px !important;
                }
                

                </style>
                """, unsafe_allow_html=True)
                percentage_ats_score = response["current_ats_score"]
                fig = go.Figure(go.Indicator(
                    mode="number+gauge",  # Shows the number and fills a gauge
                    value=percentage_ats_score,
                    number={'suffix': "%"},
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "Your ATS Score"},
                    gauge={
                        'shape': "angular",  # Makes it a half-circle gauge
                        'axis':  {'range': [None, 100], 'visible':False},
                        # Set axis range and major ticks
                        'bar': {'color': "#00b371"},  # Color of the filled bar
                    }
                ))

                # You can also adjust the font size of the displayed number
                fig.update_layout(
                    height=200,  # <-- Set a smaller height (e.g., 200 pixels)
                    width=250,
                    font=dict(size=24),  # Adjust font size for the displayed number
                    margin=dict(l=20, r=20, b=0, t=0),  # Adjust margins
                    font_color="#00b371"
                )

                # c_col, _ = st.columns([0.17,0.43])
                # with c_col:
                st.plotly_chart(fig, use_container_width=False)

                st.header(":orange[**Areas of Improvement:**]", divider=True)
                st.markdown(":red-background[Elevate your profile: Replace the **Yellow-highlighted** text with the **Blue-highlighted** suggestion.]")

                # for area in response["areas_of_improvement"]:
                #     if area.get("description"):
                #         st.subheader("Description : ")
                #         st.text(area["description"])
                #     if area.get("suggested_enhancement"):
                #         st.subheader("Suggestion : ")
                #         st.text(area["suggested_enhancement"])
                #     if area.get("reasoning"):
                #         st.subheader("Reasoning : ")
                #         st.text(area["reasoning"])

                part1, part2 = st.columns(2)
                with part1:
                    if response['overall_enhanced_resume_sections'].get("summary_or_objective"):
                        st.subheader("Objectives : ")

                        st.text("Your original text from resume : ")

                        # Render copy to clipboard button
                        st.markdown(f":orange-background[{response['overall_enhanced_resume_sections']['summary_or_objective']["original_text"]}]")
                        # Display the suggested text and the copy button on the same line
                        # st.markdown('<div class="my-custom-row-container">', unsafe_allow_html=True)
                        st.text("Suggested text : ")

                        text_col, copy_col = st.columns([0.85, 0.15])  # Adjust ratios as needed


                        with text_col:

                            st.markdown(f":blue-background[{response['overall_enhanced_resume_sections']['summary_or_objective']["suggested_text"]}]"
                                )

                        with copy_col:
                            # You might need to adjust the button's appearance or add a small margin if it's too close
                            if st_copy_to_clipboard(
                                response['overall_enhanced_resume_sections']['summary_or_objective']["suggested_text"]):
                                st.toast('Text Copied!')

                    if response['overall_enhanced_resume_sections'].get("skills"):
                            st.subheader("Skills : ")

                            s = ''
                            s2 = ''
                            suggested_text_for_copy = ''

                            for i in response['overall_enhanced_resume_sections']['skills']:
                                s += "- :orange-background[" + i["original_text"] + "]\n"
                                s2 += "- :blue-background[" + i["suggested_text"] + "]\n"
                                suggested_text_for_copy += f"- {i["suggested_text"]}\n"

                            st.text("Your original text from resume : ")

                            st.markdown(s)
                            st.text("Suggested text : ")

                            text_col, copy_col = st.columns([0.85, 0.15])  # Adjust ratios as needed
                            with text_col:

                                st.markdown(s2)

                            with copy_col:
                                # You might need to adjust the button's appearance or add a small margin if it's too close
                                st_copy_to_clipboard(suggested_text_for_copy)

                    # st.write("Objectives : ", response['overall_enhanced_resume_sections']['experience'])
                with part2:
                    if response['overall_enhanced_resume_sections'].get("experience"):
                        st.subheader("Experience : ")
                        s = ''
                        s2 = ''
                        suggested_text_for_copy = ''

                        for i in response['overall_enhanced_resume_sections']['experience']:
                            s += "- :orange-background[" + i["original_text"] + "]\n"
                            s2 += "- :blue-background[" + i["suggested_text"] + "]\n"
                            suggested_text_for_copy += f"- {i["suggested_text"]}\n"

                        st.text("Your original text from resume : ")

                        st.markdown(s)
                        st.text("Suggested text : ")

                        text_col, copy_col = st.columns([0.85, 0.15])  # Adjust ratios as needed
                        with text_col:

                            st.markdown(s2)

                        with copy_col:
                            # You might need to adjust the button's appearance or add a small margin if it's too close
                            st_copy_to_clipboard(suggested_text_for_copy)
                        # st.write("Objectives : ", response['overall_enhanced_resume_sections']['skills'])

                    if response['overall_enhanced_resume_sections'].get("projects"):
                        st.subheader("Projects : ")
                        s = ''
                        s2 = ''
                        suggested_text_for_copy = ''
                        for i in response['overall_enhanced_resume_sections']['projects']:
                            s += "- :orange-background[" + i["original_text"] + "]\n"
                            s2 += "- :blue-background[" + i["suggested_text"] + "]\n"
                            suggested_text_for_copy += f"- {i["suggested_text"]}\n"

                        st.text("Your original text from resume : ")

                        st.markdown(s)
                        st.text("Suggested text : ")

                        text_col, copy_col = st.columns([0.85, 0.15])  # Adjust ratios as needed
                        with text_col:

                            st.markdown(s2)

                        with copy_col:
                            # You might need to adjust the button's appearance or add a small margin if it's too close
                            st_copy_to_clipboard(suggested_text_for_copy)
                    # st.write("Objectives : ", response['overall_enhanced_resume_sections']['projects'])

                logging.info(response)


            # with first_tab2:
            #     st.text(prompt)
