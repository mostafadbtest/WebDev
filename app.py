from flask import Flask, session, render_template, request, redirect, url_for,jsonify

from werkzeug.datastructures import ImmutableMultiDict
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash

import time
import uuid
import json


import x

import language as languages

from icecream import ic
ic.configureOutput(prefix=f'----- | ', includeContext=True)

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

app.jinja_env.globals['hasattr'] = hasattr


##############################
@app.after_request
def disable_cache(response):
    """
    This function automatically disables caching for all responses.
    It is applied after every request to the server.
    """
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response






########################################
@app.get("/rates")
def get_rates():
    try:
        import requests
        data = requests.get("https://api.exchangerate-api.com/v4/latest/usd")
        ic(data.json())
        with open("rates.txt", "w") as file:
            file.write(data.text)
        return data.json()
    except Exception as ex:
        ic(ex)




def ___USER___():pass

########################################
@app.get("/signup")
@app.get("/signup/<lan>")
def show_signup(lan="en"):
    try:
        languages_allowed = ["en", "dk"]
        if lan not in languages_allowed: lan = "en"
        active_signup ="active"
        error_message = request.args.get("error_message", "")
        return render_template("signup.html", 
                            title="Signup us", 
                            active_signup=active_signup, 
                            error_message=error_message,
                            old_values={},
                            languages=languages,
                            lan=lan)
    except Exception as ex:
        ic(ex)
        return str(ex)
    

