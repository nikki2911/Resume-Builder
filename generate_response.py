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

load_dotenv()


def generatedResponse(response):
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
            'axis': {'range': [None, 100], 'visible': False},
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
    st.markdown(
        ":red-background[Elevate your profile: Replace the **Yellow-highlighted** text with the **Blue-highlighted** suggestion.]")

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
            st.markdown(
                f":orange-background[{response['overall_enhanced_resume_sections']['summary_or_objective']["original_text"]}]")
            # Display the suggested text and the copy button on the same line
            # st.markdown('<div class="my-custom-row-container">', unsafe_allow_html=True)
            st.text("Suggested text : ")

            text_col, copy_col = st.columns([0.85, 0.15])  # Adjust ratios as needed

            with text_col:

                st.markdown(
                    f":blue-background[{response['overall_enhanced_resume_sections']['summary_or_objective']["suggested_text"]}]"
                    )

            with copy_col:
                # You might need to adjust the button's appearance or add a small margin if it's too close
                if st_copy_to_clipboard(
                        response['overall_enhanced_resume_sections']['summary_or_objective']["suggested_text"]):
                    st.toast('Text Copied!')

        if response['overall_enhanced_resume_sections'].get("skills"):
            de_dulpicate_key = 'skills'
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
            de_dulpicate_key = 'experience'

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

    return de_dulpicate_key