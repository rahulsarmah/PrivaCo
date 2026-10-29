"""
Broker Opt-Out Tracker  (version 0.1)

Tracks which data brokers you have asked to remove your information,
reminds you when to re-check, and writes removal request emails.
Everything stays on your own computer.
"""

import json
from datetime import date, timedelta
from pathlib import Path

# Your progress is saved in this file, next to the script.
SAVE_FILE = Path(__file__).with_name("progress.json")

# Brokers often re-add people, so we re-check after this many days.
RECHECK_DAYS = 90

# The broker list. Each broker has a name and an opt-out page.
# NOTE: these pages change often. Verify each link before relying on it.
BROKERS = [
    {"name": "Spokeo", "url": "https://www.spokeo.com/optout"},
    {"name": "Whitepages", "url": "https://www.whitepages.com/suppression-requests"},
    {"name": "BeenVerified", "url": "https://www.beenverified.com/app/optout/search"},
    {"name": "Intelius", "url": "https://www.intelius.com/opt-out"},
    {"name": "Radaris", "url": "https://radaris.com/control/privacy"},
    {"name": "TruePeopleSearch", "url": "https://www.truepeoplesearch.com/removal"},
    {"name": "FastPeopleSearch", "url": "https://www.fastpeoplesearch.com/removal"},
    {"name": "PeopleFinders", "url": "https://www.peoplefinders.com/opt-out"},
]


# ---------- Saving and loading ----------

def load_progress():
    """Read saved progress. Returns {} if nothing has been saved yet."""
    if SAVE_FILE.exists():
        return json.loads(SAVE_FILE.read_text())
    return {}


def save_progress(progress):
    """Write progress to disk as readable JSON."""
    SAVE_FILE.write_text(json.dumps(progress, indent=2))


# ---------- Status logic ----------

def get_status(broker_name, progress):
    """Return a short text describing where this broker stands."""
    if broker_name not in progress:
        return "NOT DONE"

    done_on = date.fromisoformat(progress[broker_name])
    recheck_on = done_on + timedelta(days=RECHECK_DAYS)

    if date.today() >= recheck_on:
        return f"RE-CHECK DUE (requested {done_on})"
    return f"done {done_on}, re-check on {recheck_on}"


# ---------- Menu actions ----------

def show_list(progress):
    print("\n--- Data brokers ---")
    for number, broker in enumerate(BROKERS, start=1):
        print(f"{number}. {broker['name']:<18} {get_status(broker['name'], progress)}")


def choose_broker():
    """Ask the user for a broker number. Returns the broker, or None."""
    choice = input("Broker number: ").strip()
    if not choice.isdigit() or not (1 <= int(choice) <= len(BROKERS)):
        print("That is not a valid number.")
        return None
    return BROKERS[int(choice) - 1]


def open_instructions(progress):
    broker = choose_broker()
    if broker:
        print(f"\nOpen this page in your browser and follow the steps:\n{broker['url']}")
        print("When you have submitted the request, come back and choose 'Mark as done'.")


def mark_done(progress):
    broker = choose_broker()
    if broker:
        progress[broker["name"]] = date.today().isoformat()
        save_progress(progress)
        print(f"Saved. {broker['name']} marked as done today.")


def write_email():
    broker = choose_broker()
    if not broker:
        return

    # Your details are only used to build the text below. Nothing is stored.
    name = input("Your full name: ").strip()
    email = input("Your email address: ").strip()

    message = f"""Subject: Request to delete my personal information

To the {broker['name']} privacy team,

I am requesting that you delete all personal information you hold about me
and stop selling or sharing it, under applicable privacy laws including the
CCPA/CPRA (California) and the GDPR (EU/UK), where they apply to me.

Name: {name}
Contact email: {email}

Please also remove me from any people-search listings and confirm in
writing once this is complete.

Thank you,
{name}
"""
    print("\n--- Copy the email below ---\n")
    print(message)


# ---------- Main menu loop ----------

def main():
    progress = load_progress()

    while True:
        print("\n=== Broker Opt-Out Tracker ===")
        print("1. Show all brokers and status")
        print("2. Get opt-out link for a broker")
        print("3. Mark a broker as done")
        print("4. Write a removal email")
        print("5. Quit")

        choice = input("Choose 1-5: ").strip()

        if choice == "1":
            show_list(progress)
        elif choice == "2":
            show_list(progress)
            open_instructions(progress)
        elif choice == "3":
            show_list(progress)
            mark_done(progress)
            write_email()
        elif choice == "5":
            print("Goodbye!")
            break
        else:
            print("Please choose a number from 1 to 5.")


# This line means: only run main() when you run this file directly.
if __name__ == "__main__":
    main()
