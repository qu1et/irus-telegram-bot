import aiosqlite
from config.config import TAGS


async def set_tag(user_id: int, tag_name: int):
    if tag_name in TAGS:
        async with aiosqlite.connect("user.db") as conn:
            tag = await conn.execute("SELECT id FROM tags WHERE name = ?", (tag_name,))
            tag_id = await tag.fetchone()
            await conn.execute(
                "INSERT INTO users_tags (user_id, tag_id) VALUES (?, ?)",
                (user_id, tag_id[0]),
            )
            await conn.commit()
            return True
    return False


async def update_tag(tg_id: int, tag_name: int):
    if tag_name in TAGS:
        async with aiosqlite.connect("user.db") as conn:
            user = await conn.execute("SELECT id FROM users WHERE id_tg = ?", (tg_id,))
            user_id = await user.fetchone()
            tag = await conn.execute("SELECT id FROM tags WHERE name = ?", (tag_name,))
            tag_id = await tag.fetchone()
            await conn.execute("UPDATE users_tags SET tag_id = ? WHERE user_id = ?", (tag_id[0], user_id))
            await conn.commit()
            return True
    return False


async def count_users_with_tag(tag_name: str):
    if tag_name in TAGS:
        async with aiosqlite.connect("user.db") as conn:
            tag = await conn.execute("SELECT id FROM tags WHERE name = ?", (tag_name,))
            tag_id = await tag.fetchone()
            users = await conn.execute(
                "SELECT COUNT(*) FROM users_tags WHERE tag_id = ?", (tag_id[0],)
            )
            return await users.fetchone()
    return False


async def get_list_by_tag(tag_name: str):
    if tag_name in TAGS:
        async with aiosqlite.connect("user.db") as conn:
            tag = await conn.execute("SELECT id FROM tags WHERE name = ?", (tag_name,))
            tag_id = await tag.fetchone()
            users = await conn.execute(
                '''SELECT * FROM users
                    JOIN users_tags ON users.id = users_tags.user_id
                    WHERE users_tags.tag_id = ?''', (tag_id[0],))
            return await users.fetchall()
    return False


async def delete_tag(user_id: int):
    async with aiosqlite.connect("user.db") as conn:
        await conn.execute("DELETE FROM users_tags WHERE user_id = ?", (user_id,))
        await conn.commit()
    return True
