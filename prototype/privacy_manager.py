"""
Personal Privacy Manager  (version 0.2)

Keep a list of services that hold your data (social media, telecoms),
write data requests under India's DPDP Act, and track whether they replied.
Everything stays on your own computer in one file: privacy_data.json
"""

import json
from datetime import date, timedelta
from pathlib import Path

DATA_FILE = Path(__file__).with_name("privacy_data.json")

# How long we wait for a reply before marking a request OVERDUE.
# This is a tracking aid, not a legal deadline (see README notes).
RESPONSE_DAYS = 90

# Starting list. "data" is a general description of what such a service
# typically holds. Check each company's own privacy policy for the truth.
DEFAULT_SERVICES = [
    {"name": "Instagram", "category": "Social media",
     "data": "profile, phone/email, posts, messages, location, device info"},
    {"name": "Facebook", "category": "Social media",
     "data": "profile, friends, posts, messages, location, ad interests"},
    {"name": "WhatsApp", "category": "Social media",
     "data": "phone number, contacts, profile, usage and device info"},
    {"name": "X (Twitter)", "category": "Social media",
     "data": "profile, posts, messages, email/phone, ad interests"},
    {"name": "YouTube / Google", "category": "Social media",
     "data": "watch history, searches, location, email, device info"},
    {"name": "Snapchat", "category": "Social media",
     "data": "profile, snaps metadata, contacts, location"},
    {"name": "LinkedIn", "category": "Social media",
     "data": "profile, work history, connections, messages"},
    {"name": "Jio", "category": "Telecom",
     "data": "KYC documents, phone number, call/SMS records, location, usage"},
    {"name": "Airtel", "category": "Telecom",
     "data": "KYC documents, phone number, call/SMS records, location, usage"},
    {"name": "Vi (Vodafone Idea)", "category": "Telecom",
     "data": "KYC documents, phone number, call/SMS records, location, usage"},
    {"name": "BSNL", "category": "Telecom",
     "data": "KYC documents, phone number, call/SMS records, location, usage"},
]

# The three kinds of request. Each has a subject line and a body.
REQUEST_TYPES = {
    "access": {
        "label": "Access (what data do you hold about me?)",
        "subject": "Request for access to my personal data",
        "body": (
            "I am a Data Principal under the Digital Personal Data Protection "
            "Act, 2023. Under Section 11, I request a summary of the personal "
            "data you hold about me, the processing activities carried out on "
            "it, and the identities of all other Data Fiduciaries and "
            "Processors with whom you have shared it."
        ),
    },
    "correction": {
        "label": "Correction (fix wrong or outdated data)",
        "subject": "Request for correction of my personal data",
        "body": (
            "I am a Data Principal under the Digital Personal Data Protection "
            "Act, 2023. Under Section 12, I request correction or completion "
            "of inaccurate or incomplete personal data you hold about me. "
            "Please tell me which details you hold so I can specify the "
            "corrections."
        ),
    },
    "erasure": {
        "label": "Erasure (delete my data)",
        "subject": "Request for erasure of my personal data",
        "body": (
            "I am a Data Principal under the Digital Personal Data Protection "
            "Act, 2023. Under Section 12, I request erasure of my personal "
            "data, and I withdraw my consent for its processing. Please erase "
            "all data that you are not legally required to retain, and tell "
            "me which data you must keep and under which legal requirement."
        ),
    },
}

STATUSES = {"1": "replied", "2": "completed", "3": "refused"}


# ---------- Saving and loading ----------

def load_data():
    """Load saved data, or create a fresh starting file on first run."""
    if DATA_FILE.exists():
        return json.loads(DATA_FILE.read_text())
    return {"services": DEFAULT_SERVICES, "requests": []}


def save_data(data):
    DATA_FILE.write_text(json.dumps(data, indent=2))


# ---------- Small helpers ----------

def pick_number(prompt, count):
    """Ask for a number from 1 to count. Returns a 0-based index, or None."""
    answer = input(prompt).strip()
    if not answer.isdigit() or not (1 <= int(answer) <= count):
        print("That is not a valid number.")
        return None
    return int(answer) - 1


def pick_service(data):
    show_services(data)
    index = pick_number("Service number: ", len(data["services"]))
    return None if index is None else data["services"][index]


def pick_request_type():
    keys = list(REQUEST_TYPES)
    for number, key in enumerate(keys, start=1):
        print(f"{number}. {REQUEST_TYPES[key]['label']}")
    index = pick_number("Request type: ", len(keys))
    return None if index is None else keys[index]


