import os
from dotenv import load_dotenv
from fastapi import FastAPI
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langserve import add_routes

load_dotenv()

# Loading Groq API 
os.environ["GROQ_API_KEY"]=os.getenv("GROQ_API_KEY")
# Loding LangSmith API for tracing
os.environ['LANGCHAIN_API_KEY']=os.getenv("LANGCHAIN_API_KEY")
os.environ['LANGCHAIN_TRACING_V2']="true"
os.environ['LANGCHAIN_PROJECT']=os.getenv("LANGCHAIN_PROJECT")

# 1. Initializing the model
model=ChatGroq(model="qwen/qwen3-32b")

# 2. Create prompt template
system_template="Translate the followint into {language}"
prompt_template=ChatPromptTemplate([
    ("system",system_template),
    ("user",'{text}')
])

# 3. Creating parser object
parser=StrOutputParser()

# 4. Creating the Chain
chain=prompt_template|model|parser

# 5. Application definition

app = FastAPI(title="LangChain Server",
              version="0.0.1",
              description="A simple API server using LangChain with active inerface.")

add_routes(
    app,
    chain,
    path="/chain"
)

if __name__=="__main__":
    import uvicorn
    uvicorn.run(app,host="localhost",port=8000)