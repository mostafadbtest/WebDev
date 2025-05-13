from flask import request, session
import mysql.connector
import re
import uuid
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from werkzeug.utils import secure_filename
from icecream import ic

ic.configureOutput(prefix=f'***** | ', includeContext=True)

##################################################
def db():
    db = mysql.connector.connect(
        host="mysql",
        user="root",
        password="password",
        database="company_b"
    )
    cursor = db.cursor(dictionary=True)
    return db, cursor

##################################################
def validate_user_logged():
    if not session.get("user"):
        raise Exception("CPH Sightseer user not logged")
    return session.get("user")

#############################################
def send_email(user_name, user_last_name, verification_key, receiver_email): 
    try:
        sender_email = "mostafadbtest@gmail.com"
        password = "jera jylu nydi wjyt"
        verification_link = f"http://127.0.0.1:80/verify/{verification_key}"

        message = MIMEMultipart()
        message["From"] = "CPH Sightseer project"
        message["To"] = receiver_email
        message["Subject"] = "Welcome - Please Verify Your Account"

        body = f"""
        <h2>Hello {user_name} {user_last_name},</h2>
        <p>Thank you for signing up! To verify your account, please click the link below:</p>
        <p><a href="{verification_link}">Verify Your Account</a></p>
        <p>If you did not sign up, you can ignore this email.</p>
        """

        message.attach(MIMEText(body, "html"))

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())

        ic("Email sent successfully!")
        return "email sent"

    except Exception as ex:
        ic(ex)
        raise Exception("cannot send email")

############################ ##################
def send_reset_email(user_name, user_last_name, reset_key, receiver_email): 
    try:
        sender_email = "mostafadbtest@gmail.com"
        password = "jera jylu nydi wjyt"
        reset_link = f"http://127.0.0.1:80/reset-password/{reset_key}"

        message = MIMEMultipart()
        message["From"] = "CPH Sightseer project"
        message["To"] = receiver_email
        message["Subject"] = "Reset Your Password"

        body = f"""
        <h2>Hello {user_name} {user_last_name},</h2>
        <p>To reset your password, click the link below:</p>
        <p><a href="{reset_link}">Reset Password</a></p>
        <p>If you did not request this, please ignore this email.</p>
        """

        message.attach(MIMEText(body, "html"))

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())

        return "email sent"
    except Exception as ex:
        ic(ex)
        raise Exception("cannot send reset email")

############################################
def send_delete_email(user_name, user_last_name, delete_key, receiver_email):
    try:
        sender_email = "mostafadbtest@gmail.com"
        password = "jera jylu nydi wjyt"
        delete_link = f"http://127.0.0.1:80/confirm-delete/{delete_key}"

        message = MIMEMultipart()
        message["From"] = "CPH Sightseer project"
        message["To"] = receiver_email
        message["Subject"] = "Confirm Your Profile Deletion"

        body = f"""
        <h2>Hello {user_name} {user_last_name},</h2>
        <p>You have requested to delete your profile. To confirm this action, please click the link below:</p>
        <p><a href="{delete_link}">Confirm Profile Deletion</a></p>
        <p>If you did not request this change, please ignore this email.</p>
        """
        message.attach(MIMEText(body, "html"))

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())

        return "email sent"
    except Exception as ex:
        ic(ex)
        raise Exception("cannot send deletion email")

##################################################
USER_NEW_PASSWORD_MIN = 4
USER_NEW_PASSWORD_MAX = 20
def validate_new_password():
    error = f"Password must be {USER_NEW_PASSWORD_MIN} to {USER_NEW_PASSWORD_MAX} characters"
    new_password = request.form.get("new_password", "").strip()
    if len(new_password) < USER_NEW_PASSWORD_MIN or len(new_password) > USER_NEW_PASSWORD_MAX:
        raise Exception(error)
    return new_password

##################################################
USER_NAME_MIN = 3
USER_NAME_MAX = 20
USER_NAME_REGEX = f"^.{{{USER_NAME_MIN},{USER_NAME_MAX}}}$"
def validate_user_name():
    error = f"first name {USER_NAME_MIN} to {USER_NAME_MAX} characters"
    user_name = request.form.get("user_name", "").strip()
    if not re.match(USER_NAME_REGEX, user_name):
        raise Exception(error)
    return user_name

