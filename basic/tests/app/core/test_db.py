from sqlmodel import Session, select

from app.core.db import engine


class TestDB:
    def test_engine(self):
        with Session(engine) as session:
            assert session.exec(select(1)).first() == 1