def request_state(req):
    """Describe a request: waiting (with days left), overdue, or its status."""
    if req["status"] != "waiting":
        return req["status"].upper()
    deadline = date.fromisoformat(req["sent"]) + timedelta(days=RESPONSE_DAYS)
    days_left = (deadline - date.today()).days
    if days_left < 0:
        return f"OVERDUE by {-days_left} days"
    return f"waiting, {days_left} days left"


# ---------- Menu actions ----------

def show_services(data):
    print("\n--- Your services ---")
    for number, service in enumerate(data["services"], start=1):
        print(f"{number:>2}. {service['name']:<20} [{service['category']}]")


def add_service(data):
    name = input("Service name: ").strip()
    category = input("Category (e.g. Social media, Telecom, Shopping): ").strip()
    held = input("What data do you think it holds? ").strip()
    if not name:
        print("A name is required.")
        return
    data["services"].append(
        {"name": name, "category": category or "Other", "data": held}
    )
    save_data(data)
    print(f"Added {name}.")


def write_request(data):
    service = pick_service(data)
    if not service:
        return
    req_type = pick_request_type()
    if not req_type:
        return

    # Used only to fill in the text below. Not saved anywhere.
    name = input("Your full name: ").strip()
    account = input("Your account detail (username, email or phone number): ").strip()

    template = REQUEST_TYPES[req_type]
    message = (
        f"Subject: {template['subject']}\n\n"
        f"To the Grievance Officer / Data Protection Officer, {service['name']},\n\n"
        f"{template['body']}\n\n"
        f"Name: {name}\n"
        f"Account: {account}\n\n"
        f"Please acknowledge this request and respond within the timeline "
        f"required by law.\n\n"
        f"Regards,\n{name}\n"
    )
    print("\n--- Copy the request below ---\n")
    print(message)

    print(f"Where to send it: look in {service['name']}'s privacy policy for")
    print("the Grievance Officer or Data Protection contact (email or web form).")
    if service["category"].lower() == "telecom" and req_type == "erasure":
        print("\nNote: telecoms must keep some records, such as KYC, under their")
        print("licence rules, so expect a partial refusal. That is normal.")
    print("\nAfter you send it, use 'Log a request I sent' to track it.")


def log_request(data):
    service = pick_service(data)
    if not service:
        return
    req_type = pick_request_type()
    if not req_type:
        return
    data["requests"].append({
        "service": service["name"],
        "type": req_type,
        "sent": date.today().isoformat(),
        "status": "waiting",
        "note": "",
    })
    save_data(data)
    print(f"Logged. Check back in {RESPONSE_DAYS} days if there is no reply.")


def show_requests(data):
    print("\n--- Your requests ---")
    if not data["requests"]:
        print("No requests logged yet.")
        return
    for number, req in enumerate(data["requests"], start=1):
        line = (f"{number:>2}. {req['service']:<20} {req['type']:<11} "
                f"sent {req['sent']}  ->  {request_state(req)}")
        print(line)
        if req["note"]:
            print(f"      note: {req['note']}")


def update_request(data):
    show_requests(data)
    if not data["requests"]:
        return
    index = pick_number("Request number to update: ", len(data["requests"]))
    if index is None:
        return
    print("1. Replied   2. Completed   3. Refused")
    status = STATUSES.get(input("New status: ").strip())
    if not status:
        print("That is not a valid choice.")
        return
    data["requests"][index]["status"] = status
    data["requests"][index]["note"] = input("Short note (optional): ").strip()
    save_data(data)
    print("Updated.")


# ---------- Main menu loop ----------

def main():
    data = load_data()

    # Startup summary: warn about anything overdue.
    overdue = [r for r in data["requests"] if "OVERDUE" in request_state(r)]
    if overdue:
        print(f"\n!! {len(overdue)} request(s) are overdue. Choose option 5 to see them.")

    while True:
        print("\n=== Personal Privacy Manager ===")
        print("1. Show my services")
        print("2. Add a service")
        print("3. Write a request (access / correction / erasure)")
        print("4. Log a request I sent")
        print("5. Show my requests and deadlines")
        print("6. Update a request")
        print("7. Quit")

        choice = input("Choose 1-7: ").strip()

        if choice == "1":
            show_services(data)
        elif choice == "2":
            add_service(data)
        elif choice == "3":
            write_request(data)
        elif choice == "4":
            log_request(data)
        elif choice == "5":
            show_requests(data)
        elif choice == "6":
            update_request(data)
        elif choice == "7":
            print("Goodbye!")
            break
        else:
            print("Please choose a number from 1 to 7.")


if __name__ == "__main__":
    main()