@app.post("/signup")
@app.post("/signup/<lan>")
def signup(lan="en"):
    
    is_api = request.is_json or "application/json" in request.headers.get("Accept", "")
    if is_api:
        data = request.get_json(silent=True) or {}
        request.form = ImmutableMultiDict(data)

    try:
        
        user_username      = x.validate_user_username()
        user_name          = x.validate_user_name()
        user_last_name     = x.validate_user_last_name()
        user_email         = x.validate_user_email()
        user_password      = x.validate_user_password()
        user_repeat_password = request.form.get("user_repeat_password", "").strip()
       
        lan = request.form.get("lan", lan)
        if lan not in ["en", "dk"]:
            lan = "en"

        if user_password != user_repeat_password:
            old_values = request.form.to_dict()
            old_values.pop("user_password", None)
            old_values.pop("user_repeat_password", None)

            if is_api:
                return jsonify({ "error": "Passwords do not match." }), 400

            return render_template(
                "signup.html",
                error_message="Passwords do not match.",
                old_values=old_values,
                user_password_error="input_error",
                user_repeat_password_error="input_error",
                active_signup="active",
                title="Signup us",
                languages=languages,
                lan=lan
            )

        hashed_password = generate_password_hash(user_password)
        user_created_at = int(time.time())
        verification_key = str(uuid.uuid4())
        user_verified_at = 0

        q = """INSERT INTO users 
        (user_pk, user_username, user_name, user_last_name, user_email, 
         user_password, user_created_at, user_updated_at, user_deleted_at,
         user_verification_key, user_verified_at) 
        VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

        db, cursor = x.db()
        cursor.execute(q, (
            user_username,
            user_name,
            user_last_name,
            user_email,
            hashed_password,
            user_created_at,
            0,
            0,
            verification_key,
            user_verified_at
        ))
        if cursor.rowcount != 1:
            raise Exception("System under maintenance")
        db.commit()

        x.send_email(user_name, user_last_name, verification_key, user_email)

        if is_api:
            return jsonify({
                "message": "Signup ok. Check your email to verify your account."
            }), 201

        return redirect(url_for(
            "show_login",
            message="Signup ok. Check your email to verify your account."
        ))

    except Exception as ex:
        ic("Signup error:", ex)
        if "db" in locals():
            db.rollback()

        if is_api:
            return jsonify({ "error": str(ex) }), 400

        old_values = request.form.to_dict()
        lan = request.form.get("lan", "en")
        if lan not in ["en", "dk"]:
            lan = "en"

        if "user_username" in str(ex):
            return render_template(
                "signup.html",
                error_message="Username is already taken",
                old_values=old_values,
                user_username_error="input_error",
                active_signup="active",
                title="Signup us",
                languages=languages,
                lan=lan
            )
        if "username" in str(ex):
            old_values.pop("user_username", None)
            return render_template(
                "signup.html",
                error_message="Please enter a username (3-20 characters)",
                old_values=old_values,
                user_username_error="input_error",
                languages=languages,
                lan=lan
            )
        if "first name" in str(ex):
            old_values.pop("user_name", None)
            return render_template(
                "signup.html",
                error_message="Please enter your first name (3-20 characters)",
                old_values=old_values,
                user_name_error="input_error",
                languages=languages,
                lan=lan
            )
        if "last name" in str(ex):
            old_values.pop("user_last_name", None)
            return render_template(
                "signup.html",
                error_message="Please enter your last name (3-20 characters)",
                old_values=old_values,
                user_last_name_error="input_error",
                languages=languages,
                lan=lan
            )
        if "Invalid email" in str(ex):
            old_values.pop("user_email", None)
            return render_template(
                "signup.html",
                error_message="Please enter a valid email address",
                old_values=old_values,
                user_email_error="input_error",
                languages=languages,
                lan=lan
            )
        if "password" in str(ex):
            old_values.pop("user_password", None)
            return render_template(
                "signup.html",
                error_message="Please enter a password (4-20 characters)",
                old_values=old_values,
                user_password_error="input_error",
                languages=languages,
                lan=lan
            )
        if "user_email" in str(ex):
            return redirect(url_for(
                "show_signup",
                error_message="Email already exists",
                old_values=old_values,
                email_error=True,
                lan=lan
            ))
        if "user_username" in str(ex):
            return redirect(url_for(
                "show_signup",
                error_message="Username already exists",
                old_values=request.form,
                user_username_error=True,
                lan=lan
            ))
        return redirect(url_for("show_signup", error_message=ex.args[0], lan=lan))

    finally:
        if "cursor" in locals():
            cursor.close()
        if "db" in locals():
            db.close()




############ send email ##################
@app.get("/send-email")
def send_email():
    try:
        x.send_email()
        return "Email sent"
    except Exception as ex:
        ic(ex)
        return "error"
    
    
########################################### 
@app.get("/login")
@app.get("/login/<lan>")
def show_login(lan="en"):
    try:
        languages_allowed = ["en", "dk"]
        if lan not in languages_allowed: lan = "en"
        message = request.args.get("message", "")
        return render_template("login.html",
            message=message,
            old_values={},          
            user_email_error="",
            user_password_error="",
            active_login="active",
            languages=languages,
            lan=lan
        )
    except Exception as ex:
        ic(ex)
        return str(ex)




########################################
@app.post("/login")
@app.post("/login/<lan>")
def login(lan="en"):
    is_api = request.is_json or "application/json" in request.headers.get("Accept", "")
    if is_api:
        request.form = ImmutableMultiDict(request.get_json(silent=True) or {})

    try:
        languages_allowed = ["en", "dk"]
        if lan not in languages_allowed: lan = "en"
        
        user_email    = x.validate_user_email()
        user_password = x.validate_user_password()

        db, cursor = x.db()
        q = "SELECT * FROM users WHERE user_email = %s"
        cursor.execute(q, (user_email,))
        user = cursor.fetchone()

        if not user:
            raise Exception("User not found in database")

        # ← BLOCKED‐USER CHECK
        if user["user_blocked_at"] and user["user_blocked_at"] != 0:
            if is_api:
                return jsonify({ "error": "Your account has been blocked." }), 403
            return render_template(
                "login.html",
                message="Your account has been blocked by an administrator.",
                old_values={"user_email": user_email},
                languages=languages,
                lan=lan
            )
        
        if user["user_deleted_at"] != 0:
            raise Exception("Your account has been deleted. Create a new account.")

        if user["user_verified_at"] == 0:
            raise Exception("User is not verified yet. Please check your email.")

        if not check_password_hash(user["user_password"], user_password):
            raise Exception("Invalid Password")

        user.pop("user_password")
        session["user"] = user

        if user.get("role_fk") == 1:
            if is_api:
                return jsonify({ "message": "Login successful", "role": "admin" }), 200
            return redirect(url_for("admin_dashboard"))
        else:
            if is_api:
                return jsonify({ "message": "Login successful", "role": "user" }), 200
            return redirect(url_for("profile"))

    except Exception as ex:
        ic("Login error:", ex)
        if "db" in locals():
            db.rollback()

        
        if is_api:
            return jsonify({ "error": str(ex) }), 400


        old_values = request.form.to_dict()

        if "Invalid email" in str(ex):
            old_values.pop("user_email", None)
            return render_template(
                "login.html",
                message="Invalid email",
                old_values=old_values,
                user_email_error="input_error",
                languages=languages,
                lan=lan
            )
        if "password" in str(ex):
            old_values.pop("user_password", None)
            return render_template(
                "login.html",
                message="Invalid password",
                old_values=old_values,
                user_password_error="input_error",
                languages=languages,
                lan=lan
            )
        if "User not found" in str(ex):
            return render_template(
                "login.html",
                message="User not found in database",
                old_values=old_values,
                languages=languages,
                lan=lan
            )
        if "verified" in str(ex):
            return render_template(
                "login.html",
                message="User is not verified yet. Please check your email.",
                old_values=old_values,
                languages=languages,
                lan=lan
            )
        if "deleted" in str(ex):
            return render_template(
                "login.html",
                message=str(ex),
                old_values=old_values,
                languages=languages,
                lan=lan
            )
        if "Invalid credentials" in str(ex):
            return render_template(
                "login.html",
                message="Invalid credentials",
                old_values=old_values,
                languages=languages,
                lan=lan
            )

        return render_template(
            "login.html", 
            message=str(ex), 
            old_values=old_values, 
            languages=languages,
            lan=lan
        ), 400

    finally:
        if "cursor" in locals():
            cursor.close()
        if "db" in locals():
            db.close()




########################################
@app.get("/forgot-password")
@app.get("/forgot-password/<lan>")
def show_forgot_password(lan="en"):
    try:
        languages_allowed = ["en", "dk"]
        if lan not in languages_allowed: lan = "en"
        return render_template("forgot_password.html", 
                              message=request.args.get("message", ""),
                              languages=languages,
                              lan=lan)
    except Exception as ex:
        ic(ex)
        return str(ex)



########################################
@app.post("/forgot-password")
@app.post("/forgot-password/<lan>")
def forgot_password(lan="en"):
    is_api = request.is_json or "application/json" in request.headers.get("Accept", "")
    if is_api:
        request.form = ImmutableMultiDict(request.get_json(silent=True) or {})

    try:
        user_email = x.validate_user_email()
        
        lan = request.form.get("lan", lan)
        if lan not in ["en", "dk"]:
            lan = "en"

        db, cursor = x.db()
        q = "SELECT * FROM users WHERE user_email = %s"
        cursor.execute(q, (user_email,))
        user = cursor.fetchone()
        if not user:
            raise Exception("Email not found")

        reset_key = uuid.uuid4().hex
        q = "UPDATE users SET user_reset_key = %s WHERE user_email = %s"
        cursor.execute(q, (reset_key, user_email))
        db.commit()

        x.send_reset_email(user["user_name"], user["user_last_name"], reset_key, user_email)

        if is_api:
            return jsonify({
                "message": "Email sent with reset instructions.",
                "reset_key": reset_key
            }), 200

        return redirect(url_for("show_forgot_password",
                                message="Email sent with reset instructions.",
                                lan=lan))

    except Exception as ex:
        if is_api:
            return jsonify({ "error": str(ex) }), 400

        return redirect(url_for("show_forgot_password",
                                message=str(ex),
                                lan=lan))
    finally:
        if "cursor" in locals():
            cursor.close()
        if "db" in locals():
            db.close()



######################################################
@app.get("/reset-password/<reset_key>")
def show_reset_password(reset_key):
    is_api = "application/json" in request.headers.get("Accept", "")
    lan = session.get("lang", "en")  
    if lan not in ["en", "dk"]:
        lan = "en"
    session["lang"] = lan
    
    try:
        db, cursor = x.db()
        cursor.execute("SELECT * FROM users WHERE user_reset_key = %s", (reset_key,))
        user = cursor.fetchone()

        if not user:
            if is_api:
                return jsonify({ "error": "Invalid or expired reset link" }), 404
            return "Invalid or expired reset link", 404

        if is_api:
            return jsonify({
                "valid": True,
                "reset_key": reset_key,
                "user_email": user["user_email"]
            }), 200

        
        return render_template("reset-password.html", reset_key=reset_key, message="", lan=lan, languages=languages)

    except Exception as ex:
        if is_api:
            return jsonify({ "error": str(ex) }), 500
        return str(ex), 500

    finally:
        if "cursor" in locals():
            cursor.close()
        if "db" in locals():
            db.close()





#####################################################
@app.post("/reset-password/<reset_key>")
def reset_password(reset_key):
    lan = session.get("lang", "en")
    if lan not in ["en", "dk"]:
        lan = "en"
    
    try:
        new_password = x.validate_new_password()

        hashed_password = generate_password_hash(new_password)
        db, cursor = x.db()
        q = "UPDATE users SET user_password = %s, user_reset_key = NULL WHERE user_reset_key = %s"
        cursor.execute(q, (hashed_password, reset_key))
        db.commit()

        if cursor.rowcount != 1:
            raise Exception("Reset failed or link already used")

        return redirect(url_for("show_login", message="Password updated. You can log in now.", lan=lan))

    except Exception as ex:
        return render_template("reset-password.html", 
                               reset_key=reset_key, 
                               message=str(ex), 
                               status="error",
                               lan=lan,
                               languages=languages) 

    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()




###############################################################
@app.get("/delete-profile/<lan>")
def show_delete_profile(lan="en"):
    try:
        lan = request.args.get("lan", lan)
        if lan not in ("en", "dk"):
            lan = "en"
        session["lang"] = lan

        if not session.get("user"):
            return redirect(url_for("show_login", lan=lan))

        message = request.args.get("message", "")

        return render_template(
            "delete_profile.html",
            message=message,
            is_session=True,
            languages=languages,
            lan=lan
        )

    except Exception as ex:
        ic("Unexpected error in show_delete_profile:", ex)
        return "An unexpected server error occurred", 500




################### ############################################
@app.post("/delete-profile/<lan>")
def delete_profile(lan):
    is_api = request.is_json or "application/json" in request.headers.get("Accept", "")
    if is_api:
        request.form = ImmutableMultiDict(request.get_json(silent=True) or {})

    try:
        if not session.get("user"):
            if is_api:
                return jsonify({ "error": "Not authenticated" }), 401
            return redirect(url_for("show_login", lan=lan))

        user = session["user"]
        current_password = request.form.get("current_password", "").strip()

        # Get the complete user data from the database.
        db, cursor = x.db()
        q = "SELECT * FROM users WHERE user_pk = %s"
        cursor.execute(q, (user["user_pk"],))
        db_user = cursor.fetchone()
        if not db_user:
            raise Exception("User not found.")

        if not check_password_hash(db_user["user_password"], current_password):
            raise Exception("Incorrect password.")

        delete_key = uuid.uuid4().hex
        q = "UPDATE users SET user_delete_key = %s WHERE user_pk = %s"
        cursor.execute(q, (delete_key, user["user_pk"]))
        db.commit()

        x.send_delete_email(
            db_user["user_name"],
            db_user["user_last_name"],
            delete_key,
            db_user["user_email"]
        )

        if is_api:
            return jsonify({
                "message": "Confirmation email sent. Check your inbox.",
                "delete_key": delete_key
            }), 200

        return redirect(url_for(
            "show_delete_profile",
            message="A confirmation email has been sent. Please check your email to confirm deletion.",
            lan=lan
        ))

    except Exception as ex:
        if "db" in locals():
            db.rollback()

        if is_api:
            return jsonify({ "error": str(ex) }), 400

        return redirect(url_for(
            "show_delete_profile",
            message=str(ex),
            lan=lan
        ))
    finally:
        if "cursor" in locals():
            cursor.close()
        if "db" in locals():
            db.close()





################### ############################################
@app.get("/confirm-delete/<delete_key>")
def confirm_delete(delete_key):
    try:
        db, cursor = x.db()
        q = "SELECT * FROM users WHERE user_delete_key = %s"
        cursor.execute(q, (delete_key,))
        user = cursor.fetchone()
        if not user:
            return "Invalid or expired deletion link."

        q = "UPDATE users SET user_deleted_at = %s, user_delete_key = NULL WHERE user_pk = %s"
        timestamp = int(time.time())  
        cursor.execute(q, (timestamp, user["user_pk"]))
        db.commit()

        
        if session.get("user") and session["user"]["user_pk"] == user["user_pk"]:
            session.pop("user")
        
        return "Your account has been deleted. You can no longer log in."
    except Exception as ex:
        return str(ex), 500
    finally:
        if "cursor" in locals():
            cursor.close()
        if "db" in locals():
            db.close()



###############################################################
@app.get("/verify/<verification_key>")
def verify_user(verification_key):
    try:
        db, cursor = x.db()
        q = """
        UPDATE users
        SET user_verified_at = %s
        WHERE user_verification_key = %s
        AND user_verified_at = 0
        """
        cursor.execute(q, (int(time.time()), verification_key))
        db.commit()

        if cursor.rowcount == 1:
            return "Your account has been verified! You can now <a href='/login'>login</a>."
        else:
            return "Invalid or expired verification link."
    except Exception as ex:
        ic(ex)
        return "System under maintenance", 500
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()



def ___Item_Page___():pass

#############################################
@app.get("/")
@app.get("/<lan>")
def view_index(lan="en"):
    try:
        languages_allowed = ["en", "dk"]
        if lan not in languages_allowed: lan = "en"
        
        db, cursor = x.db()
        q = "SELECT * FROM items WHERE item_blocked_at = 0 ORDER BY item_created_at LIMIT 2"
        cursor.execute(q)
        items = cursor.fetchall()
        rates = ""
        with open("rates.txt", "r") as file:
            rates = file.read() 
        ic(rates)
        rates = json.loads(rates)
        return render_template("view_index.html", title="Company", items=items, rates=rates, languages=languages, lan=lan)
    except Exception as ex:
        ic(ex)
        return "ups"
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()



##############################
@app.get("/items/<item_pk>")
def get_item_by_pk(item_pk):
    try:
        db, cursor = x.db()
        q = "SELECT * FROM items WHERE item_pk = %s AND item_blocked_at = 0"
        cursor.execute(q, (item_pk,))
        item = cursor.fetchone()

        if not item:
            return """
                <mixhtml mix-top="body">
                    Item not found or blocked
                </mixhtml>
            """, 404

        rates= ""
        with open("rates.txt", "r") as file:
            rates = file.read() 
            rates = json.loads(rates)
        
        html_item = render_template("_item.html", item=item, rates=rates)
        return f"""
            <mixhtml mix-replace="#item">
                {html_item}
            </mixhtml>
        """
    except Exception as ex:
        ic(ex)
        if "CPH Sightseer page number" in str(ex):
            return """
                <mixhtml mix-top="body">
                    page number invalid
                </mixhtml>
            """
        return """
            <mixhtml mix-top="body">
                ups
            </mixhtml>
        """
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()



##############################
@app.get("/items/page/<page_number>")
def get_items_by_page(page_number):
    try:
        lan = request.args.get("lan", session.get("lang", "en"))
        if lan not in ("en", "dk"):
            lan = "en"
        session["lang"] = lan

        page = x.validate_page_number(page_number)
        per_page = 2
        offset   = (page - 1) * per_page
        limit    = per_page + 1

        db, cursor = x.db()
        cursor.execute(
            "SELECT * FROM items WHERE item_blocked_at = 0 ORDER BY item_created_at LIMIT %s OFFSET %s",
            (limit, offset)
        )
        items = cursor.fetchall()

        with open("rates.txt") as f:
            rates = json.loads(f.read())

        cards_html = ""
        for itm in items[:per_page]:
            cards_html += render_template("_item_mini.html", item=itm, rates=rates)

        if len(items) > per_page:
            button_html = render_template(
                "_button_more_items.html",
                page_number=page + 1,
                lan=lan,
                languages=languages
            )
        else:
            button_html = ""

        return f"""
          <mixhtml mix-bottom="#items">
            {cards_html}
          </mixhtml>
          <mixhtml mix-replace="#button_more_items">
            {button_html}
          </mixhtml>
          <mixhtml mix-function="add_markers_to_map">
            {json.dumps(items[:per_page])}
          </mixhtml>
        """
    except Exception as ex:
        ic("Error in get_items_by_page:", ex)
        return str(ex), 500
    finally:
        if "cursor" in locals():
            cursor.close()
        if "db" in locals():
            db.close()



##############################
@app.get("/search")
def search():
    try:
        search_for = request.args.get("q", "") 
        db, cursor = x.db()
        q = "SELECT * FROM items WHERE item_name LIKE %s AND item_blocked_at = 0"
        cursor.execute(q, (f"{search_for}%",))
        rows = cursor.fetchall()
        ic(rows)
        return rows 
    except Exception as ex:
        ic(ex)
        return "x", 400
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()




#################################
@app.get("/profile")
@app.get("/profile/<lan>")
def profile(lan="en"):
    try:
        languages_allowed = ["en", "dk"]
        if lan not in languages_allowed: lan = "en"
        
        if not session.get("user"):
            return redirect(url_for("show_login"))
        
        user = session["user"]
        is_session = True
        active_profile = "active"

        return render_template(
            "profile.html",
            title="Profile",
            user=user,
            is_session=is_session,
            active_profile=active_profile,
            languages=languages,
            lan=lan
        )
    except Exception as ex:
        ic(ex)
        return redirect(url_for("show_login"))
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()






def ___ADMIN___(): pass

###############################################################
@app.get("/admin")
@app.get("/admin/<lan>")
def admin_dashboard(lan="en"):
    try:
        if not session.get("user") or session["user"].get("role_fk") != 1:
            return "Access denied", 403

        lan = request.args.get("lan", lan)
        languages_allowed = ["en", "dk"]
        if lan not in languages_allowed:
            lan = "en"

        db, cursor = x.db()
        cursor.execute("CALL get_users()")
        all_users = cursor.fetchall()
       
        users = [u for u in all_users if u.get("role_fk") != 1]
        return render_template("admin.html",
            title="Admin Dashboard",
            users=users,
            is_session=True,
            active_admin="active",
            languages=languages,
            lan=lan
        )
        
    except Exception as ex:
        print("Admin Dashboard Error:", ex)
        return "System under maintenance", 500
    finally:
        if "cursor" in locals(): 
            cursor.close()
        if "db" in locals():
            db.close()



def ___ADMIN___():pass

########################################
@app.get("/admin-user-items")
@app.get("/admin-user-items/<lan>")
def admin_user_items(lan="en"):
    try:
        languages_allowed = ["en", "dk"]
        if lan not in languages_allowed: lan = "en"
        session["lang"] = lan
        
        if not session.get("user"):
            return redirect(url_for("show_login", lan=lan))
        
       
        if session["user"].get("role_fk") != 1:
            return redirect(url_for("profile", lan=lan))
        
        db, cursor = x.db()
        q = """SELECT items.*, users.user_username, users.user_name, users.user_last_name 
               FROM items 
               JOIN users ON items.user_pk = users.user_pk
               ORDER BY items.item_created_at DESC"""
        cursor.execute(q)
        items = cursor.fetchall()
        
        return render_template("admin_user_items.html", 
                              items=items,
                              active_admin_items="active",
                              is_session=True,
                              languages=languages,
                              lan=lan)
    except Exception as ex:
        ic("Error in admin_user_items:", ex)
        return str(ex), 500
    finally:
        if "cursor" in locals():
            cursor.close()
        if "db" in locals():
            db.close()



#################################################
@app.patch("/block-item/<item_pk>")
def block_item(item_pk):
    try:
        if not session.get("user") or session["user"].get("role_fk") != 1:
            return jsonify({"error": "Unauthorized"}), 403
            
        block_time = int(time.time())
        
        db, cursor = x.db()
        
        q = """
            SELECT items.item_name, users.user_name, users.user_last_name, users.user_email 
            FROM items
            JOIN users ON items.user_pk = users.user_pk
            WHERE items.item_pk = %s
        """
        cursor.execute(q, (item_pk,))
        item_data = cursor.fetchone()
        
        if not item_data:
            return jsonify({"error": "Item not found"}), 404
            
       
        q = "UPDATE items SET item_blocked_at = %s WHERE item_pk = %s"
        cursor.execute(q, (block_time, item_pk))
        db.commit()
        
        if cursor.rowcount != 1:
            return jsonify({"error": "Item not found or already blocked"}), 404
        
        x.send_item_block_notification_email(
            item_data["user_name"],
            item_data["user_last_name"],
            item_data["user_email"],
            item_data["item_name"],
            True  
        )
        
        item = {"item_pk": item_pk}
        lan = session.get("lang", "en")
        button_unblock = render_template(
            "_button_unblock_item.html",
            item=item,
            languages=languages,
            lan=lan
        )

        return f"""
        <mixhtml mix-replace="#block-item-{item_pk}">
            {button_unblock}
        </mixhtml>
        """
        
    except Exception as ex:
        ic("Block item error:", ex)
        if "db" in locals():
            db.rollback()
        return jsonify({"error": str(ex)}), 500
        
    finally:
        if "cursor" in locals():
            cursor.close()
        if "db" in locals():
            db.close()


#################################################
@app.patch("/unblock-item/<item_pk>")
def unblock_item(item_pk):
    try:
        if not session.get("user") or session["user"].get("role_fk") != 1:
            return jsonify({"error": "Unauthorized"}), 403
            
        db, cursor = x.db()
        
        q = """
            SELECT items.item_name, users.user_name, users.user_last_name, users.user_email 
            FROM items
            JOIN users ON items.user_pk = users.user_pk
            WHERE items.item_pk = %s
        """
        cursor.execute(q, (item_pk,))
        item_data = cursor.fetchone()
        
        if not item_data:
            return jsonify({"error": "Item not found"}), 404
            
        q = "UPDATE items SET item_blocked_at = 0 WHERE item_pk = %s"
        cursor.execute(q, (item_pk,))
        db.commit()
        
        if cursor.rowcount != 1:
            return jsonify({"error": "Item not found or already unblocked"}), 404
        
        x.send_item_block_notification_email(
            item_data["user_name"],
            item_data["user_last_name"],
            item_data["user_email"],
            item_data["item_name"],
            False  
        )
       
        item = {"item_pk": item_pk}
        lan = session.get("lang", "en")
        button_block = render_template(
            "_button_block_item.html",
            item=item,
            languages=languages,
            lan=lan
        )

        return f"""
        <mixhtml mix-replace="#unblock-item-{item_pk}">
            {button_block}
        </mixhtml>
        """
        
    except Exception as ex:
        ic("Unblock item error:", ex)
        if "db" in locals():
            db.rollback()
        return jsonify({"error": str(ex)}), 500
        
    finally:
        if "cursor" in locals():
            cursor.close()
        if "db" in locals():
            db.close()


############################################ 
@app.patch("/block/<user_pk>")
def block_user(user_pk):
    lan = session.get("lang", "en")
    if lan not in ("en", "dk"):
        lan = "en"

    try:
        db, cursor = x.db()
        cursor.execute("SELECT * FROM users WHERE user_pk = %s", (user_pk,))
        user_data = cursor.fetchone()
        
        if not user_data:
            return "User not found", 404
            
        q = "UPDATE users SET user_blocked_at = %s WHERE user_pk = %s"
        blocked_at = int(time.time())
        cursor.execute(q, (blocked_at, user_pk))
        db.commit()
        
        
        x.send_block_notification_email(
            user_data["user_name"],
            user_data["user_last_name"],
            user_data["user_email"],
            True  
        )

        user = {"user_pk": user_pk}
        button_unblock = render_template(
            "_button_unblock_user.html",
            user=user,
            languages=languages,
            lan=lan
        )

        return f"""
        <mixhtml mix-replace="#block-{user_pk}">
            {button_unblock}
        </mixhtml>
        """
    except Exception as ex:
        ic(ex)
        return str(ex)
    finally:
        if "cursor" in locals():
            cursor.close()
        if "db" in locals():
            db.close()


###########################################################
@app.patch("/unblock/<user_pk>")
def unblock_user(user_pk):
    lan = session.get("lang", "en")
    if lan not in ("en", "dk"):
        lan = "en"

    try:
        db, cursor = x.db()
        cursor.execute("SELECT * FROM users WHERE user_pk = %s", (user_pk,))
        user_data = cursor.fetchone()
        
        if not user_data:
            return "User not found", 404
            
        q = "UPDATE users SET user_blocked_at = NULL WHERE user_pk = %s"
        cursor.execute(q, (user_pk,))
        db.commit()
        
        x.send_block_notification_email(
            user_data["user_name"],
            user_data["user_last_name"],
            user_data["user_email"],
            False 
        )
        
        user = {"user_pk": user_pk}
        button_block = render_template(
            "_button_block_user.html",
            user=user,
            languages=languages,
            lan=lan
        )

        return f"""
        <mixhtml mix-replace="#unblock-{user_pk}">
            {button_block}
        </mixhtml>
        """
    except Exception as ex:
        ic(ex)
        return str(ex)
    finally:
        if "cursor" in locals():
            cursor.close()
        if "db" in locals():
            db.close()





#############################################
@app.delete("/api/v1/users/<user_id>")
def delete_user(user_id):
    try:
        db, cursor = x.db()
        q = "DELETE FROM users WHERE user_pk = %s"
        cursor.execute(q, (user_id,))
        if cursor.rowcount != 1:
            raise Exception("user not found")
        db.commit()
        return f"User {user_id} deleted"
    except Exception as ex:
        return ex, 400
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()
    


def ___Item___(): pass 

############################################ 
@app.get("/items/<item_pk>/window")
@app.get("/<lan>/items/<item_pk>/window")
def get_item_window(item_pk, lan="en"):
    
    if lan not in ("en","dk"):
        lan = "en"
    session["lang"] = lan         

    try:
        db, cursor = x.db()
        cursor.execute("SELECT * FROM items WHERE item_pk = %s", (item_pk,))
        row = cursor.fetchone()

        if not row:
            return "Not found", 404

        
        with open("rates.txt","r") as f:
            rates = json.loads(f.read())

        item_detail = {
            "item_name":      row["item_name"],
            "item_price_usd": "{:,}".format(row["item_price"]),
            "item_price_dkk": "{:,.0f}".format(row["item_price"] * rates["rates"]["DKK"]),
            "item_image":     row["item_image"],
            "item_description": row["item_description"],  
            "item_contact_url": row["item_contact_url"]   
        }

        return render_template(
            "item_detail.html",
            item=item_detail,
            rates=rates,
            languages=languages,
            lan=lan,
        )
    except Exception as ex:
        ic("Error in get_item_window:", ex)
        return str(ex), 500
    finally:
        if "cursor" in locals():
            cursor.close()
        if "db" in locals():
            db.close()



def ____Edit_User_and_Admin___(): pass

############################################ 
@app.get("/edit-profile")
@app.get("/edit-profile/<lan>")
def show_edit_profile(lan="en"):
    try:
        if not session.get("user"):
            return redirect(url_for("show_login", lan=lan))
        
        languages_allowed = ["en", "dk"]
        if lan not in languages_allowed:
            lan = "en"
        
        return render_template(
            "edit_profile.html",
            user=session["user"],
            message=request.args.get("message", ""),
            is_session=True,
            languages=languages,
            lan=lan
        )
    except Exception as ex:
        ic("Error in show_edit_profile:", ex)
        return str(ex), 500
    finally:
        if "cursor" in locals():
            cursor.close()
        if "db" in locals():
            db.close()
    
    
############################################ 
@app.post("/edit-profile")
@app.post("/edit-profile/<lan>")
def edit_profile(lan="en"):
    if not session.get("user"):
        return redirect(url_for("show_login", lan=lan))

    try:
        lan = request.form.get("lan", lan)
        languages_allowed = ["en", "dk"]
        if lan not in languages_allowed:
            lan = "en"

        user_pk = session["user"]["user_pk"]
        user_name = x.validate_user_name()
        user_last_name = x.validate_user_last_name()
        user_email = x.validate_user_email()
        user_username = x.validate_user_username()

        user_updated_at = int(time.time())

        db, cursor = x.db()
        q = """
        UPDATE users
        SET user_name = %s, user_last_name = %s, user_email = %s, user_username = %s, user_updated_at = %s
        WHERE user_pk = %s
        """
        cursor.execute(q, (user_name, user_last_name, user_email, user_username, user_updated_at, user_pk))
        db.commit()

        session["user"].update({
            "user_name": user_name,
            "user_last_name": user_last_name,
            "user_email": user_email,
            "user_username": user_username
        })

        return redirect(url_for("profile", lan=lan))

    except Exception as ex:
        if "db" in locals():
            db.rollback()
        return render_template(
            "edit_profile.html",
            user=session["user"],
            message=str(ex),
            is_session=True,
            languages=languages,
            lan=lan
        )

    finally:
        if "cursor" in locals():
            cursor.close()
        if "db" in locals():
            db.close()






def ____Add_Item_User_and_Admin___(): pass


###############################################################
@app.get("/add-item")
@app.get("/add-item/<lan>")
def add_item_page(lan=None):
    lan = request.args.get("lan", lan or "en")
    if lan not in ("en", "dk"):
        lan = "en"
    session["lang"] = lan

    user = None
    images = []

    try:
        if not session.get("user"):
            return redirect(url_for("show_login", lan=lan))
        user = session["user"]

        db, cursor = x.db()
        cursor.execute(
            "SELECT * FROM images WHERE user_fk = %s",
            (user["user_pk"],)
        )
        images = cursor.fetchall()

    except Exception as ex:
        ic("Error in add_item_page:", ex)
        return str(ex), 500

    finally:
        if "cursor" in locals():
            cursor.close()
        if "db" in locals():
            db.close()

    return render_template(
        "publish_item.html",
        user=user,
        images=images,
        is_session=True,
        active_add_item="active",
        old_values={},
        error_message="",
        languages=languages,
        lan=lan
    )




###############################################################
@app.post("/add-item")
def post_item():
    user = x.validate_user_logged()
    
    try:
        image_names = x.validate_item_images()

        db, cursor = x.db()
        new_images = []
        q = "INSERT INTO images (image_pk, user_fk, image_name) VALUES (%s, %s, %s)"
        for name in image_names:
            img_pk = uuid.uuid4().hex
            cursor.execute(q, (img_pk, user["user_pk"], name))
            new_images.append((img_pk, name))
        db.commit()

        cards = "\n".join(f"""
          <div id="x{pk}" class="image-card">
            <label class="image-selection">
              <input
                type="radio"
                name="selected_image_pk"
                value="{pk}"
                class="image-radio"
                onclick="selectImage('{pk}')"
              >
              <img src="/static/uploads/{name}" alt="Item image">
            </label>
            <button mix-delete="/images/{pk}" class="delete-btn">Delete</button>
          </div>
        """ for pk, name in new_images)

        return (
            f'<mixhtml mix-append="#images">{cards}</mixhtml>'
            f'<mixhtml mix-remove=".no-images"></mixhtml>'
        )

    except Exception as ex:
        msg = str(ex).replace("CPH Sightseer", "").strip()
        return (
            f'<mixhtml mix-append="body">'
              f'<div class="toast error">{msg}</div>'
            f'</mixhtml>',
            400
        )

    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()




###############################################################
@app.delete("/images/<image_pk>")
def delete_image(image_pk):
    user = x.validate_user_logged()
    
    try:
        db, cursor = x.db()
        
        q = """
            SELECT item_fk
              FROM images
             WHERE image_pk = %s
               AND user_fk = %s
        """
        cursor.execute(q, (image_pk, user["user_pk"]))
        row = cursor.fetchone()

        if row and row["item_fk"]:
            q = "DELETE FROM items WHERE item_pk = %s"
            cursor.execute(q, (row["item_fk"],))

        q = "DELETE FROM images WHERE image_pk = %s AND user_fk = %s"
        cursor.execute(q, (image_pk, user["user_pk"]))

        db.commit()

        return f'<mixhtml mix-remove="#x{image_pk}"></mixhtml>'

    except Exception as ex:
        msg = str(ex).replace("CPH Sightseer", "").strip()
        return (
            f'<mixhtml mix-append="body">'
              f'<div class="toast error">{msg}</div>'
            f'</mixhtml>',
            400
        )

    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()




def ____Publish_Item_User_and_Admin___(): pass



#########################################################
@app.post("/publish-item")
def publish_item():
    try:
        lan = request.form.get("lan", "en")
        languages_allowed = ["en", "dk"]
        if lan not in languages_allowed:
            lan = "en"

        user = x.validate_user_logged()

        item_name = x.validate_item_name()
        item_price = x.validate_item_price()
        item_lon, item_lat = x.validate_coordinates()
        selected_image_pk = x.validate_selected_image()
        item_description = x.validate_item_description()
        item_contact_url = x.validate_item_contact_url()
        
        db, cursor = x.db()
        q = """
            SELECT image_name
              FROM images
             WHERE image_pk = %s
               AND user_fk  = %s
               AND item_fk IS NULL
             LIMIT 1
        """
        cursor.execute(q, (selected_image_pk, user["user_pk"]))
        row = cursor.fetchone()
        if not row:
            raise Exception("Selected image is invalid or already used.")

        item_pk = uuid.uuid4().hex
        created_at = int(time.time())
        q = """
            INSERT INTO items
              (item_pk, item_name, item_image, item_price, item_lon, item_lat, item_created_at, user_pk, item_description, item_contact_url)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """
        cursor.execute(q, (
            item_pk,
            item_name,
            "uploads/" + row["image_name"],
            item_price,
            item_lon,
            item_lat,
            created_at,
            user["user_pk"],
            item_description,
            item_contact_url
        ))

        
        q = "UPDATE images SET item_fk = %s WHERE image_pk = %s"
        cursor.execute(q, (item_pk, selected_image_pk))

        db.commit()

        return f'<mixhtml mix-redirect="{url_for("add_item_page")}"></mixhtml>'

    except Exception as ex:
        
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return (
                f'<mixhtml mix-append="body">'
                f'<div class="toast error">{str(ex)}</div>'
                f'</mixhtml>',
                400
            )

        old_values = request.form.to_dict()
        lan = request.form.get("lan", "en")
        if lan not in languages_allowed:
            lan = "en"

        db, cursor = x.db()
        cursor.execute("SELECT * FROM images WHERE user_fk = %s", (user["user_pk"],))
        images = cursor.fetchall()

        return render_template(
            "publish_item.html",
            error_message=str(ex),
            old_values=old_values,
            images=images,
            user=user,
            is_session=True,
            active_add_item="active",
            languages=languages,
            lan=lan
        ), 400

    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()



####################################################### 
@app.get("/edit-items")
@app.get("/edit-items/<lan>")
def show_edit_items(lan="en"):
    try:
       
        if lan not in ("en", "dk"):
            lan = "en"
        session["lang"] = lan

        
        if not session.get("user"):
            return redirect(url_for("show_login", lan=lan))

       
        db, cursor = x.db()
        cursor.execute(
            "SELECT * FROM items WHERE user_pk = %s",
            (session["user"]["user_pk"],)
        )
        items = cursor.fetchall()


        return render_template(
            "edit_items.html",
            items=items,
            active_edit_items="active",
            is_session=True,
            languages=languages,
            lan=lan,
            error_message=""
        )

    except Exception as ex:
        return "An unexpected server error occurred", 500

    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()




####################################################### 
@app.get("/edit-item/<item_pk>")
@app.get("/edit-item/<item_pk>/<lan>")
def show_edit_item(item_pk, lan="en"):
    try:
        if lan not in ("en", "dk"):
            lan = "en"
        session["lang"] = lan

        if not session.get("user"):
            return redirect(url_for("show_login", lan=lan))

        db, cursor = x.db()
        cursor.execute(
            "SELECT * FROM items WHERE item_pk = %s AND user_pk = %s",
            (item_pk, session["user"]["user_pk"])
        )
        item = cursor.fetchone()

        if not item:
            return "Item not found or you don't have permission to edit it.", 404

        return render_template(
            "edit_item.html",
            item=item,
            old_values={},
            is_session=True,
            languages=languages,
            lan=lan,
            error_message=""
        )

    except Exception as ex:
        ic("Unexpected error in show_edit_item:", ex)
        return "An unexpected server error occurred", 500

    finally:
        if "cursor" in locals():
            cursor.close()
        if "db" in locals():
            db.close()


####################################################### 
@app.post("/edit-item/<item_pk>")
@app.post("/edit-item/<item_pk>/<lan>")
def edit_item(item_pk, lan="en"):
    try:
        languages_allowed = ["en", "dk"]
        if lan not in languages_allowed: lan = "en"
        
        if not session.get("user"):
            return redirect(url_for("show_login", lan=lan))
        
        item_name = request.form.get("item_name", "")
        item_price = request.form.get("item_price", "")
        item_lon = request.form.get("item_lon", "")
        item_lat = request.form.get("item_lat", "")
        item_description = request.form.get("item_description", "")
        item_contact_url = request.form.get("item_contact_url", "")
        
        if not item_name or len(item_name) < 3:
            return render_template("edit_item.html", 
                                  error_message="Item name must be at least 3 characters long.",
                                  old_values=request.form,
                                  item={"item_pk": item_pk},
                                  languages=languages,
                                  lan=lan)
        
        db, cursor = x.db()
        q = """UPDATE items 
               SET item_name = %s, item_price = %s, item_lon = %s, item_lat = %s,
               item_description = %s, item_contact_url = %s 
               WHERE item_pk = %s AND user_pk = %s"""
        cursor.execute(q, (item_name, item_price, item_lon, item_lat, 
                          item_description, item_contact_url,
                          item_pk, session["user"]["user_pk"]))
        db.commit()
        
        if cursor.rowcount != 1:
            return "Item not found or you don't have permission to edit it."
        
        return redirect(url_for("show_edit_items", lan=lan))
    except Exception as ex:
        ic(ex)
        if "db" in locals(): db.rollback()
        return render_template("edit_item.html", 
                              error_message=str(ex),
                              old_values=request.form,
                              item={"item_pk": item_pk},
                              languages=languages,
                              lan=lan)
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()



def ____Log_out___(): pass
##############################################################
@app.get("/logout")
def logout():
    session.pop("user")
    return redirect(url_for("show_login"))