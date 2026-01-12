import os
import json
import random
import hashlib
import smtplib

import pwinput

from datetime import datetime, timedelta
from email.message import EmailMessage

from cryptography.fernet import Fernet
from email_validator import validate_email, EmailNotValidError

# file section

def saveFile(fileName, fileVar):
    with open(f"./{fileName}.json", "w") as f:
        json.dump(fileVar, f, indent=4)

def initializeFiles(fileName):
    try:
        with open(f"./{fileName}.json", "r") as f:
            dicttt = json.load(f)
            print(f"The {fileName} file was found")
    except json.JSONDecodeError:
        print(f"The {fileName} was empty")
        dicttt = {
            "users": {

            }
        }
        saveFile(fileName, dicttt)
    except FileNotFoundError:
        print(f"The {fileName} was not found")
        dicttt = {
            "users": {

            }
        }
        saveFile(fileName, dicttt)

    return dicttt

# cryptography section
KEY_PATH = "./secret.key"

def loadOrCreateKey():
    if os.path.exists(KEY_PATH):
        with open(KEY_PATH, "rb") as f:
            return f.read()
    else:
        key = Fernet.generate_key()
        with open(KEY_PATH, "wb") as f:
            f.write(key)
        return key

key = loadOrCreateKey()
cipher = Fernet(key)

def encrypt_text(text: str) -> str:
    return cipher.encrypt(text.encode("utf-8")).decode("utf-8")

def decrypt_text(token: str) -> str:
    return cipher.decrypt(token.encode("utf-8")).decode("utf-8")

# notification section
def recoverPassword():
    print("Feature coming soon")

def sendEmail(subject, body, to_email):
    msg = EmailMessage()
    msg["From"] = "todolistwithpy@gmail.com"
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login("todolistwithpy@gmail.com", "fqyd atpz bqdn fflg")
        smtp.send_message(msg)

# user section

def userRegister():
    usersList = list(usersFile["users"].keys())
    while True:
        newUser = input("Write your username: ")
        if newUser in usersList:
            print(f"{newUser} is already a user | Try again")
        elif newUser.strip() == "":
            print("The username cannot be empty | Try again")
        else:
            break
    while True:
        password = pwinput.pwinput(prompt="Add a password: ", mask="*")
        if password.strip() == "":
            print("The password cannot be empty | Try again")
        else:
            confirmPassword = pwinput.pwinput(prompt="Repeat the new password: ", mask="*")
            if confirmPassword != password:
                print("The password does not match | Try again")
            else:
                hashedPassword = hashlib.sha256(password.encode("utf-8")).hexdigest()
                break
    while True:
        email = input("Add an email: ").strip()
        try:
            info = validate_email(email)
            emailNormalized = info.email

            code = random.randint(1000, 9999)
            sendEmail(
                "confirmation code",
                f"Use this code to validate your email: {code}\nYou have 5 minutes until the code expire",
                emailNormalized
            )
            timeSent = datetime.now()
            try:
                confirmCode = int(input("Enter the code: "))
                timeReceived = datetime.now()
                if timeReceived - timeSent > timedelta(minutes=5):
                    print("Code expired | Try again")
                else:
                    if confirmCode != code:
                        print("The code does not match with the one provided")
                    else:
                        break
            except ValueError:
                print("The code must be a number | Try again")

        except EmailNotValidError as e:
            print("Invalid email:", str(e))


    if usersList:
        encryptDniList = []
        for username in usersList:
            encryptDniList.append(usersFile["users"][username]["dni"])

        usedDnis = []
        for enc in encryptDniList:
            usedDnis.append(decrypt_text(enc))

        while True:
            try:
                newDni = int(input("Add your dni: "))
            except ValueError:
                print("The dni must be a number | Try again")
                continue

            if newDni < 10000000 or newDni > 99999999:
                print("The DNI must have 8 digits | Try again")
                continue

            newDni = str(newDni)

            if newDni in usedDnis:
                print(f"{newDni} is already being used by someone else | Try again")
                continue

            encryptedDni = encrypt_text(newDni)
            break
    else:
        while True:
            try:
                newDni = int(input("Add your dni: "))
            except ValueError:
                print("The dni must be a number | Try again")
                continue

            if newDni < 10000000 or newDni > 99999999:
                print("The DNI must have 8 digits | Try again")
                continue

            newDni = str(newDni)
            encryptedDni = encrypt_text(newDni)
            break
    
    banUntil = (datetime.now() + timedelta(minutes=5)).isoformat()
    usersFile["users"][newUser] = {
        "dni": encryptedDni,
        "email": emailNormalized,
        "password": hashedPassword,
        "ban": False,
        "banUntil": banUntil,
        "phrases": [    
            "Session closed successfully.",
            "See you next time!",
            "Exiting without errors. Impressive.",
            "Take care and come back soon!",
            "The program rests now. Gently.",
            "Clean exit. Very professional of you.",
            "Alright… I'll miss you (a little).",
            "Touch grass now"
            ]
    }
    saveFile("usersFile", usersFile)
    return newUser

