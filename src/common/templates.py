

def get_otp_template(user_email, otp):
    return f"""
        <div style="font-family: Arial, sans-serif; font-size: 16px; color: #333; line-height: 1.5;">
            <p>Hello {user_email},</p>
            <p>Here is your One Time Password (OTP): <strong>{otp}</strong></p>
            <p>Use this OTP to log in to your account.</p>
            <p>Please do not share this OTP with anyone.</p>
        </div>
        """