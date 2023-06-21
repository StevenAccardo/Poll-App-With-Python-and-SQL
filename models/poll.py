import database
from models import Option

class Poll:
    def __init__(self, title: str, owner: str, _id: int = None):
        self.id = _id
        self.title = title
        self.owner = owner

    # Short for represent. Used to show what the object would look like in a string format
    def __repr__(self):
        return f"Poll({self.title!r}, {self.owner!r}, {self.id!r})"
    
    def save(self):
        connection = create_connection()
        new_poll_id = database.create_poll(connection, self.title, self.owner)
        connection.close()
        self.id = new_poll_id

    def add_option(self, option_text: str):
        Option(option_text, self.id).save()

    @property
    def options(self) -> list[Option]:
        connection = create_connection()
        options = database.get_poll_options(connection, self.id)
        connection.close()
        
        return [Option(option[1], option[2], option[0]) for option in options]
    
    @classmethod
    def get(cls, poll_id: int) -> "Poll":
        connection = create_connection()
        poll = database.get_poll(connection, poll_id)
        connection.close()

        return cls(poll[1], poll[2], poll[0])
    
    @classmethod
    def all(cls) -> list["Poll"]:
        connection = create_connection()
        polls = database.get_poll(connection)
        connection.close()
        
        return [cls(poll[1], poll[2], poll[0]) for poll in polls]
    
    @classmethod
    def latest(cls) -> "Poll":
        connection = create_connection()
        poll = database.get_poll(connection)
        connection.close()
        
        return cls(poll[1], poll[2], poll[0])