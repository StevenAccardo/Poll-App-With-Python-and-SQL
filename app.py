import random
import datetime
import pytz

import database
from models.poll import Poll
from models.option import Option
from connection_pool import get_connection


DATABASE_PROMPT = "Enter the DATABASE_URI value or leave empty to load from .env file: "
MENU_PROMPT = """-- Menu --

1) Create new poll
2) List open polls
3) Vote on a poll
4) Show poll votes
5) Select a random winner from a poll option
6) Exit

Enter your choice: """
NEW_OPTION_PROMPT = "Enter new option text (or leave empty to stop adding options): "


def prompt_create_poll() -> None:
    poll_title = input("Enter poll title: ")
    poll_owner = input("Enter poll owner: ")
    poll = Poll(poll_title, poll_owner)
    poll.save()

    # While the user continues to type and enter a value for an option, keep running this loop. Once the user does not type into the input and presses enter, the value will no longer be true and execution will move outside of the while loop.
    while (new_option := input(NEW_OPTION_PROMPT)):
        poll.add_option(new_option)


def list_open_polls() -> None:
    for poll in Poll.all():
        print(f"{poll.id}: {poll.title} (created by {poll.owner})")


def prompt_vote_poll() -> None:
    poll_id = int(input("Enter poll would you like to vote on: "))

    _print_poll_options(Poll.get(poll_id).options)

    option_id = int(input("Enter option you'd like to vote for: "))
    username = input("Enter the username you'd like to vote as: ")
    Option.get(option_id).vote(username)


def _print_poll_options(options: list[Option]) -> None:
    for option in options:
        print(f"{option.id}: {option.text}")

def _print_votes_for_options(options: list[Option]) -> None:
    for option in options:
        print(f"-- {option.text} --")
        for vote in option.votes:
            # Takes the epoch/unix/posix timestamp that was stored in the database and converts it to a naive UTC datetime object (if we don't use the utcfromtimestamp method, then the datetime object will be converted to a naive local datetime vs naive UTC datetime).
            naive_datetime = datetime.datetime.utcfromtimestamp(vote[2])
            # Converts the naive datetime object to an aware datetime object set to a UTC timezone.
            utc_datetime = pytz.utc.localize(naive_datetime)
            # Adjusts the aware UTC datetime object to an aware datetime object set to the hard-coded PST timezone.
            local_datetime = utc_datetime.astimezone(pytz.timezone("US/Pacific"))
            # Converts the aware datetime object to a string in the desired format.
            local_datetime_str = local_datetime.strftime("%m-%d-%Y %H:%M")
            print(f"\t- {vote[0]} on {local_datetime_str}")


def show_poll_votes() -> None:
    poll_id = int(input("Enter poll you would like to see votes for: "))
    options = Poll.get(poll_id).options
    votes_per_option = [len(option.votes) for option in options]
    total_votes = sum(votes_per_option)

    try:
        for option, votes in zip(options, votes_per_option):
            percentage = votes / total_votes * 100
            print(f"{option.text} got {votes} votes ({percentage:.2f}% of total)")
    except ZeroDivisionError:
        print("No votes cast for this poll yet.")

    vote_log = input("Would you like to see the vote log? (y/N) ")

    if vote_log == "y":
        _print_votes_for_options(options)


def randomize_poll_winner() -> None:
    poll_id = int(input("Enter poll you'd like to pick a winner for: "))
    _print_poll_options(Poll.get(poll_id).options)

    option_id = int(input("Enter which is the winning option, we'll pick a random winner from voters: "))
    votes = Option.get(option_id).votes
    winner = random.choice(votes)
    print(f"The randomly selected winner is {winner[0]}.")


MENU_OPTIONS = {
    "1": prompt_create_poll,
    "2": list_open_polls,
    "3": prompt_vote_poll,
    "4": show_poll_votes,
    "5": randomize_poll_winner
}


def menu():
    # Asks user to enter the hosted PostgreSQL database uri to be used for this application, otherwise it will try and use one stored in the .env file.
    with get_connection() as connection:
        database.create_tables(connection)

    while (selection := input(MENU_PROMPT)) != "6":
        try:
            MENU_OPTIONS[selection]()
        except KeyError:
            print("Invalid input selected. Please try again.")


menu()