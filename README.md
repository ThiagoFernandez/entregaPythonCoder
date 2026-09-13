# entregaPythonCoder

A multi-user account system for the command line, written in Python. It handles registration and
login with email verification, encrypts each user's national ID (DNI) with Fernet, hashes
passwords, and locks an account for five minutes after three failed login attempts.

> **Learning project.** Built to practice applied cryptography, email verification flows and
> on-disk state, not to run in production. See [Known limitations](#known-limitations) before
> storing any real data.

---

## Features

- **Registration with email verification** — a one-time code (generated with `secrets`) must be entered before the account is created; if verification fails, nothing is stored
- **Fernet-encrypted DNI** — the national ID is encrypted at rest and only decrypted to display it; duplicate DNIs are rejected
- **Hashed passwords** — stored as SHA-256 digests, never in plain text
- **Three attempts and a 5-minute lock** — the ban is saved with an ISO timestamp (`banUntil`), so it survives closing the program and auto-lifts when it expires
- **Password reset by email** — verifies ownership of the registered email before letting you set a new password
- **Custom farewell phrases** — each user keeps their own list; a random one is printed on exit
- **Dev mode** — with `DEV_MODE = True` (default) emails are simulated (printed to the console), so the whole flow runs without an SMTP server

---

## Requirements

**Python 3.10+** (uses the `X | None` union syntax, PEP 604)

```bash
pip install cryptography email-validator
```

- `cryptography` — Fernet encryption for the DNI
- `email_validator` — real email validation on input

> There is no `requirements.txt` yet; install the two dependencies with the line above.

---

## Usage

```bash
git clone https://github.com/ThiagoFernandez/entregaPythonCoder.git
cd entregaPythonCoder
pip install cryptography email-validator
python main.py
```

By default `DEV_MODE = True`, so verification codes are **printed to the console** instead of
emailed — no mail setup needed to try it. To send real email, set `DEV_MODE = False` and configure
your own SMTP account in `sendEmail`.

The first run creates `usersFile.json` (user data) and `secret.key` (the Fernet key). Neither
should be committed — see below.

---

## Structure

```
entregaPythonCoder/
├── main.py           # UI: menus, registration/login flows, email and crypto helpers
├── users.py          # User entity: password check/change, ban logic, phrases
├── usersManager.py   # UserManager: persistence, lookup and authentication
├── usersFile.json    # user store (created on first run)
└── secret.key        # Fernet key (created on first run)
```

- **`main.py`** drives every menu and orchestrates the flows (register, login, settings).
- **`users.py`** is the `User` entity — it knows how to check and change its own password, ban and unban itself, and manage its farewell phrases.
- **`usersManager.py`** is the persistence and auth layer — it builds `User` objects from the JSON store, saves them back, authenticates credentials and applies bans.

---

## How it works

- **Two layers around the data**: `UserManager` reads and writes the raw dict in `usersFile.json`; `User` is the in-memory object with the behaviour. The manager rebuilds a `User` from storage, the flow mutates it, and the manager saves it back.
- **The DNI never touches disk in plain text**: `validate_dni` encrypts it with Fernet before storing, and `show_settings` decrypts it only to print it.
- **Bans survive restarts**: the lock is stored as an ISO timestamp in `banUntil`, and `unban_if_expired` clears it automatically once the five minutes are up.
- **Verification gates registration**: `userRegister` only calls `create_user` when `verify_email_code` returns `True`.

---

## Known limitations

- **Passwords are hashed with SHA-256 (no salt)**: fine for practice, but a real system should use `bcrypt` or `PBKDF2` with a salt.
- **`secret.key` and `usersFile.json` should not be committed**: the key decrypts every stored DNI, and the JSON holds emails and password hashes. Add a `.gitignore` for both.
- **The verification code is shown in the console** (dev convenience), even outside `DEV_MODE`.
- **The main menu still has a placeholder** (option 1 → "Coming soon").
