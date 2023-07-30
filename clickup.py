"""This module provides a ClickUp class for interacting with the ClickUp API to create tasks."""

import json
import os

import requests


class ClickUp:
    """
    A class for interacting with the ClickUp API.
    """

    def __init__(self, api_key: str = os.environ['CLICKUP_API_KEY']):
        self.api_key = api_key
        self.base_url = 'https://api.clickup.com/api/v2'

    def create_task(
        self,
        name: str,
        description: str,
        due_date: int,
        due_date_time: bool = False,
        priority: int = 4,
        tags: list = []
    ):
        """
        Create a new task in ClickUp.

        Args:
            list_id: The ID of the list where the task should be created.
            name: The name of the task.
            description: The description of the task.
            priority: The priority of the task.
            due_date: The due date of the task.
            due_date_time: Whether the due date includes time. Defaults to False.
            tags: The list of tags for the task.

        Returns:
            dict: The response JSON containing the created task data.
        """
        uid = os.environ['CLICKUP_USER_ID']
        list_id = os.environ['CLICKUP_LIST_ID']
        url = f'{self.base_url}/list/{list_id}/task'

        payload = {
            'name': name,
            'description': description,
            'tags': tags,
            'priority': priority,
            'due_date': due_date,
            'due_date_time': due_date_time,
            'assignees': [uid],
            'notify_all': True,
        }

        headers = {'Content-Type': 'application/json', 'Authorization': self.api_key}

        response = requests.post(url, json=payload, headers=headers)
        data = response.json()
        return json.dumps(data)
