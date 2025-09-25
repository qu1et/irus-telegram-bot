import aiosqlite

async def create_tables(app):
    conn = await aiosqlite.connect('user.db')
    await conn.execute('''CREATE TABLE IF NOT EXISTS users(
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            id_tg INTEGER UNIQUE,
                            name TEXT NULL,
                            phone TEXT NULL,
                            email TEXT NULL,
                            agreement INTEGER DEFAULT 0,
                            created_at DATETIME CURRENT_TIMESTAMP)''')
    await conn.commit()
    await conn.close()