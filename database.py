from contextlib import contextmanager
from psycopg2.extras import execute_values

# Types
Poll = tuple[int, str, str]
Option = tuple[int, str, int]
Vote = tuple[str, int]

# SERIAL is a short way for us to tell PostgreSQL that we want the id to be an integer that is auto-incremented for each record inserted
# Creates a polls table if it doesn't already exist with an auto-incremented id as a primary key, a title column, and an owner_username column.
CREATE_POLLS = """CREATE TABLE IF NOT EXISTS polls
(id SERIAL PRIMARY KEY, title TEXT, owner_username TEXT);"""

# Creates an options table if it doesn't already exist with an auto-incremented id as a primary key, an option_text column, and a poll_id column which is a foreign key that references the primary key of the id column in the polls table.
CREATE_OPTIONS = """CREATE TABLE IF NOT EXISTS options
(id SERIAL PRIMARY KEY, option_text TEXT, poll_id INTEGER, FOREIGN KEY(poll_id) REFERENCES polls (id));"""

# Creates a votes table if it doesn't already exist with an username column and an option_id column which is a foreign key that references the primary key of the id column in the options table.
CREATE_VOTES = """CREATE TABLE IF NOT EXISTS votes
(username TEXT, option_id INTEGER, vote_timestamp INTEGER, FOREIGN KEY(option_id) REFERENCES options (id));"""

#
SELECT_POLL = "SELECT * FROM polls WHERE id = %s;"

# Selects all of the colummns for each record in the polls table.
SELECT_ALL_POLLS = "SELECT * FROM polls;"

# Selects all columns from the options table that match the passed in poll_id.
SELECT_POLL_OPTIONS = "SELECT * FROM options WHERE poll_id = %s;"

# Selects all of the colummns for each record in the polls table as well as the options that correspond for those polls where the poll is the most recent poll.
SELECT_LATEST_POLL = """SELECT * FROM poll WHERE polls.id = (
    SELECT id FROM polls ORDER BY id DESC LIMIT 1
);"""

SELECT_OPTION = "SELECT * FROM options WHERE id = %s;"

SELECT_VOTES_FOR_OPTION = "SELECT * FROM votes WHERE option_id = %s;"

# Inserts a new poll record and returns the auto-incremented/generated id value of that new record.
INSERT_POLL_RETURN_ID = "INSERT INTO polls (title, owner_username) VALUES (%s, %s) RETURNING id;"

# Inserts a new options record into the new options table.
INSERT_OPTION_RETURN_ID = "INSERT INTO options (option_text, poll_id) VALUES (%s, %s) RETURNING id;"

# Inserts a new vote record into the votes tab
INSERT_VOTE = "INSERT INTO votes (username, option_id, vote_timestamp) VALUES (%s, %s, %s);"

@contextmanager
def get_cursor(connection):
        with connection:
            with connection.cursor() as cursor:
                yield cursor

def create_tables(connection):
    with get_cursor(connection) as cursor:
        cursor.execute(CREATE_POLLS)
        cursor.execute(CREATE_OPTIONS)
        cursor.execute(CREATE_VOTES)

# -- Polls --

def create_poll(connection, title: str, owner: str):
    with get_cursor(connection) as cursor:
        # Will return the id column of the new record created in the polls table
        cursor.execute(INSERT_POLL_RETURN_ID, (title, owner))

        # Will get the returned id
        poll_id = cursor.fetchone()[0]
        return poll_id

def get_polls(connection) -> list[Poll]:
    with get_cursor(connection) as cursor:
        cursor.execute(SELECT_ALL_POLLS)

        return cursor.fetchall()

def get_poll(connection, poll_id: int) -> Poll:
    with get_cursor(connection) as cursor:
        cursor.execute(SELECT_POLL, (poll_id,))
        
        return cursor.fetchone()

def get_latest_poll(connection) -> Poll:
    with get_cursor(connection) as cursor:
        cursor.execute(SELECT_LATEST_POLL)

        return cursor.fetchone()


def get_poll_options(connection, poll_id: int) -> list[Option]:
    with get_cursor(connection) as cursor:
        cursor.execute(SELECT_POLL_OPTIONS, (poll_id,))
        
        return cursor.fetchall()

# -- Options --

def get_option(connection, option_id: int) -> Option:
    with get_cursor(connection) as cursor:
        cursor.execute(SELECT_OPTION, (option_id,))
        
        return cursor.fetchone()

def add_option(connection, option_text, poll_id: int):
    with get_cursor(connection) as cursor:
        cursor.execute(INSERT_OPTION_RETURN_ID, (option_text, poll_id))
        option_id = cursor.fetchone()[0]

        return option_id

# -- Votes --

def get_votes_for_option(connection, option_id: int) -> list[Vote]:
    with get_cursor(connection) as cursor:
        cursor.execute(SELECT_VOTES_FOR_OPTION, (option_id,))

        return cursor.fetchall()

def add_poll_vote(connection, username: str, vote_timestamp: float, option_id: int):
    with get_cursor(connection) as cursor:
        cursor.execute(INSERT_VOTE, (username, option_id, vote_timestamp))