##################################################
USER_LAST_NAME_MIN = 3
USER_LAST_NAME_MAX = 20
USER_LAST_NAME_REGEX = f"^.{{{USER_LAST_NAME_MIN},{USER_LAST_NAME_MAX}}}$"
def validate_user_last_name():
    error = f"last name {USER_LAST_NAME_MIN} to {USER_LAST_NAME_MAX} characters"
    user_last_name = request.form.get("user_last_name", "").strip()
    if not re.match(USER_LAST_NAME_REGEX, user_last_name):
        raise Exception(error)
    return user_last_name

##################################################
USER_USER_USERNAME_MIN = 3
USER_USER_USERNAME_MAX = 20
USER_USER_USERNAME_REGEX = f"^.{{{USER_USER_USERNAME_MIN},{USER_USER_USERNAME_MAX}}}$"
def validate_user_username():
    error = f"user username {USER_USER_USERNAME_MIN} to {USER_USER_USERNAME_MAX} characters"
    user_username = request.form.get("user_username", "").strip()
    if not re.match(USER_USER_USERNAME_REGEX, user_username):
        raise Exception(error)
    return user_username

##################################################
USER_EMAIL_REGEX = "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
def validate_user_email():
    error = "Invalid email"
    user_email = request.form.get("user_email", "").strip().lower()
    if not re.match(USER_EMAIL_REGEX, user_email):
        raise Exception(error)
    return user_email

##################################################
USER_PASSWORD_MIN = 4
USER_PASSWORD_MAX = 20
def validate_user_password():
    error = f"password {USER_PASSWORD_MIN} to {USER_PASSWORD_MAX} characters"
    user_password = request.form.get("user_password", "").strip()
    if len(user_password) < USER_PASSWORD_MIN or len(user_password) > USER_PASSWORD_MAX:
        raise Exception(error)
    return user_password

##################################################
# Pagination
REGEX_PAGE_NUMBER = "^[1-9][0-9]*$"
def validate_page_number(page_number):
    error = "CPH Sightseer page number"
    page_number = page_number.strip()
    if not re.match(REGEX_PAGE_NUMBER, page_number):
        raise Exception(error)
    return int(page_number)

##################################################
ITEM_NAME_MIN = 3
ITEM_NAME_MAX = 50
ITEM_NAME_REGEX = f"^.{{{ITEM_NAME_MIN},{ITEM_NAME_MAX}}}$"

def validate_item_name():
    """
    Validates that the item name is between 3 and 50 characters.
    """
    error = f"item name must be {ITEM_NAME_MIN} to {ITEM_NAME_MAX} characters"
    item_name = request.form.get("item_name", "").strip()
    if not re.match(ITEM_NAME_REGEX, item_name):
        raise Exception(error)
    return item_name

def validate_item_price():
    """
    Validates that the price is a number between 0 and 500 (inclusive of 0).
    """
    item_price = request.form.get("item_price", "").strip()
    try:
        price = float(item_price)
        if price < 0 or price > 500:
            raise Exception("price must be between 0 and 500")
        return price
    except ValueError:
        raise Exception("price must be a valid number")

def validate_coordinates():
    """
    Validates that longitude is between -180 and 180,
    and latitude is between -90 and 90.
    """
    lon_error = "longitude must be between -180 and 180"
    lat_error = "latitude must be between -90 and 90"
    item_lon = request.form.get("item_lon", "").strip()
    item_lat = request.form.get("item_lat", "").strip()

    try:
        lon = float(item_lon)
        if not -180 <= lon <= 180:
            raise Exception(lon_error)
    except ValueError:
        raise Exception(lon_error)

    try:
        lat = float(item_lat)
        if not -90 <= lat <= 90:
            raise Exception(lat_error)
    except ValueError:
        raise Exception(lat_error)

    return lon, lat

##################################################
def validate_selected_image():
    error = "CPH Sightseer Please select an image"
    selected_image_pk = request.form.get("selected_image_pk", "").strip()
    if not selected_image_pk:
        raise Exception(error)
    return selected_image_pk

##################################################
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
MAX_FILE_SIZE      = 2 * 1024 * 1024    # 1 MB
MAX_FILES          = 6                  

