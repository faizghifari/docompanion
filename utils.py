import os
import re

import random
import requests

import streamlit as st


def parse_string(input_string):
    parsed_string = input_string.replace(" ", "_")
    parsed_string = parsed_string.replace("-", "_")
    parsed_string = re.sub(r"[^a-z0-9_]", "", parsed_string.lower())
    parsed_string = re.sub(r"(_)\1+", r"\1", parsed_string)

    return parsed_string


def parse_model_fname(input_path):
    return input_path.replace("\\", "/").split("/")[-1]


def get_supported_files():
    return [
        "pdf",
        "csv",
        "docx",
        "txt",
        "epub",
        "hwp",
        "mbox",
        "ppt",
        "pptm",
        "pptx",
        "ipynb",
        "md",
    ]


def get_random_wait_txt():
    return random.choice(
        [
            "Give me some time to think and answer your question okay? Please wait...",
            "Allow me a moment to ponder and respond to your question, alright? Your patience is appreciated.",
            "Kindly grant me a moment to contemplate and provide an answer to your query, please. Thank you for your patience.",
            "I need a moment to consider and address your question, if that's okay. Thank you for your understanding.",
            "Let me take a moment to reflect and offer a response to your question, alright? Your patience is valued.",
            "Please give me a moment to mull over and reply to your question, okay? Thank you for your patience.",
            "I require some time to think through and respond to your question, if that's alright. Thank you for your patience.",
            "Just need a moment to deliberate and answer your question, okay? Thank you for your understanding.",
            "I'd appreciate a moment to consider and address your question, please. Your patience is valued.",
            "Please grant me a moment to ponder and reply to your question, alright? Thank you for your patience.",
            "Kindly allow me a moment to think and respond to your question, okay? Your patience is appreciated.",
        ]
    )


def get_random_answer_txt(answer_len):
    return random.choice(
        [
            f"""Sorry for taking too long!
I generated {answer_len} subquestions derived from your question for more accurate answer!
Here are my answer from the generated subquestions""",
            f"""Apologies for the delay!
I've created {answer_len} subquestions based on your query to enhance the accuracy of my response.
Here are the answers derived from these subquestions.""",
            f"""I regret the delay!
I've produced {answer_len} subqueries stemming from your initial question to ensure a more precise response.
Here are the resulting answers.""",
            f"""Forgive the delay!
I've formulated {answer_len} subqueries from your original question for increased accuracy.
Here are the responses derived from these queries.""",
            f"""I apologize for the wait!
I've constructed {answer_len} subqueries from your question to provide a more precise response.
Here are the answers resulting from these subqueries.""",
            f"""Regretfully, it took longer than expected!
I've generated {answer_len} subquestions from your query to ensure a more accurate response.
Here are the answers derived from these subqueries.""",
            f"""I'm sorry for the delay!
I've devised {answer_len} subqueries based on your question to enhance the accuracy of my response.
Here are the resulting answers.""",
            f"""Apologies for the delay in response!
I've generated {answer_len} subquestions stemming from your query for a more accurate answer.
Here are the answers derived from these subquestions.""",
            f"""Sorry for the delay!
I've created {answer_len} subqueries derived from your question to provide a more accurate response.
Here are the answers resulting from these subqueries.""",
            f"""I regret the delay!
I've formulated {answer_len} subquestions from your initial query to ensure a more precise response.
Here are the resulting answers.""",
            f"""Forgive the delay!
I've compiled {answer_len} subqueries based on your original question for increased accuracy.
Here are the responses derived from these queries.""",
        ]
    )


def download(url, dest_folder):
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)

    filename = url.split("/")[-1].replace(" ", "_")
    file_path = os.path.join(dest_folder, filename)

    r = requests.get(url, stream=True)
    if r.ok:
        progress_text = "Downloading LLM. Please wait."
        download_bar = st.progress(0.0, text=progress_text)
        total_size = int(r.headers.get("content-length"))
        with open(file_path, "wb") as f:
            print("Downloading %s" % file_path)
            downloaded = 0
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    f.flush()
                    os.fsync(f.fileno())
                    downloaded = downloaded + len(chunk)
                    progress = downloaded / total_size
                    download_bar.progress(progress, text=progress_text)

        return file_path
    else:
        raise ConnectionError(
            "Download failed: status code {}\n{}".format(r.status_code, r.text)
        )
