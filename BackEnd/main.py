from fastapi import FastAPI, Query as FastAPIQuery
from pydantic import BaseModel
from groq import Groq
from json import load, dump
import datetime
import time
import serial
from dotenv import dotenv_values
import os

# Load environment variables
env_vars = dotenv_values(".env")
Username = env_vars.get("Username", "User")
Assistantname = env_vars.get("Assistantname", "Assistant")
GroqAPIKey = env_vars.get("GroqAPIKey")

# Initialize Groq client
client = Groq(api_key=GroqAPIKey)

# Initialize Serial Communication with Arduino
try:
    arduino = serial.Serial(port='COM4', baudrate=9600, timeout=1)
    time.sleep(2)
    print("Arduino connected successfully.")
except serial.SerialException as e:
    print("Could not connect to Arduino:", e)
    arduino = None

# System prompt
System = f"""
Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname}
which also has real-time up-to-date information from the internet.
*** Do not tell time until I ask, do not talk too much, just answer the question.***
*** Do not provide notes in the output, just answer the question and never mention your training data.
You can control the hardware like LED and fan. ***
"""

SystemChatBot = [{"role": "system", "content": System}]

def RealtimeInformation():
    now = datetime.datetime.now()
    return f"Current day: {now.strftime('%A')}\nDate: {now.strftime('%d %B %Y')}, Time: {now.strftime('%H:%M:%S')}\n"

def AnswerModifier(answer):
    return '\n'.join([line for line in answer.split('\n') if line.strip()])

def send_command_to_arduino(command):
    if arduino and arduino.is_open:
        arduino.write((command + "\n").encode())
        print(f"Sent to Arduino: {command}")
    else:
        print("Arduino is not connected.")

def load_chat_log():
    path = "Data/ChatLog.json"
    os.makedirs("Data", exist_ok=True)
    try:
        with open(path, "r") as f:
            return load(f)
    except FileNotFoundError:
        with open(path, "w") as f:
            dump([], f)
        return []

def save_chat_log(messages):
    with open("Data/ChatLog.json", "w") as f:
        dump(messages, f, indent=4)

def ChatBot(query: str):
    messages = load_chat_log()
    messages.append({"role": "user", "content": query})

    try:
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=SystemChatBot + [{"role": "system", "content": RealtimeInformation()}] + messages,
            max_tokens=1024,
            temperature=0.7,
            top_p=1,
            stream=True,
        )

        answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                answer += chunk.choices[0].delta.content

        answer = answer.replace("</s>", "")
        messages.append({"role": "assistant", "content": answer})
        save_chat_log(messages)

        command = query.lower()
        if "turn on led" in command or "led on" in command or "1" in command:
            send_command_to_arduino("LED_ON")
        elif "turn off led" in command or "led off" in command or "0" in command:
            send_command_to_arduino("LED_OFF")
        elif "turn on fan" in command:
            send_command_to_arduino("FAN_ON")
        elif "turn off fan" in command:
            send_command_to_arduino("FAN_OFF")
        elif "open door" in command:
            send_command_to_arduino("DOOR_OPEN")
        elif "close door" in command:
            send_command_to_arduino("DOOR_CLOSE")

        return {"bot_response": AnswerModifier(answer)}

    except Exception as e:
        print(f"Error: {e}")
        return {"error": "Something went wrong while processing your query."}

# FastAPI app
app = FastAPI()

class Query(BaseModel):
    message: str

@app.post("/chat")
def chat_with_bot(query: Query):
    print(f"Received query: {query.message}")
    return ChatBot(query.message)

@app.get("/send")
def send_message(message: str = FastAPIQuery(..., max_length=100, description="User message for the chatbot")):
    return ChatBot(message)

@app.get("/")
def root():
    return {"message": "Groq-Arduino Chatbot API is running"}
