import json
import secrets

from email_validator import validate_email

__all__ = ["generate"]


def generate():
    secret_key = secrets.token_hex()

    while True:
        first_name = input("\nEnter the first name of an admin: ").strip()

        if 0 < len(first_name) < 64:
            break
        else:
            print("The username is too short or too long.")

    while True:
        last_name = input("\nEnter the last name of an admin: ").strip()

        if 0 < len(last_name) < 64:
            break
        else:
            print("The username is too short or too long.")

    while True:
        email = input("\nEnter the email address of an admin: ").strip()

        if not validate_email(email):
            print("The email address is invalid!")
        else:
            break

    for_json = {"SECRET_KEY": secret_key, "USER": (first_name, last_name, email)}

    with open("config.json", "w") as file:
        file.write(json.dumps(for_json))
