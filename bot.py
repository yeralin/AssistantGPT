"""Main entry where the Telegram bot is launched"""
import logging
import os

from io import BytesIO

import dotenv

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackContext,
    CommandHandler,
    MessageHandler,
    filters,
)

from speech import Speech
from clickup import ClickUp
from gpt import GPT, GPTModel
import util

dotenv.load_dotenv()
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


class TelegramBotException(Exception):
    """Custom exception for errors raised by the Telegram bot."""


class TelegramBot:
    """Main Telegram bot class"""

    WELCOME_MESSAGE = """I am AssistantGPT bot!"""

    REJECTION_MESSAGE = """Unfortunately this bot is no longer available."""

    def __init__(self):
        self.speech = Speech()
        self.clickup = ClickUp()
        available_functions = {
            self.clickup.create_task: {
                "name": "create_task",
                "description": "Create personalized task",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "description": {"type": "string"},
                        "tags": {"type": "array", "items": {"type": "string"}},
                        "priority": {"type": "integer", "minimum": 0, "maximum": 4},
                        "due_date": {"type": "integer"},
                        "due_date_time": {"type": "boolean"},
                    },
                    "required": ["name", "description", "due_date"],
                },
            },
            util.calculate_date: {
                "name": "calculate_date",
                "description": "Calculate date in unix time format",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "days": {"type": "integer"},
                        "hours": {"type": "integer"},
                        "minutes": {"type": "integer"},
                        "week_day": {"type": "integer", "minimum": 1, "maximum": 7},
                    },
                    "required": ["name"],
                },
            },
        }
        self.gpt = GPT(available_functions)
        # Configure bot application
        self.application = (
            ApplicationBuilder().token(os.getenv("TELEGRAM_TOKEN")).build()
        )

    async def start(self, update: Update, context: CallbackContext) -> None:
        """
        Handles the /start command and initializes the message limiter.
        Args:
            update (Update): The update object from Telegram.
            context (CallbackContext): The context object from Telegram.
        """
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=TelegramBot.WELCOME_MESSAGE
        )

    async def voice_message(self, update: Update, context: CallbackContext) -> None:
        """
        Handles incoming messages from users and sends a response from the assistant.
        Args:
            update (Update): The update object from Telegram.
            context (CallbackContext): The context object from Telegram.
        """
        typing_task = context.application.create_task(
            util.typing_action(context, update.effective_chat.id)
        )
        message_recording = await context.bot.get_file(update.message.voice.file_id)
        # Download and recognize the audio recording
        with BytesIO() as recording:
            await message_recording.download_to_memory(out=recording)
            transcript = self.speech.recognize(recording)
            if not transcript:
                raise TelegramBotException("Speech recognition failed.")
        # Communicate recognized speech to GPT
        response_message = self.gpt.converse(transcript)
        typing_task.cancel()
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=response_message
        )

    async def rejection(self, update: Update, context: CallbackContext) -> None:
        """
        Handles rejection messages for non-allowed users.
        Args:
            update (Update): The update object from Telegram.
            context (CallbackContext): The context object from Telegram.
        """
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=TelegramBot.REJECTION_MESSAGE
        )

    def run(self):
        """Start the bot in polling mode."""
        # Configure optional user filter
        user_id = os.getenv("USER_ID")
        user_filter = filters.User(int(user_id)) if user_id else filters.ALL
        # Configure main handlers
        start_handler = CommandHandler("start", self.start, user_filter)
        voice_message_handler = MessageHandler(
            user_filter & filters.VOICE & (~filters.COMMAND), self.voice_message
        )
        rejection_handler = MessageHandler(~user_filter, self.rejection)
        self.application.add_handlers(
            [start_handler, voice_message_handler, rejection_handler]
        )
        self.application.run_polling()


if __name__ == "__main__":
    bot = TelegramBot()
    bot.run()