def userLogin():
    usersList = list(usersFile["users"].keys())
    if not usersList:
        print("There are no users yet")
        return -1
    else:
        while True:
            for i, user in enumerate(usersList):
                print(f"{i+1}. {user}")
            print(f"{len(usersList)+1}. Go back...")
            try:
                option = int(input("Choose an option: "))
                if option < 1 or option > len(usersList)+1:
                    print(f"The option must be between 1-{len(usersList)+1} | Try again")
                elif option == len(usersList)+1:
                    return -1
                else:
                    userOption = usersList[option-1]
                    if usersFile["users"][userOption]["ban"] != True:
                        break
                    else:
                        now = datetime.now()
                        banUntil = datetime.fromisoformat(usersFile["users"][userOption]["banUntil"])
                        if now > banUntil:
                            usersFile["users"][userOption]["ban"] = False
                            saveFile("usersFile", usersFile)
                            break
                        else:
                            print(f"The user: {userOption} is banned until: {usersFile["users"][userOption]["banUntil"]}")
            except ValueError:
                print("The option must be a number | Try again")
        attempts = 0
        while True:
            if attempts < 3:
                password = pwinput.pwinput(prompt="Write your password: ", mask="*")
                checkPassword = hashlib.sha256(password.encode()).hexdigest()
                if checkPassword == usersFile["users"][userOption]["password"]:
                    return userOption
                else:
                    print("The password does not match | Try again")
                    attempts+=1
            else:
                banUntil = (datetime.now() + timedelta(minutes=5)).isoformat()
                print(f"You failed your 3 attempts | try again at {banUntil}")
                usersFile["users"][userOption]["banUntil"] = banUntil
                usersFile["users"][userOption]["ban"] = True
                saveFile("usersFile", usersFile)
                return -1
        
def userSelectorMenu():
    while True:
        print(f"{'Welcome to the user selector menu':-^60}\n1. Login\n2. Register\n3. Exit")
        try:
            option = int(input("Choose an option: "))
            if option < 1 or option >3:
                print("The option must be between 1-3 | Try again")
            elif option == 3:
                print("Closing...")
                return None
            else:
                match option:
                    case 1:
                        return userLogin()
                    case 2:
                        return userRegister()
        except ValueError:
            print("The option must be a number | Try again")
# settings section

def displaySettings(user):
    valuesList = list(usersFile["users"][user].keys())
    for i, values in enumerate(valuesList):
        if values == "phrases":
            phrasesList = usersFile["users"][user][values]
            for j, phrases in enumerate(phrasesList):
                print(f"{i+1}.{j+1} - {values}: {phrases}")
        else:
            print(f"{i+1}. {values}: {usersFile["users"][user][values]}")  
    return None

def changeEmail(user):
    while True:
        print(f"1. Change email\n2. Go back")
        try:
            option = int(input("Choose an option: "))
            if option < 1 or option > 2:
                print("The option must be between 1-2 | Try again")
            elif option == 2:
                return None
            else:
                email = input("Add an email: ").strip()
                if email == usersFile["users"][user]["email"]:
                    print(f"{email} is already your email | Try again")
                else:
                    try:
                        info = validate_email(email)
                        emailNormalized = info.email

                        code = random.randint(1000, 9999)
                        sendEmail(
                            "confirmation code",
                            f"Use this code to validate your email: {code}\nYou have 5 minutes until the code expire",
                            emailNormalized
                        )
                        timeSent = datetime.now()
                        try:
                            confirmCode = int(input("Enter the code: "))
                            timeReceived = datetime.now()
                            if timeReceived - timeSent > timedelta(minutes=5):
                                print("Code expired | Try again")
                            else:
                                if confirmCode != code:
                                    print("The code does not match with the one provided")
                                else:
                                    usersFile["users"][user]["email"] = emailNormalized
                                    saveFile("usersFile", usersFile)
                                    return None
                        except ValueError:
                            print("The code must be a number | Try again")

                    except EmailNotValidError as e:
                        print("Invalid email:", str(e))
        except ValueError:
            print("The option must be a number | Try again")

def changePassword(user):
    while True:
        print(f"1. Change password\n2. Go back")
        try:
            option = int(input("Choose an option: "))
            if option < 1 or option > 2:
                print("The option must be between 1-2 | Try again")
            elif option == 2:
                return None
            else:
                checkPassword = pwinput.pwinput(prompt="Insert your password: ", mask="*")
                hashPassword = hashlib.sha256(checkPassword.encode()).hexdigest()
                if hashPassword == usersFile["users"][user]["password"]:
                    newPassword = pwinput.pwinput(prompt="Insert your new password: ", mask="*")
                    hashedNewPassword = hashlib.sha256(newPassword.encode()).hexdigest()
                    if hashedNewPassword!=usersFile["users"][user]["password"]:
                        usersFile["users"][user]["password"] = hashedNewPassword
                        saveFile("usersFile", usersFile)
                        return None
                    else:
                        print("The new password must be different from the old one | Try again")
                else:
                    print("The password does not match | Try again")
        except ValueError:
            print("The option must be a number | Try again")

