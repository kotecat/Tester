import sqlite3
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Type, List, Optional

from database.models import Test, Question, Answer, Result


T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    @property
    @abstractmethod
    def table_name(self) -> str:
        ...

    @property
    @abstractmethod
    def model_class(self) -> Type[T]:
        ...

    def _row_to_model(self, row: sqlite3.Row) -> T:
        return self.model_class(**dict(row))
    
    def find_by_id(self, id_: int) -> Optional[T]:
        cur = self.conn.execute(
            f"SELECT * FROM {self.table_name} WHERE id = ?",
            (id_,),
        )
        row = cur.fetchone()
        return self._row_to_model(row) if row else None

    def find_all(self, limit: int = -1, offset: int = 0) -> List[T]:
        query = f"SELECT * FROM {self.table_name}"
        cur = self.conn.execute(
            query + (" LIMIT ? OFFSET ?" if limit >= 0 else ""),
            (limit, offset) if limit >= 0 else (),
        )
        rows = cur.fetchall()
        return [self._row_to_model(r) for r in rows]

    def create(self, obj: dict = {}, **kwargs) -> int:
        obj = {**obj, **kwargs}
        columns = list(obj.keys())
        values = tuple(obj.values())
        
        query = f"INSERT INTO {self.table_name} ({', '.join(columns)}) VALUES ({', '.join(['?' for _ in values])})"
        cur = self.conn.execute(query, values)
        self.conn.commit()
        new_id = cur.lastrowid
        return self.find_by_id(new_id)
    
    def delete(self, id_: int) -> bool:
        cur = self.conn.execute(
            f"DELETE FROM {self.table_name} WHERE id = ?",
            (id_,),
        )
        self.conn.commit()
        return cur.rowcount > 0



class TestRepository(BaseRepository[Test]):
    @property
    def table_name(self) -> str:
        return "tests"

    @property
    def model_class(self):
        return Test

    def find_by_name(self, name: str) -> Optional[Test]:
        cur = self.conn.execute(
            "SELECT * FROM tests WHERE name = ?",
            (name,),
        )
        row = cur.fetchone()
        return self._row_to_model(row) if row else None

    def search(self, query: str, limit: int = 50) -> List[Test]:
        like = f"%{query}%"
        cur = self.conn.execute(
            """
            SELECT * FROM tests
            WHERE name LIKE ? OR description LIKE ?
            ORDER BY name
            LIMIT ?
            """,
            (like, like, limit),
        )
        return [self._row_to_model(r) for r in cur.fetchall()]


class QuestionRepository(BaseRepository[Question]):
    @property
    def table_name(self) -> str:
        return "questions"

    @property
    def model_class(self):
        return Question

    def find_by_test(self, test_id: int) -> List[Question]:
        cur = self.conn.execute(
            "SELECT * FROM questions WHERE test_id = ? ORDER BY id",
            (test_id,),
        )
        return [self._row_to_model(r) for r in cur.fetchall()]
    

class AnswerRepository(BaseRepository[Answer]):
    @property
    def table_name(self) -> str:
        return "answers"

    @property
    def model_class(self):
        return Answer

    def find_by_question(self, question_id: int) -> List[Answer]:
        cur = self.conn.execute(
            "SELECT * FROM answers WHERE question_id = ? ORDER BY id",
            (question_id,),
        )
        return [self._row_to_model(r) for r in cur.fetchall()]
    

class ResultRepository(BaseRepository[Result]):
    @property
    def table_name(self) -> str:
        return "results"

    @property
    def model_class(self):
        return Result

    def find_by_test(self, test_id: int) -> List[Result]:
        cur = self.conn.execute(
            """
            SELECT * FROM results
            WHERE test_id = ?
            ORDER BY taken_at DESC
            """,
            (test_id,),
        )
        return [self._row_to_model(r) for r in cur.fetchall()]

    def find_by_user(self, user_name: str) -> List[Result]:
        cur = self.conn.execute(
            """
            SELECT * FROM results
            WHERE user_name = ?
            ORDER BY taken_at DESC
            """,
            (user_name,),
        )
        return [self._row_to_model(r) for r in cur.fetchall()]
