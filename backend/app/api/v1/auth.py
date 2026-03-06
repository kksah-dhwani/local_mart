import random
import string
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.core.security import hash_password, verify_password, create_access_token
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.schemas import (
    RegisterRequest, LoginRequest, TokenResponse,
    UserOut, ProfileUpdateRequest, ChangePasswordRequest,
    ForgotPasswordRequest, ResetPasswordRequest,
)
from app.services.email_service import send_email

router = APIRouter(prefix="/auth", tags=["Auth"])


def generate_otp() -> str:
    return "".join(random.choices(string.digits, k=6))


def send_otp_email(to_email: str, user_name: str, otp: str):
    html = f"""
    <!DOCTYPE html>
    <html>
    <body style="margin:0;padding:0;background:#f8fafc;font-family:Arial,sans-serif;">
      <div style="max-width:480px;margin:30px auto;background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.08);">
        <div style="background:#2563eb;padding:24px 28px;">
          <h1 style="margin:0;color:#fff;font-size:20px;">🔐 Password Reset</h1>
          <p style="margin:6px 0 0;color:#bfdbfe;font-size:14px;">Local Mart</p>
        </div>
        <div style="padding:28px;text-align:center;">
          <p style="color:#475569;font-size:15px;">Hi <strong>{user_name}</strong>,</p>
          <p style="color:#475569;font-size:14px;">Your OTP for password reset is:</p>
          <div style="background:#eff6ff;border:2px dashed #93c5fd;border-radius:12px;padding:20px;margin:20px 0;">
            <p style="margin:0;font-size:36px;font-weight:900;letter-spacing:10px;color:#1d4ed8;">{otp}</p>
          </div>
          <p style="color:#94a3b8;font-size:13px;">This OTP is valid for <strong>10 minutes</strong>.</p>
          <p style="color:#ef4444;font-size:12px;margin-top:8px;">If you did not request this, please ignore this email.</p>
        </div>
        <div style="padding:14px;background:#f8fafc;text-align:center;">
          <p style="margin:0;font-size:12px;color:#94a3b8;">Local Mart — Your Neighbourhood Store 🛒</p>
        </div>
      </div>
    </body>
    </html>
    """
    send_email(to=to_email, subject="🔐 Password Reset OTP — Local Mart", html_body=html)


# ── Register ─────────────────────────────────────────────
@router.post("/register", status_code=201)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(400, "Email already registered")
    if db.query(User).filter(User.phone == data.phone).first():
        raise HTTPException(400, "Phone already registered")
    user = User(
        name=data.name,
        email=data.email,
        phone=data.phone,
        password_hash=hash_password(data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "Registration successful", "user_id": user.id}


# ── Login ─────────────────────────────────────────────────
@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email, User.is_active == True).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": str(user.id), "role": user.role})
    return {"access_token": token, "token_type": "bearer"}


# ── Me ────────────────────────────────────────────────────
@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user


# ── Update Profile ────────────────────────────────────────
@router.put("/profile")
def update_profile(
    data: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if data.name:
        current_user.name = data.name
    if data.phone:
        existing = db.query(User).filter(User.phone == data.phone, User.id != current_user.id).first()
        if existing:
            raise HTTPException(400, "Phone already in use")
        current_user.phone = data.phone
    db.commit()
    db.refresh(current_user)
    return {"message": "Profile updated"}


# ── Change Password (logged in) ───────────────────────────
@router.put("/change-password")
def change_password(
    data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not verify_password(data.old_password, current_user.password_hash):
        raise HTTPException(400, "Old password incorrect")
    current_user.password_hash = hash_password(data.new_password)
    db.commit()
    return {"message": "Password changed successfully"}


# ── Forgot Password — OTP bhejo ───────────────────────────
@router.post("/forgot-password")
def forgot_password(
    data: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == data.email, User.is_active == True).first()

    # Security: email exist kare ya na kare, same response do
    # (taaki attacker ko pata na chale koi email registered hai ya nahi)
    if user:
        otp = generate_otp()
        user.reset_otp = otp
        user.reset_otp_expiry = datetime.utcnow() + timedelta(minutes=10)
        db.commit()
        background_tasks.add_task(send_otp_email, user.email, user.name, otp)

    return {"message": "If this email is registered, an OTP has been sent."}


# ── Reset Password — OTP verify + new password ────────────
@router.post("/reset-password")
def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email, User.is_active == True).first()

    if not user or not user.reset_otp or not user.reset_otp_expiry:
        raise HTTPException(400, "Invalid or expired OTP. Please request a new one.")

    if datetime.utcnow() > user.reset_otp_expiry:
        user.reset_otp = None
        user.reset_otp_expiry = None
        db.commit()
        raise HTTPException(400, "OTP has expired. Please request a new one.")

    if user.reset_otp != data.otp:
        raise HTTPException(400, "Incorrect OTP. Please try again.")

    # OTP sahi — password reset karo
    user.password_hash = hash_password(data.new_password)
    user.reset_otp = None
    user.reset_otp_expiry = None
    db.commit()

    return {"message": "Password reset successful. You can now login."}
