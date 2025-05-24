from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class GameState(Base):
    __tablename__ = "game_state"

    id = Column(Integer, primary_key=True)
    fen = Column(Text, nullable=False)
    updated_at = Column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp()
    )


class Move(Base):
    __tablename__ = "moves"

    id = Column(Integer, primary_key=True, autoincrement=True)
    move_notation = Column(String(10), nullable=False)
    fen = Column(Text, nullable=False)
    created_at = Column(
        TIMESTAMP,
        server_default=func.current_timestamp()
    )
