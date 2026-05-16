from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.runnables import RunnablePassthrough , RunnableLambda

import os 

def get_llm():
    return ChatMistralAI(model="mistral-small-latest", temperature=0.2, max_tokens=2048)

def split_text(transcript:str)-> list:
    
    splitter = RecursiveCharacterTextSplitter(chunk_size=3000, chunk_overlap=200)
    return splitter.split_text(transcript)

def summarize(transcript:str)->str:
    llm = get_llm()
    map_prompt =ChatPromptTemplate.from_messages([
        ("system","Summarize this portion of a meeting concisely"),
        ("human","{text}")
    ])
    
    map_chain = map_prompt | llm | StrOutputParser()
    # text_chunks = split_text(transcript)
    
    chunks  = split_text(transcript)
    chunks_summaries = [map_chain.invoke({"text": chunk}) for chunk in chunks]
    combined = "\n\n".join(chunks_summaries)
    combined_prompt = ChatPromptTemplate.from_messages([
        (
            "system","you are an expert at summarizer. Combine these partial summaries " "into the one final professional meeting summary in bullet points."
        ),
        ("human","{text}")
    ])
    combined_chain = (
        RunnablePassthrough() | RunnableLambda(lambda x: {"text": x}) | combined_prompt | llm | StrOutputParser()
    )
    return combined_chain.invoke(combined)

def generate_title(transcript:str)->str:
    llm = get_llm()
    
    title_chain = (
        RunnablePassthrough() | RunnableLambda(lambda x: {"text": x}) |
        ChatPromptTemplate.from_messages([
            ("system","Based on the meeting transcript, generate a short professional meeting title "
             "(max 8 words) only return the title without any additional text."),
             
            ("human","{text}")
        ]) 
        |llm 
        | StrOutputParser()
    ) 
    return title_chain.invoke(transcript[:2000])