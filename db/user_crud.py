import aiosqlite

async def create_user(id_tg: int, username: str):
    async with aiosqlite.connect('user.db') as conn:
        await conn.execute('INSERT INTO users (id_tg, username) VALUES (?, ?)', (id_tg, username,))
        await conn.commit()
    return True

async def get_user(id_tg: int):
    async with aiosqlite.connect('user.db') as conn:
        user = await conn.execute('SELECT * FROM users WHERE id_tg = ?', (id_tg,))
        return await user.fetchone()
    
async def get_users():
    async with aiosqlite.connect('user.db') as conn:
        users = await conn.execute('SELECT * FROM users')
        return await users.fetchall()
    
async def update_user(id_tg: int, column: str, data):
    async with aiosqlite.connect('user.db') as conn:
        await conn.execute(f'UPDATE users SET {column} = ? WHERE id_tg = ?', (data, id_tg))
        await conn.commit()
    return True
        
