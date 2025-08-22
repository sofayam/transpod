import sqlite3

def list_words(db_path='concordance.db'):
    """Lists all words in the database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT word FROM words ORDER BY word")
    words = cursor.fetchall()

    for word in words:
        print(word[0])

    conn.close()

if __name__ == '__main__':
    list_words()
