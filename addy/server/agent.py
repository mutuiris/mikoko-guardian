import datetime
import json
import os
from typing import Dict, List, Optional
from zoneinfo import ZoneInfo
from google.adk.agents import Agent
from google.generativeai import GenerativeModel
from google.genai import types
import vertexai
from vertexai.preview import reasoning_engines

