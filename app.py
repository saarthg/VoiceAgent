import speech_recognition as sr
import os
from dotenv import load_dotenv
import pyttsx3
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain.agents.format_scratchpad.openai_tools import (
    format_to_openai_tool_messages,
)
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import AgentExecutor
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.tools import tool

import os.path

from gcalendar import add_calendar_event, get_upcoming_events
from gmail import gmail_create_draft
from news import get_latest_news


load_dotenv()

llm = ChatOpenAI(
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    temperature=1, 
    model_name='gpt-3.5-turbo'
    )

tools = [gmail_create_draft, add_calendar_event, get_upcoming_events, get_latest_news]

MEMORY_KEY = "chat_history"
chat_history = []
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful assistant. Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous.",
        ),
        MessagesPlaceholder(variable_name=MEMORY_KEY),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

llm_with_tools = llm.bind_tools(tools)

agent = (
    {
        "input": lambda x: x["input"],
        "agent_scratchpad": lambda x: format_to_openai_tool_messages(
            x["intermediate_steps"]
        ),
        "chat_history": lambda x: x["chat_history"],
    }
    | prompt
    | llm_with_tools
    | OpenAIToolsAgentOutputParser()
)

agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, return_intermediate_steps=True)

def listen_input():
    while True:
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("Say something!")
            audio = r.listen(source, 6)
        
        try:
            query = r.recognize_google(audio)
            print(query)
            if "bye" in query.lower():
                break
            result = agent_executor.invoke({"input": query, "chat_history": chat_history})
            chat_history.extend(
                [
                HumanMessage(content=query),
                AIMessage(content=result["output"]),
                ]
            )
            engine.say(result["output"])
            engine.runAndWait()
            print(result["output"])
            if len(result["intermediate_steps"]) != 0:
                engine.say("Is there anything else you would like me to help you with?")
                engine.runAndWait()
                print("Is there anything else you would like me to help you with?")

        except sr.UnknownValueError:
            print("Could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))    


if __name__ == "__main__":
    engine = pyttsx3.init()
    engine.setProperty('rate', 175)
    engine.say("How may I help you?")
    engine.runAndWait()
    listen_input()



