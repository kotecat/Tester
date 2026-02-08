from dataclasses import dataclass
from typing import Optional

from datetime import datetime


@dataclass
class Test:
    id: Optional[int]
    name: str
    description: Optional[str]
    questions: int
    time_limit: int

@dataclass
class Question:
    id: Optional[int]
    test_id: int
    q_text: str

@dataclass
class Answer:
    id: Optional[int]
    question_id: int
    a_text: str
    is_correct: bool

@dataclass
class Result:
    id: Optional[int]
    test_id: int
    user_name: str
    group_name: Optional[str]
    score: int
    max_score: int
    time_taken: int
    taken_at: str = ""
