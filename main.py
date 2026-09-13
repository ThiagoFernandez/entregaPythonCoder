import os
import json
import random
import hashlib
import smtplib
import getpass  # Cambiado de pwinput a getpass
import secrets

from datetime import datetime, timedelta
from email.message import EmailMessage
from cryptography.fernet import Fernet
from email_validator import validate_email, EmailNotValidError

from users import User
from usersManager import UserManager

DEV_MODE = True

# ================= FILE =================

def saveFile(fileName: str, fileVar: dict) -> None:
    """Save data to JSON file."""
    with open(f"./{fileName}.json", "w") as f:
        json.dump(fileVar, f, indent=4)


def initializeFiles(fileName: str) -> dict:
    """Load or initialize JSON file."""
    try:
        with open(f"./{fileName}.json", "r") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {"users": {}}
        saveFile(fileName, data)
    return data

# ================= CRYPTO =================

KEY_PATH = "./secret.key"

def loadOrCreateKey() ->bytes:
    """Load existing key or create a new one."""
    if os.path.exists(KEY_PATH):
        with open(KEY_PATH, "rb") as f:
            return f.read()
    key = Fernet.generate_key()
    with open(KEY_PATH, "wb") as f:
        f.write(key)
    return key


cipher = Fernet(loadOrCreateKey())

def encrypt_text(text: str) -> str:
    """Encrypt plain text."""
    return cipher.encrypt(text.encode()).decode()

def decrypt_text(token: str) -> str:
    """Decrypt encrypted text."""
    return cipher.decrypt(token.encode()).decode()

# ================= EMAIL =================

def sendEmail(subject: str, body: str, to_email: str) -> None:
    """Send or simulate an email."""
    if DEV_MODE:
        print("\n--- EMAIL SIMULADO ---")
        print(f"To: {to_email}")
        print(f"Subject: {subject}")
        print(body)
        print("----------------------\n")
    else:
        msg = EmailMessage()
        msg["From"] = "todolistwithpy@gmail.com"
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.set_content(body)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login("todolistwithpy@gmail.com", "fqyd atpz bqdn fflg")
            smtp.send_message(msg)

def input_valid_email() ->str:
    """Ask for a valid email."""
    while True:
        try:
            email = validate_email(input("Email: ").strip()).email
            return email
        except EmailNotValidError:
            print("Invalid email format")


def verify_email_code(email: str) -> bool:
    code = secrets.randbelow(9000) + 1000   # uniforme 1000–9999
    sendEmail("Confirmation code", f"Your code: {code}", email) # igual pongo el code aca para q se vea pero el standar es q no se vea el codigo

    start = datetime.now()
    try:
        entered = int(input("Enter code: "))
    except ValueError:
        return False

    if datetime.now() - start > timedelta(minutes=5):
        print("Code expired")
        return False

    if entered != code:
        print("Invalid code")
        return False

    return True

# ================= DNI =================

def validate_dni() ->str:
    """Validate and encrypt DNI."""
    used_dnis = [
        decrypt_text(u["dni"])
        for u in manager.users_data.values()
    ]

    while True:
        try:
            dni = int(input("DNI: "))
            if 10000000 <= dni <= 99999999 and str(dni) not in used_dnis:
                encrypted_dni = encrypt_text(str(dni))
                return encrypted_dni
        except ValueError:
            pass
        print("Invalid or duplicated DNI")

# ================= REGISTER =================

def validate_username() ->str:
    """Validate username."""
    while True:
        username = input("Username: ").strip()
        if not username:
            print("Empty username")
        elif manager.user_exists(username):
            print("User already exists")
        else:
            break
    return username

def validate_password() ->str:
    """Ask and hash password."""
    while True:
        # getpass no usa el argumento 'mask', solo el prompt
        password = getpass.getpass("Password: ")
        confirm = getpass.getpass("Repeat password: ")
        if password and password == confirm:
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            break
        print("Passwords do not match")
    return password_hash

def userRegister()  -> User:
    """Register a new user."""
    while True:
        username = validate_username()

        password_hash = validate_password()

        email = input_valid_email()
        if not verify_email_code(email):
            print("Email verification failed")

        else:
            encrypted_dni = validate_dni()

            user = manager.create_user(
                username=username,
                password_hash=password_hash,
                email=email,
                encrypted_dni=encrypted_dni,
                phrases=[
                    "Session closed successfully.",
                    "See you next time!",
                    "Exiting without errors. Impressive.",
                    "Take care and come back soon!",
                    "The program rests now. Gently.",
                    "Clean exit. Very professional of you.",
                    "I'll miss you (a little)."
                ]
            )
            break

    saveFile("usersFile", usersFile)
    return user


# ================= LOGIN =================

def change_password(user: User) -> None:
    """Change user password."""
    pwd = getpass.getpass("Current password: ")
    if user.check_password(pwd):
        new_pwd = getpass.getpass("New password: ")
        user.change_password(new_pwd)
        manager.save_user(user)
        saveFile("usersFile", usersFile)
        print("Password updated")
    else:
        print("Wrong password")

