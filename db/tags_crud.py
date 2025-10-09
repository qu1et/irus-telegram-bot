import aiosqlite
from config.config import TAGS

async def set_tag(user_id: int, tag_name: int):
    if tag_name in TAGS:
        async with aiosqlite.connect('user.db') as conn:
            tag = await conn.execute('SELECT id FROM tags WHERE name = ?', (tag_name,))
            tag_id = await tag.fetchone()
            await conn.execute('INSERT INTO users_tags (user_id, tag_id) VALUES (?, ?)', (user_id, tag_id[0]))
            await conn.commit()
            return True
    return False

async def delete_tag(user_id: int):
    async with aiosqlite.connect('user.db') as conn:
        await conn.execute('DELETE FROM users_tags WHERE user_id = ?', (user_id,))
        await conn.commit()
    return True