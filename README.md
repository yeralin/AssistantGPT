# AssistantGPT - Telegram Bot

<img src="logo.svg" width="250" height="250" alt="Description of the image">

<sub>Generated using [recraft.ai](https://www.recraft.ai/)</sub>

This is a Telegram bot powered by GPT-3.5 to act as a personal assistant. It can handle natural language requests sent as **voice messages** in a Telegram chat.

## Features

- Voice message handling
  - Transcribes audio recordings from Telegram to text using Google Speech API
  - Sends transcript to GPT assistant
- Conversation with GPT-3.5 assistant
  - Contextual conversations to handle user requests
  - Leverages features like [function calling](https://platform.openai.com/docs/guides/gpt/function-calling) to take actions
- ClickUp integration
  - Create tasks in ClickUp based on user requests  
- Date/time calculation
- User access control

## Usage

1. Get API keys
   - Telegram Bot token (`TELEGRAM_TOKEN`)
   - OpenAI API key (`OPENAI_API_KEY`)
   - Google Cloud Speech API credentials ([service account credentials](https://cloud.google.com/iam/docs/service-account-creds))
   - ClickUp API key (`CLICKUP_API_KEY`)
   - ClickUp User ID - to whom tasks will be assigned (`CLICKUP_USER_ID`)
   - ClickUp List ID - under which tasks will be created (`CLICKUP_LIST_ID`)
2. Add keys and credentials to `.env`
3. `pip install -r requirements.txt`  
4. `python bot.py` to run
5. Interact via Telegram bot using **voice messages**

## Structure

- `bot.py` - Main bot application 
- `gpt.py` - GPT client class
- `speech.py` - Speech recognition 
- `clickup.py` - ClickUp integration
- `utils.py` - Helper functions
