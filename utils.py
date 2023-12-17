import os
import re

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