def validate_item_images():
    user = validate_user_logged()

    files = request.files.getlist("files")
    if not files or len(files) < 2:
        raise Exception("Please select at least 2 images to upload")
    if len(files) > MAX_FILES:
        raise Exception(f"You can upload at most {MAX_FILES} files at once")

    db_conn, cursor = db()
    try:
        cursor.execute(
            "SELECT COUNT(*) AS cnt FROM images WHERE user_fk=%s AND item_fk IS NULL",
            (user["user_pk"],)
        )
        existing = cursor.fetchone().get("cnt", 0)
    finally:
        cursor.close()
        db_conn.close()

    remaining = MAX_FILES - existing
    if remaining <= 0:
        raise Exception(f"You already have the maximum of {MAX_FILES} images")
    if len(files) > remaining:
        raise Exception(f"You may only upload {remaining} more image(s)")

    upload_dir = os.path.join("static", "uploads")
    os.makedirs(upload_dir, exist_ok=True)

    saved_filenames = []
    for f in files:
        fname = secure_filename(f.filename or "")
        if "." not in fname:
            raise Exception("Invalid file name")
        ext = fname.rsplit(".", 1)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise Exception("File extension not allowed")

        f.stream.seek(0, os.SEEK_END)
        size = f.stream.tell()
        f.stream.seek(0)
        if size > MAX_FILE_SIZE:
            raise Exception("File too large")

        new_name = f"{uuid.uuid4().hex}.{ext}"
        f.save(os.path.join(upload_dir, new_name))
        saved_filenames.append(new_name)

    return saved_filenames

##################################################
ITEM_DESCRIPTION_MAX = 250
def validate_item_description():
    error = "CPH Sightseer Description must be 10 to 200 characters"
    desc = request.form.get("item_description", "").strip()
    if not 10 <= len(desc) <= 200:
        raise Exception(error)
    return desc

##################################################
def validate_item_contact_url():
    error = "CPH Sightseer Invalid URL format"
    url = request.form.get("item_contact_url", "").strip()
    if not re.match(r"^(http|https)://", url):
        raise Exception(error)
    return url


##################################################
def send_block_notification_email(user_name, user_last_name, receiver_email, is_blocked):
    try:
        sender_email = "mostafadbtest@gmail.com"
        password = "jera jylu nydi wjyt"
        
        message = MIMEMultipart()
        message["From"] = "CPH Sightseer project"
        message["To"] = receiver_email
        
        if is_blocked:
            message["Subject"] = "Your Account Has Been Blocked"
            body = f"""
            <h2>Hello {user_name} {user_last_name},</h2>
            <p>We inform you that your account has been blocked by an administrator.</p>
            """
        else:
            message["Subject"] = "Your Account Has Been Unblocked"
            body = f"""
            <h2>Hello {user_name} {user_last_name},</h2>
            <p>Good news! Your account has been unblocked and you can now access to add items again.</p>
            """

        message.attach(MIMEText(body, "html"))

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())

        return "email sent"
    except Exception as ex:
        ic(ex)
        raise Exception("cannot send block notification email")
    

##################################################
def send_item_block_notification_email(user_name, user_last_name, receiver_email, item_name, is_blocked):
    try:
        sender_email = "mostafadbtest@gmail.com"
        password = "jera jylu nydi wjyt"
        
        message = MIMEMultipart()
        message["From"] = "CPH Sightseer project"
        message["To"] = receiver_email
        
        if is_blocked:
            message["Subject"] = "Your Item Has Been Blocked"
            body = f"""
            <h2>Hello {user_name} {user_last_name},</h2>
            <p>We inform you that your item "{item_name}" has been blocked by an administrator.</p>
            """
        else:
            message["Subject"] = "Your Item Has Been Unblocked"
            body = f"""
            <h2>Hello {user_name} {user_last_name},</h2>
            <p>Good news! Your item "{item_name}" has been unblocked by an administrator.</p>
            <p>You can now view and manage your item again.</p>
            """

        message.attach(MIMEText(body, "html"))

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())

        ic(f"Item {'block' if is_blocked else 'unblock'} notification email sent successfully!")
        return "email sent"
    except Exception as ex:
        ic(ex)
        raise Exception(f"cannot send item {'block' if is_blocked else 'unblock'} notification email")