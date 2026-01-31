from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()


def get_password_hash(password: str) -> str:
    """
    Hashes the provided plain password.
    """
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies if a plain password matches a stored hashed password.
    """
    return password_hash.verify(plain_password, hashed_password)
