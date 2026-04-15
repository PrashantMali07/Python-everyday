from crewai_tools import YoutubeChannelSearchTool
from dotenv import load_dotenv

load_dotenv()

import os
os.environ["OPENAI_API_KEY"]= os.getenv("OPENAI_API_KEY")

# Initialize the tool with a specific Youtube channel handle to target your search
yt_tool = YoutubeChannelSearchTool(youtube_channel_handle="https://www.youtube.com/channel/UCNU_lfiiWBdtULKOw6X0Dig")