from crewai import Agent, LLM
from tools import yt_tool

from dotenv import load_dotenv

load_dotenv()

import os
OPENAI_API_KEY= os.getenv("OPENAI_API_KEY")

llm = LLM(
    model="gpt-4o-mini",
    temperature=0.7,
    max_tokens=4000,
    api_key=OPENAI_API_KEY
)

## Blog content researcher agent
blog_researcher = Agent(
    role="Blog Content Researcher from YouTube video",
    goal="Get the relevant video content for the topic {topic} from YouTube and extract the key points to create a blog post.",
    verbose=True,
    memory=True,
    backstory=(
        "Expert in understanding videos in AI Data Science , MAchine Learning And GEN AI and providing suggestion" 
    ),
    llm=llm,
    tools=[yt_tool],
    allow_delegation=True
)

## Blog content writer agent
blog_writer = Agent(
    role="Blog Content Writer from YouTube video",
    goal="Narrate compelling tech stories about the video {topic} from YT video",
    verbose=True,
    memory=True,
    backstory=(
        "With a flair for simplifying complex topics, you craft"
        "engaging narratives that captivate and educate, bringing new"
        "discoveries to light in an accessible manner."
    ),
    llm=llm,
    tools=[yt_tool],
    allow_delegation=False
)