def addPhrases(user):
    while True:
        print(f"1. Add\n2. Stop")
        try: 
            option = int(input("Choose an option: "))
            if option < 1 or option > 2:
                print("The option must be between 1-2 | Try again")
            elif option == 2:
                return None
            else:
                phrasesList = usersFile["users"][user]["phrases"]
                newPhrase = input("Write the new one: ")
                if newPhrase in phrasesList:
                    print(f"The {newPhrase} is already a phrase | Try again")
                else:
                    phrasesList.append(newPhrase)
                    usersFile["users"][user]["phrases"] = phrasesList
                    saveFile("usersFile", usersFile)
        except ValueError:
            print("The option must be a number | Try again")

def deletePhrases(user):
    while True:
        print(f"1. Delete\n2. Stop")
        try:
            option = int(input("Choose an option: "))
            if option < 1 or option > 2:
                print("The option must be between 1-2 | Try again")
            elif option == 2:
                return None
            else:
                phrasesList = usersFile["users"][user]["phrases"]
                for i, phrase in enumerate(phrasesList):
                    print(f"{i+1}. {phrase}")
                try:
                    optionDelete = int(input("Choose one to delete: "))
                    if optionDelete < 1 or optionDelete > len(phrasesList):
                        print(f"The phrase to delete must be between 1-{len(phrasesList)} | Try again")
                    else:
                        phrasesList.pop(optionDelete-1)
                        usersFile["users"][user]["phrases"] = phrasesList
                        saveFile("usersFile", usersFile)
                except ValueError:
                    print("The option must be a number | Try again")
        except ValueError:
            print("The option must be a number | Try again")

def changePhrases(user):
    while True:
        print(f"1. Add phrases\n2. Delete phrases\n3. Go back")
        try:
            option = int(input("Choose an option: "))
            if option < 1 or option > 3:
                print("The option must be between 1-2 | Try again")
            elif option == 3:
                return None
            else:
                match option:
                    case 1:
                        addPhrases(user)
                    case 2:
                        deletePhrases(user)
        except ValueError:
            print("The option must be a number | Try again")
    return None

def deleteUser(user):
    while True:
        password = pwinput.pwinput(prompt="Enter your password: ", mask="*")
        checkPassword = hashlib.sha256(password.encode("utf-8")).hexdigest()
        if checkPassword == usersFile["users"][user]["password"]:
            break
        else:
            print("The password does not match | Try again")
    while True:
        print(f"1. Confirm\n2. Cancel")
        try:
            option = int(input("Choose an option: "))
            if option < 1 or option > 2:
                print("The option must be between 1-2 | Try again")
            elif option == 1:
                del usersFile["users"][user]
                saveFile("usersFile", usersFile)
                return -1
            else:
                return None
        except ValueError:
            print("The option must be a number | Try again")

        print(f"")

def userSettingsMenu(user):
    while True:
        print(f"{'Welcome to the user settings menu':-^60}\n1. See your settings\n2. Change your email\n3. Change your password\n4. Change your farewell phrases\n5. Delete account\n6. Exit")
        try:
            option = int(input("Choose an option: "))
            if option < 1 or option > 6:
                print("The option must be between 1-6 | Try again")
            elif option == 6:
                print("Back to the menu")
                return None
            else:
                match option:
                    case 1:
                        displaySettings(user)
                    case 2:
                        changeEmail(user)
                    case 3:
                        changePassword(user)
                    case 4:
                        changePhrases(user)
                    case 5:
                        result = deleteUser(user)
                        if result == -1:
                            return -1
        except ValueError:
            print("The option must be a number | Try again")

# display users section

def displayUsers():
    usersList = list(usersFile["users"].keys())
    if not usersList:
        print("No users registered yet.")
        return

    for i, user in enumerate(usersList, start=1):
        print(f"{i}. username: {user}")

# placeholder section

def placeholder():
    print("Wait for the next update")
    return

# menu section

def farewell(user):
    phrasesList = usersFile["users"][user]["phrases"]
    if not phrasesList:
        print("Loggin out...")
        return None
    else:
        print(random.choice(phrasesList))
        return None
    

def showMenu(user):
    while True:
        print(f"{f'Welcome {user} to the main menu':-^60}\n1. placeholder1\n2. placeholder2\n3. placeholder3\n4. Display users4\n5. User settings\n6. Exit")
        try:
            option = int(input("Choose an option: "))
            if option < 1 or option > 6:
                print("The option must be between 1-6 | Try again")
            elif option == 6:
                farewell(user)
                return None
            else:
                match option:
                    case 1:
                        placeholder()
                    case 2:
                        placeholder()
                    case 3:
                        placeholder()
                    case 4:
                        displayUsers()
                    case 5:
                        result = userSettingsMenu(user)
                        if result == -1:
                            return None
                            
        except ValueError:
            print("The option must be a number | Try again")

# m.p
usersFile = initializeFiles("usersFile")
while True:
    activeUser = userSelectorMenu()

    if activeUser is None:
        break

    if activeUser == -1:
        continue

    showMenu(activeUser)
