import database
from connections import create_connection

class Option:
    def __init__(self, option_text: str, poll_id: str, _id: int = None):
        self.id = _id
        self.text = option_text
        self.poll_id = poll_id

    # Short for represent. Used to show what the object would look like in a string format
    def __repr__(self) -> str:
        return f"Poll({self.text!r}, {self.poll_id!r}, {self.id!r})"
    
    def save(self):
        connection = create_connection()
        new_option_id = database.add_option(connection, self.text, self.poll_id)
        connection.close()
        self.id = new_option_id

    def vote(self, username: str):
        connection = create_connection()
        database.add_poll_vote(connection, username, self.id)
        connection.close()

    @classmethod
    def get(cls, option_id: int) -> "Option":
        connection = create_connection()
        option = database.get_option(connection, option_id)
        connection.close()

        return cls(option[1], option[2], option[0])
    
    @property
    def votes(self) -> list[database.Vote]:
        connection = create_connection()
        votes = database.get_votes_for_option(connection, self.id)
        connection.close()

        return votes
    
