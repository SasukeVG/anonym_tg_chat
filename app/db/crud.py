from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select
from app.db.models import User, Message, Vote, VoteType
from app.db.database import connection_url
from datetime import datetime, timedelta
import asyncpg


async def add_user(session: AsyncSession, username: str, user_id: int, name: str, surname: str):
    new_user = User(username=username, user_id=user_id, name=name, surname=surname, date=datetime.now())
    session.add(new_user)

    try:
        await session.commit()
        print("Пользователь успешно добавлен.")
    except IntegrityError as e:
        await session.rollback()
        print(f"Ошибка при добавлении пользователя: {e}")


async def add_message(session: AsyncSession, message_id: int, text: str, author_id: int):
    # Проверяем, существует ли пользователь с данным author_id
    result = await session.execute(select(User).filter(User.user_id == author_id))
    user = result.scalars().first()

    if user:
        new_message = Message(
            message_id=message_id,
            text=text,
            author_id=author_id,
            date=datetime.now()
        )
        session.add(new_message)

        try:
            await session.commit()
            print("Сообщение успешно добавлено.")
        except IntegrityError as e:
            await session.rollback()
            print(f"Ошибка при добавлении сообщения: {e}")
    else:
        print(f"Пользователь с ID {author_id} не найден.")


async def get_votes_and_text_by_message_id(session: AsyncSession, message_id: int):
    result = await session.execute(select(Message).filter(Message.message_id == message_id))
    message = result.scalars().first()

    if message:
        return {
            "positive_votes": message.positive_votes,
            "negative_votes": message.negative_votes,
            "text": message.text,
        }
    else:
        print(f"Сообщение с ID {message_id} не найдено.")
        return None


async def update_positive_votes(session: AsyncSession, message_id: int):
    result = await session.execute(select(Message).filter(Message.message_id == message_id))
    message = result.scalars().first()

    if message:
        message.positive_votes += 1
        await session.commit()
        print("Голос успешно добавлен.")
    else:
        print(f"Сообщение с ID {message_id} не найдено.")


async def update_negative_votes(session: AsyncSession, message_id: int):
    result = await session.execute(select(Message).filter(Message.message_id == message_id))
    message = result.scalars().first()

    if message:
        message.negative_votes += 1
        await session.commit()
        print("Голос успешно добавлен.")
    else:
        print(f"Сообщение с ID {message_id} не найдено.")


async def has_user_voted(session: AsyncSession, user_id: int, message_id: int) -> bool:
    result = await session.execute(
        select(Vote).filter(Vote.user_id == user_id, Vote.message_id == message_id)
    )
    vote = result.scalars().first()
    return vote is not None


async def add_vote(session: AsyncSession, user_id: int, message_id: int, vote_type: VoteType):
    # Проверяем, существует ли голос от этого пользователя за это сообщение
    if await has_user_voted(session, user_id, message_id):
        print("Пользователь уже голосовал за это сообщение.")
        return False

    # Создаем новый голос
    new_vote = Vote(user_id=user_id, message_id=message_id, vote_type=vote_type)
    session.add(new_vote)

    try:
        await session.commit()
        print("Голос успешно добавлен.")
        return True
    except IntegrityError as e:
        await session.rollback()
        print(f"Ошибка при добавлении голоса: {e}")
        return False


async def can_send_message(user_id: int, timeout_seconds: int = 10) -> bool:
    try:
        # Создаем подключение к базе данных
        conn = await asyncpg.connect(connection_url)

        # Выполняем сырой SQL-запрос
        result = await conn.fetchrow("""
            SELECT date 
            FROM messages 
            WHERE author_id = $1
            ORDER BY date DESC
            LIMIT 1
        """, user_id)

        # Закрываем подключение
        await conn.close()

        # Извлекаем дату последнего сообщения
        last_message_time = result['date'] if result else None

        if last_message_time and datetime.now() - last_message_time < timedelta(seconds=timeout_seconds):
            return False

        return True

    except Exception as e:
        # Обрабатываем любые ошибки, например, если данных нет
        print(f"Ошибка при проверке времени последнего сообщения: {e}")
        return True  # Разрешаем отправку сообщения, если произошла ошибка
