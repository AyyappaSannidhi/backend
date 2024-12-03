from enum import Enum

class UserAccountType(Enum):
    INTERNAL : str = "internal"
    GOOGLE : str = "google"
    OTP : str = "otp"

class UserType(Enum):
    DEVOTEE : str = "devotee"
    MEMBER : str = "member"