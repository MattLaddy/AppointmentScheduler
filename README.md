# Inbound Call Appointment server


## Overview
This project uses Vocode to handle inbound and outbound phone calls. It includes a custom agent for spelling out text and integrates with Twilio for telephony 
services.


## Requirements
- **Ngrok**: For exposing the local server to the internet.
- **ffmpeg**: For processing audio. If you have Homebrew installed, run:
  ```bash
  brew install ffmpeg

- **redis**: For managing state. If you have Homebrew installed, run:
- **Docker**: For containerized deployment.
## Example .env file:

    # Vocode API Key
    VOCODE_API_KEY=your_vocode_api_key_here

    # Twilio API Keys
    TWILIO_ACCOUNT_SID=your_twilio_account_sid_here
    TWILIO_AUTH_TOKEN=your_twilio_auth_token_here
    TWILIO_PHONE_NUMBER=your_twilio_phone_number_here

    # Eleven Labs API Keys
    ELEVEN_LABS_API_KEY=your_eleven_labs_api_key_here
    ELEVEN_LABS_VOICE_ID=your_eleven_labs_voice_id_here

    # Deepgram API Key
    DEEPGRAM_API_KEY=your_deepgram_api_key_here

    # OpenAI API Key
    OPENAI_API_KEY=your_openai_api_key_here

    # Azure Speech API Keys
    AZURE_SPEECH_KEY=your_azure_speech_key_here
    AZURE_SPEECH_REGION=your_azure_speech_region_here

    # Courier API Token
    COURIER_AUTH_TOKEN=your_courier_auth_token_here

    # Ngrok Authentication Token
    NGROK_AUTH_TOKEN=your_ngrok_auth_token_here

    # Base URL for Ngrok or your deployed server
    BASE_URL=your_base_url_here


## Step 3: Setup Hosting

### To make your server accessible to Twilio, you need to expose it to the internet. A simple way to do this is with Ngrok. In this setup, we assume your server is running on port 3000. Run:

    ngrok http 3000

### Ngrok will provide you with a URL that tunnels localhost:3000. Copy this URL and update the BASE_URL in your .env file, excluding the https:// part, e.g.:

    BASE_URL=asdf1234.ngrok.app

## Step 4: Install Dependencies 
### Install the required dependencies for the project. If using Python, you might need to set up a virtual environment and install packages from requirements.txt:

    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt

### Configuring Twilio

Before starting your server, you need to set up Twilio to handle incoming and outgoing calls. Follow these steps:

#### Step 1: Sign Up for a Twilio Account
1. Go to the [Twilio website](https://www.twilio.com/).
2. Sign up for a new account if you don’t already have one. Follow the instructions to verify your email and phone number.

#### Step 2: Obtain Twilio API Credentials
1. Log in to your Twilio console.
2. Navigate to the [Twilio Console Dashboard](https://www.twilio.com/console).
3. Note down the following credentials from the dashboard:
   - **Account SID**: This is a unique identifier for your Twilio account.
   - **Auth Token**: This is used to authenticate API requests.

   These credentials will be used in your `.env` file:
   ```bash
   TWILIO_ACCOUNT_SID=your_twilio_account_sid_here
   TWILIO_AUTH_TOKEN=your_twilio_auth_token_here

#### Step 3: Get A Twilio Phone Number: 

1. Go to the Phone Numbers section in the Twilio console.
2. Click on Get a Number.
3. Choose a number that suits your needs and purchase it. This number will be used to send and receive calls and SMS.

4. Add this number to your .env file:
    ```bash
    TWILIO_PHONE_NUMBER=your_twilio_phone_number_here

#### Step 4: Set Up Twilio Webhooks
1. To handle incoming calls and messages, you need to configure Twilio to point to your server’s endpoints:

2. Configure Incoming Call Handling:

3. In the Twilio console, go to the Phone Numbers section and select your Twilio number.
4. Under Voice & Fax, set the A CALL COMES IN webhook to point to your server’s URL where you handle incoming calls. For example:

    http://your-server-url/inbound_call

## Step 5: Start Dcoker
### Start Redis using Docker or directly on your machine. For Docker, use:

    docker build -t vocode-telephony-app .

## Step 6: Run the Application
### Start your application. This might involve running a server script or using Docker:

    docker-compose up



## Contact

For any questions or issues, you can reach me at [matthewpierceladdy@gmail.com](mailto:matthewpierceladdy@gmail.com).
