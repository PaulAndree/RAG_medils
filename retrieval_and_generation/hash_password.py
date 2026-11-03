"""Print an Argon2 hash for manual insertion into PostgreSQL."""
from getpass import getpass

from pwdlib import PasswordHash


if __name__ == "__main__":
    password = getpass("Password: ")
    if not password or password != getpass("Confirm password: "):
        raise SystemExit("Passwords must be nonempty and match")
    print(PasswordHash.recommended().hash(password))
