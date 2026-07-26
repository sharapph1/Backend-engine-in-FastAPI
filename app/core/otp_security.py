from pwdlib import PasswordHash


otp_hasher = PasswordHash.recommended()


def hash_otp(otp: str) -> str:
    return otp_hasher.hash(otp)


def verify_otp_hash(otp: str, otp_hash: str) -> bool:
    return otp_hasher.verify(otp, otp_hash)