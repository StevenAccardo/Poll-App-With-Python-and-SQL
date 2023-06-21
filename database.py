from psycopg2.extras import execute_values

# Types
Poll = tuple[int, str, str]
Vote = tuple[str, int]
PollWithOption = tuple[int, str, str, int, str, int]
PollResults = tuple[int, str, int, float]

# SERIAL is a short way for us to tell PostgreSQL that we want the id to be an integer that is auto-incremented for each record inserted
# Creates a polls table if it doesn't already exist with an auto-incremented id as a primary key, a title column, and an owner_username column.
CREATE_POLLS = """CREATE TABLE IF NOT EXISTS polls
(id SERIAL PRIMARY KEY, title TEXT, owner_username TEXT);"""

# Creates an options table if it doesn't already exist with an auto-incremented id as a primary key, an option_text column, and a poll_id column which is a foreign key that references the primary key of the id column in the polls table.
CREATE_OPTIONS = """CREATE TABLE IF NOT EXISTS options
(id SERIAL PRIMARY KEY, option_text TEXT, poll_id INTEGER, FOREIGN KEY(poll_id) REFERENCES polls (id));"""

# Creates a votes table if it doesn't already exist with an username column and an option_id column which is a foreign key that references the primary key of the id column in the options table.
CREATE_VOTES = """CREATE TABLE IF NOT EXISTS votes
(username TEXT, option_id INTEGER, FOREIGN KEY(option_id) REFERENCES options (id));"""

# Selects all of the colummns for each record in the polls table.
SELECT_ALL_POLLS = "SELECT * FROM polls;"

# Selects all of the colummns for each record in the polls table as well as the options that correspond for those polls where the poll is the value of the id passed into the query.
SELECT_POLL_WITH_OPTIONS = """SELECT * FROM polls
JOIN options ON polls.id = options.poll_id
WHERE polls.id = %s;"""

# Selects all of the colummns for each record in the polls table as well as the options that correspond for those polls where the poll is the most recent poll.
SELECT_LATEST_POLL = """SELECT * FROM polls
JOIN options ON polls.id = options.poll_id
WHERE polls.id = (
    SELECT id FROM polls ORDER BY id DESC LIMIT 1
);"""

# Return all records from the options table and any matching records from the votes table, group the records with matching options.id into on record. Then we want to return the options.id and options.text column.
# Additionally, we want to return the count of each votes.option_id, which is essentially how many votes were made for that option, returning it as a column titled vote_count.
# We also want to return a column that portrays the percentage of votes of that option wrt the total votes for all options. We do this by dividing the vote count for each option by the sum of the vote count for each option.
# The OVER() window function is used to allow the calculation fo the percentage to have data of the whole COUNT(votes.option_id) column for each record, otherwise without the window function the sum would be calculated just on a single row, which wouldn't yield the required sum we are interested in.
SELECT_POLL_VOTE_DETAILS = """SELECT
options.id,
options.option_text,
COUNT(votes.option_id) AS vote_count,
COUNT(votes.option_id) / SUM(COUNT(votes.option_id)) OVER() * 100.0 AS vote_percentage
FROM options
LEFT JOIN votes ON options.id = votes.option_id
WHERE options.poll_id = %s
GROUP BY options.id;"""

# Selects all of the votes from a specific option, assigns each one a random float value between 0 to 1.0, orders the rows based on these generated random numbers, then returns the first record.
SELECT_RANDOM_VOTE = "SELECT * FROM votes WHERE option_id = %s ORDER BY RANDOM() LIMIT 1;"

# Inserts a new poll record and returns the auto-incremented/generated id value of that new record.
INSERT_POLL_RETURN_ID = "INSERT INTO polls (title, owner_username) VALUES (%s, %s) RETURNING id;"

# Inserts a new options record into the new options table.
INSERT_OPTION = "INSERT INTO options (option_text, poll_id) VALUES %s;"

# Inserts a new vote record into the votes tab
INSERT_VOTE = "INSERT INTO votes (username, option_id) VALUES (%s, %s);"


def create_tables(connection):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(CREATE_POLLS)
            cursor.execute(CREATE_OPTIONS)
            cursor.execute(CREATE_VOTES)


def get_polls(connection) -> list[Poll]:
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(SELECT_ALL_POLLS)
            return cursor.fetchall()


def get_latest_poll(connection) -> list[PollWithOption]:
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(SELECT_LATEST_POLL)
            return cursor.fetchall()


def get_poll_details(connection, poll_id: int) -> list[PollWithOption]:
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(SELECT_POLL_WITH_OPTIONS, (poll_id,))
            return cursor.fetchall()


def get_poll_and_vote_results(connection, poll_id: int) -> list[PollResults]:
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(SELECT_POLL_VOTE_DETAILS, (poll_id,))
            return cursor.fetchall()


def get_random_poll_vote(connection, option_id: int) -> Vote:
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(SELECT_RANDOM_VOTE, (option_id,))
            return cursor.fetchone()


def create_poll(connection, title: str, owner: str, options: list[str]):
    with connection:
        with connection.cursor() as cursor:
            # Will return the id column of the new record created in the polls table
            cursor.execute(INSERT_POLL_RETURN_ID, (title, owner))

            # Will get the returned id
            poll_id = cursor.fetchone()[0]
            option_values = [(option_text, poll_id) for option_text in options]

            # The execute_values functiion is helper function for iterating through a list and executing SQL for each index in the list of values. It replaces handwritten code below.
            # for option_value in option_values:
            #   cursor.execute(INSERT_OPTION, option_value)
            execute_values(cursor, INSERT_OPTION, option_values)

def add_poll_vote(connection, username: str, option_id: int):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(INSERT_VOTE, (username, option_id))