def input_new_password_plain() ->str:
    """Ask for new password."""
    while True:
        pwd = getpass.getpass("New password: ")
        confirm = getpass.getpass("Repeat password: ")
        if pwd and pwd == confirm:
            return pwd
        print("Passwords do not match")

def userLogin() ->User | None:
    """Login or reset password."""
    users = list(manager.users_data.keys())
    if not users:
        print("No users registered")
        return None

    for i, u in enumerate(users, 1):
        print(f"{i}. {u}")

    try:
        username = users[int(input("Choose: ")) - 1]
    except (ValueError, IndexError):
        return None

    try:
        option = int(input("1. Enter password\n2. Reset password\nOption: "))
    except ValueError:
        return None

    if option == 1:
        for _ in range(3):
            password = getpass.getpass("Password: ")

            user = manager.authenticate(username, password)
            if user:
                return user

            print("Wrong password")

        print("User banned for 5 minutes")
        manager.ban_user(username)
        saveFile("usersFile", usersFile)
        return None

    elif option == 2:
        # Nota: Aquí faltaba definir 'user' antes de usar user.email.
        # Asegúrate de que manager tenga un método para buscar el usuario por nombre.
        user_data = manager.users_data.get(username)
        if not user_data:
             return None

        email = input_valid_email()

        if email != user_data.get("email"):
            print("Email does not match user")
            return None

        if verify_email_code(email):
            plain_pwd = input_new_password_plain()
            # Asumiendo que necesitas cargar el objeto User primero
            user_obj = manager.get_user(username)
            user_obj.change_password(plain_pwd)
            manager.save_user(user_obj)
            saveFile("usersFile", usersFile)

# ================= PHRASES =================

def managePhrasesMenu(user: User) -> None:
    """Manage user phrases."""
    while True:
        print("\n1. Show phrases\n2. Add phrase\n3. Delete phrase\n4. Back")

        try:
            op = int(input("Option: "))

            if op == 1:
                if not user.phrases:
                    print("No phrases yet.")
                else:
                    for i, p in enumerate(user.phrases, 1):
                        print(f"{i}. {p}")

            elif op == 2:
                phrase = input("New phrase: ").strip()
                if phrase:
                    user.add_phrase(phrase)
                    manager.save_user(user)
                    saveFile("usersFile", usersFile)

            elif op == 3:
                if not user.phrases:
                    print("No phrases to delete.")
                    continue

                for i, p in enumerate(user.phrases, 1):
                    print(f"{i}. {p}")

                idx = int(input("Choose one: ")) - 1
                if 0 <= idx < len(user.phrases):
                    user.remove_phrase(user.phrases[idx])
                    manager.save_user(user)
                    saveFile("usersFile", usersFile)

            elif op == 4:
                return

        except ValueError:
            print("Invalid option")


# ================= SETTINGS =================

def userSettingsMenu(user: User) ->int | None:
    """User settings menu."""
    while True:
        print("\n1. Show settings\n2. Change email\n3. Change password")
        print("4. Manage phrases\n5. Delete account\n6. Back")

        try:
            op = int(input("Option: "))

            if op == 1:
                decrypt_dni = decrypt_text(user.dni)
                User.show_settings(user, decrypt_dni)

            elif op == 2:
                new_email = input_valid_email()
                if verify_email_code(new_email):
                    user.change_email(new_email)

            elif op == 3:
                change_password(user)

            elif op == 4:
                managePhrasesMenu(user)

            elif op == 5:
                manager.delete_user(user.username)
                saveFile("usersFile", usersFile)
                return -1

            elif op == 6:
                return

            manager.save_user(user)
            saveFile("usersFile", usersFile)

        except ValueError:
            print("Invalid option")


# ================= MAIN MENU =================

def showMenu(user: User) -> None:
    """Main user menu."""
    while True:
        print(f"\nWelcome {user.username}")
        print("1. Placeholder\n2. Display users\n3. Settings\n4. Exit")

        try:
            op = int(input("Option: "))
            if op == 1:
                print("Coming soon")
            elif op == 2:
                for u in manager.users_data:
                    print("-", u)
            elif op == 3:
                if userSettingsMenu(user) == -1:
                    return
            elif op == 4:
                if user.phrases:
                    print(random.choice(user.phrases))
                return
        except ValueError:
            print("Invalid option")

# ================= START MENU =================

def start_menu() -> None:
    """Start menu."""
    while True:
        print("\n1. Login\n2. Register\n3. Exit")
        try:
            op = int(input("Option: "))
            if op == 1:
                user = userLogin()
                if user:
                    showMenu(user)
            elif op == 2:
                user = userRegister()
                showMenu(user)
            elif op == 3:
                break
        except ValueError:
            print("Invalid option")


# ================= ENTRY =================

usersFile = initializeFiles("usersFile")
manager = UserManager(usersFile["users"])

start_menu()
