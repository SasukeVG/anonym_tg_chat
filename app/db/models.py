from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, UniqueConstraint, BigInteger
from sqlalchemy.orm import relationship
from app.db.database import Base
import enum


class VoteType(enum.Enum):
    positive = "positive"
    negative = "negative"


class Message(Base):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(BigInteger, unique=True, index=True)
    author_id = Column(BigInteger, ForeignKey('users.user_id'))
    text = Column(String)
    date = Column(DateTime)
    positive_votes = Column(Integer, default=0)
    negative_votes = Column(Integer, default=0)

    author = relationship("User", back_populates="messages")
    votes = relationship("Vote", back_populates="message")  # Связь с Vote


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True, nullable=True)
    user_id = Column(BigInteger, unique=True, index=True, nullable=False)
    date = Column(DateTime)
    name = Column(String, nullable=True)
    surname = Column(String, nullable=True)

    messages = relationship("Message", back_populates="author", cascade="all, delete-orphan")
    votes = relationship("Vote", back_populates="voter", cascade="all, delete-orphan")  # Добавьте эту строку


class Vote(Base):
    __tablename__ = 'votes'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey('users.user_id'))
    message_id = Column(BigInteger, ForeignKey('messages.message_id'))
    vote_type = Column(Enum(VoteType), nullable=False)

    voter = relationship("User", back_populates="votes")  # Связь с User
    message = relationship("Message", back_populates="votes")  # Связь с Message

    __table_args__ = (UniqueConstraint('user_id', 'message_id', name='_user_message_uc'),)


class Thread(Base):
    __tablename__ = 'threads'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    chat_id = Column(BigInteger, nullable=False)
    thread_id = Column(BigInteger, unique=True, index=True)

