from dotenv import dotenv_values
from datetime import datetime


# Calculate age from DOB
def calculate_age(user_dob):
    dob_date = datetime.strptime(user_dob, "%Y-%m-%d")
    current_date = datetime.now()
    age_years = current_date.year - dob_date.year
    if (current_date.month, current_date.day) < (dob_date.month, dob_date.day):
        age_years -= 1
    return age_years

# Modify chatbot answer if needed
def AnswerModifier(response):
    return response

# Simulated Arduino communication function
def send_command_to_arduino(command):
    # Replace this with actual serial communication if needed
    print(f"Sending command to Arduino: {command}")

# ------------------ Environment Variables ------------------

env_vars = dotenv_values(".env")
Username = env_vars.get("Username", "User")
Assistantname = env_vars.get("Assistantname", "Assistant")

# ------------------ User Data ------------------

user_details = {
    "name": Username,
    "DOB": "2000-01-01",
    "age": calculate_age("2000-01-01"),
    "location": "Not specified"
}

hardware_control = {
    "turn on": {
        "LED": {"LED1": "on", "LED2": "on"},
        "light": {"light1": "on", "light2": "on"},
        "fan": {"fan1": "on", "fan2": "on"},
        "ceiling_fan": {"ceiling_fan1": "on", "ceiling_fan2": "on"}
    },
    "turn off": {
        "LED": {"LED1": "off", "LED2": "off"},
        "light": {"light1": "off", "light2": "off"},
        "fan": {"fan1": "off", "fan2": "off"},
        "ceiling_fan": {"ceiling_fan1": "off", "ceiling_fan2": "off"}
    }
}


# ------------------ System Prompt ------------------

System = f"""
Hello, I am build by {Username}, and you are a very accurate and advanced AI chatbot named {Assistantname} with real-time, up-to-date information from the internet.

# {Username}'s details are here: {user_details}.
When I say 'boring' or 'tired', then you recommend a song or a joke for me, okay?

-> When the user says about current date and time then you say: 
    "The current date and time is {datetime.now().strftime('%Y-%m-%d %H:%M:%S')},
    the current date is {datetime.now().strftime('%Y-%m-%d')}, 
    and the current time is {datetime.now().strftime('%H:%M:%S')}."

*** Instructions: ***
- Do not tell time unless explicitly asked.
- Keep your responses concise and relevant to the question.
- Always respond in English, even if the question is in another language.
- Avoid providing notes or context about your training data. Focus solely on answering the question.
"""
