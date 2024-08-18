from sqlalchemy import select, text

from database.models import async_session, User, Booking, Table


async def get_user_by_id(id: int):
    async with async_session() as session:
        return await session.scalar(select(User).where(User.telegram_id == id))


async def get_user(id: int):
    async with async_session() as session:
        res = await session.execute(select(User).where(User.id == id))
        return res.scalar_one_or_none()


async def create_user(id: int, name: str, phone_number: str):
    async with async_session() as session:
        if not await get_user_by_id(id):
            session.add(User(telegram_id=id, name=name, phone_number=phone_number))
            await session.commit()


async def get_booking_by_table_id(table_id: int):
    async with async_session() as session:
        return await session.scalars(select(Booking).where(Booking.table == table_id))


async def booking_table(table_id: int, user_id: int, start_time, end_time):
    async with async_session() as session:
        new_booking = Booking(
            table_id=table_id,
            user_id=user_id,
            start_time=start_time,
            end_time=end_time,
        )
        session.add(new_booking)
        await session.commit()
        await session.refresh(new_booking)
        return new_booking


async def get_tables():
    async with async_session() as session:
        return await session.scalars(select(Table))


async def get_free_tables(start_time, end_time):
    async with async_session() as session:
        not_free_tables = [
            *await session.scalars(
                text(
                    f"SELECT `restaurant_tables`.id FROM `bookings` JOIN `restaurant_tables` ON `bookings`.table_id = `restaurant_tables`.id WHERE `bookings`.start_time < '{end_time}' AND `bookings`.end_time > '{start_time}'"
                )
            )
        ]
        string = ""
        for table in not_free_tables:
            string += f"{', ' if not_free_tables[0] != table else ''}'{str(table)}'"
        return await session.execute(
            text(f"SELECT * FROM restaurant_tables WHERE id NOT IN ({string})")
        )


async def get_table(id: int):
    async with async_session() as session:
        table = await session.execute(select(Table).where(Table.id == id))
        return table.scalar_one_or_none()
