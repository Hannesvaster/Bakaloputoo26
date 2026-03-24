import os
from pathlib import Path

from fastapi import FastAPI
from dotenv import load_dotenv
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))