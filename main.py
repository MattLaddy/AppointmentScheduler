import asyncio
import os
import json
import sys
import aiohttp
from dotenv import load_dotenv

# Third-party imports
from fastapi import FastAPI, Request
from loguru import logger
from pyngrok import ngrok
from openai import OpenAI

# Local application/library specific imports
from speller_agent import SpellerAgentFactory

from vocode.logging import configure_pretty_logging
from vocode.streaming.models.events import Event, EventType
from vocode.streaming.models.agent import ChatGPTAgentConfig
from vocode.streaming.models.message import BaseMessage
from vocode.streaming.models.telephony import TwilioConfig
from vocode.streaming.models.transcript import TranscriptCompleteEvent
from vocode.streaming.telephony.config_manager.redis_config_manager import RedisConfigManager
from vocode.streaming.telephony.server.base import TelephonyServer, TwilioInboundCallConfig
from vocode.streaming.utils.events_manager import EventsManager

# Initialize FastAPI app
app = FastAPI(docs_url=None)
configure_pretty_logging()

# Load environment variables
load_dotenv()

# Setup ngrok if BASE_URL is not defined
BASE_URL = os.getenv("BASE_URL")
if not BASE_URL:
    ngrok_auth = os.environ.get("NGROK_AUTH_TOKEN")
    if ngrok_auth is not None:
        ngrok.set_auth_token(ngrok_auth)
    port = sys.argv[sys.argv.index("--port") + 1] if "--port" in sys.argv else 3000
    BASE_URL = ngrok.connect(port).public_url.replace("https://", "")
    logger.info('ngrok tunnel "{}" -> "http://127.0.0.1:{}"'.format(BASE_URL, port))
if not BASE_URL:
    raise ValueError("BASE_URL must be set in environment if not using pyngrok")

async def extract_data_from_transcript(transcript):
    logger.info("extract_data_from_transcript called.")
    prompt = f"""
    Extract the following information from the transcript:
    1. Email address
    2. Name
    3. Appointment details or other relevant information
    
    Transcript:
    {transcript}
    
    Provide the information in the format, you should have the info formatted and cleaned up nicely so it has the doctor appointment on one line and each important piece of info on the line after
    do not include the users address only include the appointment schedule what it is.:
    Email: <email>
    Name: <name>
    Info: <info>
    """

    api_key = os.environ.get("OPENAI_API_KEY")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    choices = result.get("choices", [])
                    if choices:
                        response_text = choices[0].get("message", {}).get("content", "")
                        email, name, info = parse_openai_response(response_text)
                        logger.info(f"Data extracted - Email: {email}, Name: {name}, Info: {info}")
                        return email, name, info
                    else:
                        raise Exception("No choices found in the response.")
                else:
                    raise Exception(f"Request failed with status code {response.status}")
    except Exception as e:
        logger.error(f"Error in extract_data_from_transcript: {e}")

def parse_openai_response(response_text):
    logger.info("parse_openai_response called.")
    lines = response_text.split('\n')
    email = next((line.split(': ')[1] for line in lines if line.startswith('Email: ')), None)
    name = next((line.split(': ')[1] for line in lines if line.startswith('Name: ')), None)
    info = next((line.split(': ')[1] for line in lines if line.startswith('Info: ')), None)
    logger.info(f"Parsed response - Email: {email}, Name: {name}, Info: {info}")
    return email, name, info

class CustomEventsManager(EventsManager):
    def __init__(self):
        super().__init__([EventType.TRANSCRIPT_COMPLETE])

    async def handle_event(self, event: Event):
        logger.info("handle_event called.")
        if isinstance(event, TranscriptCompleteEvent):
            transcript = event.transcript.to_string()
            print("The call has finished, the transcript was", transcript)
            logger.info("The call has finished, the transcript was: %s", transcript)
            
            # Extract data using GPT-3.5 Turbo
            try:
                email, name, info = await extract_data_from_transcript(transcript)
                if email and name and info:
                    send_appointment_confirmation(email, name, info)
                else:
                    logger.warning("Missing information in the transcript for appointment confirmation")
            except Exception as e:
                logger.error(f"Error handling event: {e}")

# Initialize Telephony Server
config_manager = RedisConfigManager()
telephony_server = TelephonyServer(
    base_url=BASE_URL,
    config_manager=config_manager,
    inbound_call_configs=[
        TwilioInboundCallConfig(
            url="/inbound_call",
            agent_config=ChatGPTAgentConfig(
                initial_message=BaseMessage(text="Hello! I'm here to assist you with your medical visit details. Let's get started. Can you first tell me your Name and Date of Birth?"),
                prompt_preamble="""You are an AI assistant tasked with collecting patient information for a medical visit.
                You need to gather the following details from the caller:
                - Patient's name and date of birth
                - Insurance information including payer name and ID
                - Referral information including the name of the referring physician
                - Chief medical complaint or reason for the visit
                - Other demographics like address
                - Contact information (here you should ask for an email that we can send a confirmation email to)
                - Available providers and times (provide fake data if needed)
                Make sure to ask each question clearly and collect all required information. If a response is unclear or incomplete, ask follow-up questions to get the necessary details.
                also make sure that when you are listing off doctors, you list off doctors by the name "Doctor" and not Dr. make sure you do this.
                Make sure to double check when you are receiving contact information, repeat it back to them and make sure you are formatting it properly when you repeat it back
                as if it were there email""",
                generate_responses=True,
            ),
            twilio_config=TwilioConfig(
                account_sid=os.environ["TWILIO_ACCOUNT_SID"],
                auth_token=os.environ["TWILIO_AUTH_TOKEN"],
            ),
        )
    ],
    agent_factory=SpellerAgentFactory(),
    events_manager=CustomEventsManager()
)
app.include_router(telephony_server.get_router())

def send_appointment_confirmation(email, name, info):
    logger.info("send_appointment_confirmation called.")
    load_dotenv()
    COURIER_AUTH_TOKEN = os.getenv("COURIER_AUTH_TOKEN")

    curl_command = f'''
    curl --request POST \\
        --url https://api.courier.com/send \\
        --header 'Authorization: Bearer {COURIER_AUTH_TOKEN}' \\
        --data '{{
          "message": {{
            "to": {{"email":"{email}"}},
            "content": {{
              "title": "Appointment confirmation for {name}",
              "body": "Hey {name},                 here is information about the appointment you just booked:                           {info}"
            }}
          }}
        }}'
    '''
    try:
        os.system(curl_command)
        logger.info(f"Appointment confirmation email sent to {email}.")
    except Exception as e:
        logger.error(f"Error sending appointment confirmation email: {e}")
