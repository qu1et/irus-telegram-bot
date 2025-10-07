import aiosqlite

async def set_tag(user_id: int, tag_id: int):
    async with aiosqlite.connect('user.db') as conn:
        await conn.execute('INSERT INTO users_tags (user_id, tag_id) VALUES (?, ?)', (user_id, tag_id))
        await conn.commit()
    return True

async def delete_tag(user_id: int):
    async with aiosqlite.connect('user.db') as conn:
        await conn.execute('DELETE FROM users_tags WHERE user_id = ?', (user_id,))
        await conn.commit()
    return True