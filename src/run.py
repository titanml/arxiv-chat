"""Streamlit app for the arxiv summarization project. """
# ───────────────────────────────────────────────────── imports ────────────────────────────────────────────────────── #
import streamlit as st
st.set_page_config(layout="wide") # set the page to wide layout

import os
from pathlib import Path

import streamlit as st

from arxiv_loader import ArxivLoader
from pdf_utils import display_pdf, pdf_to_text

Path("paper_downloads").mkdir(parents=True, exist_ok=True)  # create a folder to store the downloaded papers

# from arxiv_miner import ArxivPaper,ResearchPaperFactory
# ROOT_DICTORY_TO_STORE_LATEX = './paper_downloads'
# paper = ArxivPaper.from_arxiv_id('1706.03762',ROOT_DICTORY_TO_STORE_LATEX,detex_path='./detex')
# paperdoc = ResearchPaperFactory.from_arxiv_record(paper)
# print(paperdoc.unknown_sections)
# for section in paperdoc.unknown_sections:
#     print(section.text)

PDF_DISPLAY = True

summarizer = os.environ.get('SUMMARIZER_LOCATION', "http://localhost:8000")
qna = os.environ.get('QNA_LOCATION', "http://localhost:8001")
embedder = os.environ.get('EMBED_LOCATION', "http://localhost:8002")
print("SUMMARIZER: ", summarizer)
print("QNA: ", qna)
print("EMBEDDER: ", embedder)

# ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────── #
#                                                    Streamlit App                                                     #
# ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────── #

# ─────────────────────────────────── Initialize Session State ─────────────────────────────────── #

if "arxiv_code" not in st.session_state:
    st.session_state.arxiv_code = ""

if "pdf_file" not in st.session_state:
    st.session_state.pdf_file = None

if "uploaded_pdf" not in st.session_state:
    st.session_state.uploaded_pdf = False

if "contents" not in st.session_state:
    st.session_state.contents = ""

st.title("Chat with Arxiv")

col1, col2 = st.columns(2)



# Upload option 1 - arxiv code
with col1.form(key="my_form"):
    st.subheader("Option 1: Enter arxiv code")
    arxiv_code = st.text_input(
        label="Please enter the arxiv code for the paper. For example: 2307.08621", key="arxiv_code"
    )
    st.write("\nYou entered: ", arxiv_code)
    submit_button = st.form_submit_button(label="Get PDF")

# Upload option 2 - upload pdf file
with col2.form(key="my_form2"):
    st.subheader("Option 2: Upload pdf file")
    st.session_state.pdf_file = st.file_uploader(label="Please browse for a pdf file", type="pdf")
    submit_button = st.form_submit_button(label="Get PDF")
    if submit_button:
        st.session_state.uploaded_pdf = True

        with open(os.path.join("paper_downloads", st.session_state.pdf_file.name), "wb") as f:
            f.write(st.session_state.pdf_file.getbuffer())

# ───────────────────────────────────────── Display PDF ────────────────────────────────────────── #

with col1:
    if not st.session_state.uploaded_pdf and not st.session_state.arxiv_code:
        st.stop()
    if st.session_state.uploaded_pdf:
        # load pdf, convert to text, display pdf
        pdf = st.session_state.pdf_file
        pdf_path = Path("paper_downloads") / pdf.name
        st.session_state.contents = pdf_to_text(pdf_path)
        pdf_display = display_pdf(pdf_path)
        st.markdown(pdf_display, unsafe_allow_html=True)
    if st.session_state.arxiv_code:
        # load pdf from arxiv, convert to text, display pdf
        docs, file_path = ArxivLoader(query=arxiv_code, load_max_docs=2).load()
        st.session_state.contents = docs[0].page_content
        if PDF_DISPLAY and file_path:
            pdf_display = display_pdf(file_path)
            st.markdown(pdf_display, unsafe_allow_html=True)

    

import requests
import json

def remove_waste_data(text):
    lines = text.split('\n')
    return "\n".join([line for line in lines if len(line) > 10])

def process_text(text):
    text = text.replace("[ section ]", " ")
    return text

def truncate_to_last_full_stop(text):
    if '.' in text:
        return text[:text.rindex('.') + 1]
    return text

def build_prompt(query, contexts):
    contexts.reverse()
    context = "\n".join(contexts)
    prompt = f"context: {context}, question: {query}" 
    return prompt


# ──────────────────────────────────────── Functionality ───────────────────────────────────────── #
with col2:
    contents = st.session_state.contents
    contents = contents.lower().split('references')[0]
    contents = remove_waste_data(contents)
    arxiv_code = st.session_state.arxiv_code.strip()
    if contents and arxiv_code:
        print(arxiv_code)
        response = requests.get(f'{embedder}/papers/{arxiv_code}')
        if not response.json()['exists']:
            response = requests.post(f'{embedder}/embed', json={'code': arxiv_code, 'text': contents})
            print("RESPONSE: ", response.json())
        else:
            print("Paper already stored")

    st.write("Total chars of the document: ", len(contents))
    st.write("Total words of the document: ", len(contents.split(" ")))

    whitespace = 22

    font_css = """
    <style>
    button[data-baseweb="tab"] > div[data-testid="stMarkdownContainer"] > p {
      font-size: 24px;
    }
    </style>
    """

    st.write(font_css, unsafe_allow_html=True)

    # --------------------------------------------------------------------------------------------------
    #                                          Chat with arXiv
    # --------------------------------------------------------------------------------------------------

    st.subheader("Chat with my Arxiv")
    query = st.text_input('Ask your question here: ')
    if query:
        response = requests.post(f'{embedder}/papers', json={'code': arxiv_code, 'query': query}).json()
        if response['status'] == 'success':
            docs = json.loads(response['data'])
            prompt = build_prompt(query, docs)
            response = requests.post(f'{qna}/generate', json={'text': prompt, 'generate_max_length': 200, 'repetition_penalty': 1.5, 'beam_size': 4, 'length_penalty': 1}).json()
            st.write(response['message'])
    # --------------------------------------------------------------------------------------------------
    #                                           Summarization
    # --------------------------------------------------------------------------------------------------
    chunk_size = 8000
    overlap = 1000

    st.subheader("Summarize the whole paper")
    if st.button("Summarize", type="primary"):
        st.subheader("Summary: ")
        with st.spinner(text="In progress..."):
            placeholder = st.empty()
            with placeholder.container():

                summary = contents
                while len(summary) > chunk_size:
                    print("LEN SUMMARY: ", len(summary))
                    chunks = []
                    i = 0
                    while i < len(summary):
                        chunk = summary[i:i+chunk_size]
                        chunks.append(chunk)
                        i += chunk_size - overlap

                    summary = ""
                    for chunk in chunks:
                        response = requests.post(f'{summarizer}/generate', json={'text': process_text(chunk), 'generate_max_length': 200, 'repetition_penalty': 1.5, 'beam_size': 4, 'length_penalty': 1}).json()
                        summary += response['message'] + " "
                        placeholder.write(summary)

                response = requests.post(f'{summarizer}/generate', json={'text': process_text(summary), 'generate_max_length': 500, 'repetition_penalty': 1.5, 'beam_size': 4, 'length_penalty': 1}).json()
                summary = truncate_to_last_full_stop(response['message'])
                placeholder.write(summary)

            