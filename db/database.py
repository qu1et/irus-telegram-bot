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
    
    await conn.execute('''CREATE TABLE IF NOT EXISTS tags(
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT UNIQUE)''')
    
    await conn.execute('''CREATE TABLE IF NOT EXISTS users_tags(
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id INTEGER,
                            tag_id INTEGER,
                            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                            FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE)''')
    
    cursor = await conn.execute('SELECT COUNT(*) FROM tags')
    num = await cursor.fetchone()

    if num[0] == 0:
        await conn.execute('''INSERT OR IGNORE INTO tags (name) VALUES ('Горячий'), ('Обычный'), ('Холодный')''')

    await conn.commit()
    await conn.close()