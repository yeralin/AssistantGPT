"""This module contains utility functions used throughout the codebase."""

import asyncio
import datetime
from enum import Enum
from typing import Optional

from telegram.constants import ChatAction
from telegram.ext import CallbackContext


class WeekDayEnum(Enum):
    """
    Enumeration class representing the weekdays.
    """

    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6


def calculate_date(
    days: int = 0,
    hours: Optional[int] = None,
    minutes: Optional[int] = None,
    week_day: Optional[WeekDayEnum] = None,
) -> str:
    """
    Calculates the Unix timestamp of a future date and time based on the current time.

    Args:
        days (int, optional): Number of days to add (default: 0).
        hours (int, optional): Number of hours to set (default: 0).
        minutes (int, optional): Number of minutes to set (default: 0).
        week_day (WeekDayEnum, optional): Target weekday to calculate time until (default: None).

    Returns:
        str: Unix timestamp of the future date and time.
    """
    current_time = future_time = datetime.datetime.now()

    # Set the specific time
    if hours or minutes:
        hours = hours if hours else 0
        minutes = minutes if minutes else 0
        future_time = current_time.replace(hour=hours, minute=minutes)

    # Add the specified number of days
    future_time += datetime.timedelta(days=days)

    if week_day is not None:
        current_weekday = current_time.weekday()
        days_ahead = (week_day.value - current_weekday) % 7
        future_time += datetime.timedelta(days=days_ahead)

    return str(int(future_time.timestamp() * 1000))


def escape_telegram_message(message: str) -> str:
    """
    Escapes special characters for a Telegram message.

    Args:
        message (str): The message to escape.

    Returns:
        str: The escaped message.
    """
    return (
        message.replace("-", r"\-")
        .replace(".", r"\.")
    )


async def typing_action(context: CallbackContext, chat_id: int):
    """
    Coroutine that sends a "typing..." action to the chat every 5 seconds.

    Args:
        context (CallbackContext): The context object from Telegram.
        chat_id (int): The ID of the chat to send the action to.
    """
    while True:
        try:
            await context.bot.send_chat_action(
                chat_id=chat_id, action=ChatAction.TYPING
            )
            await asyncio.sleep(5.0)
        except asyncio.CancelledError:
            break
