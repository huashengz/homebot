from typing import Literal
from pydantic import BaseModel


class SentenceComplete(BaseModel):
    type: Literal["sentence_complete"] = "sentence_complete"


class TextContent(BaseModel):
    type: Literal["text"] = "text"
    content: str


class TurnDone(BaseModel):
    type: Literal["turn_done"] = "turn_done"