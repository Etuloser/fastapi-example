from sqlmodel import Session

from app.core.db import engine, init_db
from app.core.logging import logger


def init() -> None:
    with Session(engine) as session:
        init_db(session)


def main() -> None:
    logger.info("Initializing service")
    init()
    logger.info("Service finished initializing")


if __name__ == "__main__":
    main()
