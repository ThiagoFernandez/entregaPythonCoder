import hashlib
from datetime import datetime, timedelta
from typing import List, Optional


class User:
    """User entity with authentication and settings."""

    def __init__(
        self,
        username: str,
        password: str,
        email: str,
        dni: str,
        ban: bool = False,
        banUntil: Optional[str] = None,
        phrases: Optional[List[str]] = None
    ) -> None:
        self.username: str = username
        self.password: str = password          # hashed
        self.email: str = email
        self.dni: str = dni                    # encrypted
        self.ban: bool = ban
        self.banUntil: Optional[str] = banUntil
        self.phrases: List[str] = phrases or []

    def __str__(self) -> str:
        """String representation."""
        return f"User: {self.username} | Email: {self.email}"

    def check_password(self, plain_password: str) -> bool:
        """Check if password matches."""
        return hashlib.sha256(plain_password.encode()).hexdigest() == self.password

    def change_password(self, new_password: str) -> None:
        """Update password."""
        self.password = hashlib.sha256(new_password.encode()).hexdigest()

    def change_email(self, new_email: str) -> None:
        """Update email."""
        self.email = new_email

    def ban_user(self, minutes: int = 5) -> None:
        """Ban user for given minutes."""
        self.ban = True
        self.banUntil = (datetime.now() + timedelta(minutes=minutes)).isoformat()

    def unban(self) -> None:
        """Remove ban."""
        self.ban = False
        self.banUntil = None

    def unban_if_expired(self) -> None:
        """Auto-unban if time expired."""
        if self.ban and self.banUntil:
            if datetime.now() > datetime.fromisoformat(self.banUntil):
                self.unban()

    def is_banned(self) -> bool:
        """Return ban status."""
        return self.ban

    def add_phrase(self, phrase: str) -> None:
        """Add farewell phrase."""
        if phrase not in self.phrases:
            self.phrases.append(phrase)

    def remove_phrase(self, phrase: str) -> None:
        """Remove farewell phrase."""
        if phrase in self.phrases:
            self.phrases.remove(phrase)

    def show_settings(self, decrypt_dni: str) -> None:
        """Print user settings."""
        for attr, value in vars(self).items():
            if attr == "dni":
                print(f"{attr}: {decrypt_dni}")
            else:
                print(f"{attr}: {value}")
