from typing import Dict, Optional, List
from users import User


class UserManager:
    """Handles user persistence and authentication."""

    def __init__(self, users_data: Dict[str, dict]) -> None:
        self.users_data: Dict[str, dict] = users_data

    # ---------- helpers ----------

    def user_exists(self, username: str) -> bool:
        """Check if user exists."""
        return username in self.users_data

    def get_user(self, username: str) -> User:
        """Build User object from stored data."""
        data: dict = self.users_data[username]
        return User(
            username=username,
            password=data["password"],
            email=data["email"],
            dni=data["dni"],
            ban=data.get("ban", False),
            banUntil=data.get("banUntil"),
            phrases=data.get("phrases", [])
        )

    def save_user(self, user: User) -> None:
        """Save User into storage."""
        self.users_data[user.username] = {
            "password": user.password,
            "email": user.email,
            "dni": user.dni,
            "ban": user.ban,
            "banUntil": user.banUntil,
            "phrases": user.phrases
        }

    def delete_user(self, username: str) -> None:
        """Delete user from storage."""
        if username in self.users_data:
            del self.users_data[username]

    # ---------- core logic ----------

    def create_user(
        self,
        username: str,
        password_hash: str,
        email: str,
        encrypted_dni: str,
        phrases: List[str]
    ) -> User:
        """Create and store a new user."""
        user = User(
            username=username,
            password=password_hash,
            email=email,
            dni=encrypted_dni,
            phrases=phrases
        )
        self.save_user(user)
        return user

    def authenticate(self, username: str, plain_password: str) -> Optional[User]:
        """Authenticate user credentials."""
        if not self.user_exists(username):
            return None

        user: User = self.get_user(username)
        user.unban_if_expired()

        if user.is_banned():
            return None

        if user.check_password(plain_password):
            self.save_user(user)
            return user

        return None

    def ban_user(self, username: str, minutes: int = 5) -> None:
        """Ban(hammer) user for given minutes."""
        user: User = self.get_user(username)
        user.ban_user(minutes)
        self.save_user(user)
