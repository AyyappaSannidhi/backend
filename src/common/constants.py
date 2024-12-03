from dataclasses import dataclass

@dataclass(slots=True)
class Constants():
    INTERNAL_SERVER_ERROR = "Internal Server Error"
    BOT_DETECTED = "Automation bot detected, please stop immediately"
    USERNAME_NOT_AVAILABLE= "User Name not available"
    INVALID_USERNAME_AND_PASSWORD= "Invalid User Name and Password"
    REGISTER_FIRST = "Kindly register first"
    INVALID_TOKEN = "Invalid Token"
    NOT_GOOGLE_VERIFIED_USER = "Not google verified user"
    LOGIN_SUCCESS = "Login Success"
    EMAIL_SENT = "Email sent to the provided email"
    OTP_FAILURE = "OTP service is unavailable"
    OTP_EXPIRED = "OTP is Expired"
    OTP_NOT_SENT_FAILURE = "Failed to send OTP to the provided email"
    MANY_OTP_REQUESTS = "Multiple OTP Request, please try after some time"
    OTP_SUBJECT = "OTP - Sri Ayyapappa Swamy Seva Sannidhi"
    PLEASE_REQUEST_FIRST = "Please Request OTP First"
    OTP_EXPIRED_OR_INVALID = "OTP Expired or Invalid"
    OTP = "otp"
    USER_NOT_FOUND = "User not found"
    USER_PROFILE_UPDATED = "User profile is successfully updated"
