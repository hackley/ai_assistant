import sqlite3
from typing import List
from datetime import datetime

from langchain.schema import (
    BaseChatMessageHistory,
    BaseMessage,
    HumanMessage,
    AIMessage,
)


def message_from_tuple(obj: tuple) -> BaseMessage:
    id_, type_, content, timestamp = obj
    if type_ == "human":
        klass = HumanMessage
    elif type_ == "ai":
        klass = AIMessage
    else:
        raise ValueError("Unknown message type")
    message = klass(content=content)
    return message


def serialize_message(obj: tuple) -> dict:
    id_, type_, content, timestamp = obj
    return {
        "id": id_,
        "type": type_,
        "content": content,
        "timestamp": timestamp,
    }


class ChatMessageHistory(BaseChatMessageHistory):
    def __init__(self, session_id: str,):
        self.connection = sqlite3.connect('tmp/database.db')
        self.cursor = self.connection.cursor()
        self.session_id = session_id

    def query_messages(self) -> List[tuple]:
        """Retrieve the messages from SQLite"""
        self.cursor.execute(
            "SELECT id, type, content, timestamp FROM messages WHERE session_id = ?",
            (self.session_id,)
        )
        records = self.cursor.fetchall()
        return records

    @property
    def json_messages(self) -> List[dict]:
        query_results = self.query_messages()
        messages = [serialize_message(m) for m in query_results]
        return messages

    @property
    def messages(self) -> List[BaseMessage]:
        query_results = self.query_messages()
        messages = [message_from_tuple(m) for m in query_results]
        return messages

    def add_user_message(self, message: str) -> None:
        self.append(HumanMessage(content=message))

    def add_ai_message(self, message: str) -> None:
        self.append(AIMessage(content=message))

    def append(self, message: BaseMessage) -> None:
        """Append the message to the record in SQLite"""
        self.cursor.execute(
            '''
              INSERT INTO messages (type, content, session_id, timestamp)
              VALUES (?, ?, ?, ?)
            ''', 
            (message.type, message.content, self.session_id, datetime.now())
        )
        self.connection.commit()

    def clear(self) -> None:
        """Clear session memory from Redis"""
        self.redis_client.delete(self.key)
