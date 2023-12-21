import streamlit as st
import pandas as pd 
from streamlit.runtime.uploaded_file_manager import UploadedFile
import json
import csv

import text_to_speech as tts
from explainer import send_question

OUTPUT_FILE_NAME = "output_file.csv"
OUTPUT_FILE = "./" + OUTPUT_FILE_NAME
questions_start_index = 0

def display_header() -> None:
    st.image("img/logo.png", width=200)
    st.title("Welcome to Go-Ho-Ho-Time - User Interview Copilot")
    st.text("Just upload your transcripts and csv of questions and we'll do the rest!")

def display_widgets():
    transcripts = st.file_uploader("Upload your TRANSCRIPTS here.", accept_multiple_files=True)
    csv_file = st.file_uploader("Upload your csv file of QUESTIONS here.")

    # if not (file and csv_file):
    #     st.error("Please upload a transcript and an excel file of questions")

    return transcripts, csv_file

def retrieve_content_from_file(file: UploadedFile) -> str:
    return file.getvalue().decode("utf8")

def create_questions_file_grab_only_questions(input_csv_file: UploadedFile):
    global questions_start_index

    questions = []
    output_file_path = OUTPUT_FILE
    
    with open(output_file_path, "wb") as f:
        f.write(input_csv_file.read())

    with open(output_file_path, "r") as f:
        reader = csv.reader(f)
        for row_number, row in enumerate(reader):
            if row and "QUESTIONS" in row[0]:
                questions_start_index = row_number
                break
    
    if questions_start_index >= 0:
        with open(output_file_path, "r") as f:
            reader = csv.DictReader(f)
            for row_number, row in enumerate(reader):
                if row_number >= questions_start_index:
                    questions.append(row['DETAILS'])

    return questions

def file_contents(uploaded_scripts: [UploadedFile], csv_file: UploadedFile):
    # for each uploaded script, get the text
    transcript_texts = []
    for uploaded_script in uploaded_scripts:
        transcript_texts.append(retrieve_content_from_file(uploaded_script))

    return transcript_texts, create_questions_file_grab_only_questions(csv_file)

def extract_transcript():
    uploaded_scripts, csv_file = display_widgets()

    if uploaded_scripts and csv_file:
        return file_contents(uploaded_scripts, csv_file)
    return None, None

# used to convert index of transcript to column letter
def index_to_column(index):
    return chr(ord('F') + index * 2)

# used to convert index of transcript to column letter
def next_column(index):
    column = index_to_column(index)
    next_column = chr(ord(column) + 1)
    return next_column

def main() -> None:
    display_header()

    transcript_texts, questions_text = extract_transcript()

    if transcript_texts and questions_text:
        with st.spinner(text="Analyzing the transcripts..."):
            # loop through each transcript
            user_summaries = ''
            for index, transcript_text in enumerate(transcript_texts):
                # get the answers from the transcript
                question = f"Read this transcript '{transcript_text}'. Now find the answers and timestamps for the following questions. Only provide responses for the questions you do find in this array: \n\n {questions_text}. Important: format your response as an array of json objects, where each json object includes question_number, answer and timestamp attributes. Each question is numbered, use that for the question_number value."

                chat_gpt_resp = send_question(question)
                users_responses = chat_gpt_resp.choices[0].message.content

                # get summary of transcript
                summary_question = f"Read this transcript '{transcript_text}' and give a 1-2 paragraph summary of the interview.  Include a summary of the positive feedback and potential frustrations"
                summary_resp = send_question(summary_question)
                summary = summary_resp.choices[0].message.content

                # get interviewee name
                name_question = f"Read this transcript '{transcript_text}' and provide me ONLY the name of the person being interviewed with no additional text."
                name_resp = send_question(name_question)
                interviewee_name = name_resp.choices[0].message.content

                # get interviewee name
                highlights_question = f"Please analyze the following transcript '{transcript_text}' and identify the two most impactful quotes from the interviewee, {interviewee_name}, regarding their user experience with the product. These quotes can be either positive or negative, but they should be notably descriptive or emotionally charged. Present these quotes in a list format, providing only the direct quotes without any additional text."
                highlights_resp = send_question(highlights_question)
                user_highlights = highlights_resp.choices[0].message.content

                # format the response
                json_string = users_responses.replace("json", "")
                json_string = json_string.replace("`", "")
                json_dict = json.loads(json_string)

                # Updating the output csv file
                df = pd.read_csv(OUTPUT_FILE) 
                for response in json_dict:
                    question_number = int(response['question_number'])

                    # Updating the column value/data
                    df_row_index = (question_number + questions_start_index) - 1
                    df.loc[df_row_index, interviewee_name] = response['timestamp'] + ' - ' + response['answer']

                    # writing into the file 
                    df.to_csv(OUTPUT_FILE, index=False)
                
                user_summaries += f"<u>{interviewee_name}</u>: \n\n {summary}\n\n <b>Highlights</b>: \n\n {user_highlights}\n\n"


        st.success("Uhg, that was hard! But here is your explanation")
        st.markdown(f"**Interview Summary:** \n\n{user_summaries}", unsafe_allow_html=True)
        
        ### Give the csv file to the user
        with open(OUTPUT_FILE, "rb") as file:
            btn = st.download_button(
                    label="Download CSV of Answers",
                    data=file,
                    file_name=OUTPUT_FILE_NAME, 
                    mime="text/csv"
                )


if __name__ == "__main__":
    main()
