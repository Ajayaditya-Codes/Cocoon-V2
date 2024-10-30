from flask import Flask, jsonify, request, session, send_file, Response
from flask_session import Session
from flask_cors import CORS
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import re
from datetime import datetime 
import tempfile
from dotenv import load_dotenv
import requests
import os
from celery import Celery
from celery.schedules import crontab
from dotenv import load_dotenv
from fpdf import FPDF
import pandas as pd
import io

load_dotenv()
app = Flask(__name__)

CORS(app, supports_credentials=True)

app.config['SESSION_TYPE'] = 'filesystem' 
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True  
app.config['SECRET_KEY'] = 'aefnjnsdfjnqoiwj18921@q83&e239asd' 

Session(app)

MAILGUN_API_URL = os.getenv('MAILGUN_API_URL')
MAILGUN_API_KEY = os.getenv('MAILGUN_API_KEY')  
MAILGUN_FROM_EMAIL = os.getenv('MAILGUN_FROM_EMAIL')

app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
celery = Celery(__name__, broker=app.config['CELERY_BROKER_URL'])

@celery.task
def send_celery_email():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        users = cursor.execute("SELECT email, username, id FROM credentials WHERE userType = 'professional'").fetchall()

        user_list = [dict(user) for user in users]

        for user in user_list:
            cursor.execute("""
                SELECT 
                    sr.id AS request_id,
                    c.full_name AS customer_name,
                    c.address,
                    c.pincode,
                    sr.price,
                    sr.date_of_service,
                    sr.service_description,
                    c.phone,
                    sr.service_status
                FROM service_requests sr
                JOIN customers c ON sr.customer_id = c.credential_id
                WHERE sr.professional_id = ? AND (sr.service_status = 'requested' OR sr.service_status = 'assigned')
            """, (user["id"],))
            services = cursor.fetchall()

            services = [dict(service) for service in services]

            email_content = f"Hello,\n\nHere are your pending service requests:\n\n"

            for service in services:
                email_content += (
                    f"Request ID: {service['request_id']}\n" 
                    f"Customer Name: {service['customer_name']}\n"
                    f"Address: {service['address']}\n"  
                    f"Pincode: {service['pincode']}\n" 
                    f"Price: {service['price']}\n"  
                    f"Date of Service: {service['date_of_service']}\n"  
                    f"Description: {service['service_description']}\n"  
                    f"Phone: {service['phone']}\n"  
                    f"Status: {service['service_status']}\n\n"  
                )
            
            email_content += "Thank you!\nCocoon Team"

            response = requests.post(
                MAILGUN_API_URL,
                auth=("api", MAILGUN_API_KEY),
                data={
                    "from": MAILGUN_FROM_EMAIL,
                    "to": user["email"],
                    "subject": "Cocoon Daily Report Remainder - Celery",
                    "text": email_content
                }
            )

            if response.status_code == 200:
                return {'success': True, 'message': 'Email sent successfully'}
            else:
                return {'success': False, 'error': response.json()}

    except sqlite3.Error as e:
        return jsonify({"success": False, "error": "Database error", "message": str(e), "code": 500}), 500

    finally:
        conn.close()

@celery.task
def generate_professional_monthly_report():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        users = cursor.execute("SELECT email, username, id FROM credentials WHERE userType = 'professional'").fetchall()

        user_list = [dict(user) for user in users]

        for user in user_list:
            query = """
            SELECT 
                sr.id AS request_id,
                c.full_name AS customer_name,
                c.address AS customer_address,
                c.pincode AS customer_pincode,
                c.phone AS customer_phone,
                sr.price,
                sr.date_of_service,
                sr.service_description,
                sr.service_status,
                sr.rating,
                sr.review,
                s.name AS service_name    
            FROM service_requests sr
            JOIN customers c ON sr.customer_id = c.credential_id
            JOIN services s ON s.id = sr.service_id
            WHERE sr.professional_id = ? 
            """

            email_content = f"Hey, {user['username']}. Find your monthly report attached below.\n\n Thank You! \n Cocoon Team"

            cursor.execute(query, (user['id'],))
            rows = cursor.fetchall()

            if not rows:
                raise Exception("No service requests found for the specified professional.")

            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt="Service Requests Report", ln=True, align='C')

            for row in rows:
                pdf.cell(0, 10, txt=f"Request ID: {row['request_id']}", ln=True)
                pdf.cell(0, 10, txt=f"Customer Name: {row['customer_name']}", ln=True)
                pdf.cell(0, 10, txt=f"Customer Address: {row['customer_address']}", ln=True)
                pdf.cell(0, 10, txt=f"Customer Pincode: {row['customer_pincode']}", ln=True)
                pdf.cell(0, 10, txt=f"Customer Phone: {row['customer_phone']}", ln=True)
                pdf.cell(0, 10, txt=f"Price: {row['price']:.2f}", ln=True)
                pdf.cell(0, 10, txt=f"Date of Service: {row['date_of_service']}", ln=True)
                pdf.cell(0, 10, txt=f"Service Description: {row['service_description']}", ln=True)
                pdf.cell(0, 10, txt=f"Service Status: {row['service_status']}", ln=True)
                pdf.cell(0, 10, txt=f"Rating: {row['rating']}", ln=True)
                pdf.cell(0, 10, txt=f"Review: {row['review']}", ln=True)
                pdf.cell(0, 10, txt=f"Service Name: {row['service_name']}", ln=True)
                pdf.cell(0, 10, txt="", ln=True) 

            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                pdf.output(temp_file.name)  
                temp_file.seek(0)  

            with open(temp_file.name, 'rb') as pdf_file:
                response = requests.post(
                    MAILGUN_API_URL,
                    auth=("api", MAILGUN_API_KEY),
                    data={
                        "from": MAILGUN_FROM_EMAIL,
                        "to": user['email'],
                        "subject": "Cocoon Monthly Report - Celery",
                        "text": email_content
                    },
                    files={
                        "attachment": (temp_file.name, pdf_file, "application/pdf")
                    }
                )

                if response.status_code == 200:
                    return {'success': True, 'message': 'Email sent successfully'}
                else:
                    return {'success': False, 'error': response.json()}

    except sqlite3.Error as e:
        return jsonify({"success": False, "error": "Database error", "message": str(e), "code": 500}), 500

    finally:
        conn.close()

@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(crontab(hour = "1", minute="30"), send_celery_email.s())
    sender.add_periodic_task(crontab(day_of_month= "1", hour = "6", minute="40"), generate_professional_monthly_report.s())

setup_periodic_tasks(celery)

def send_email(to_email, subject, text):
    api_url = MAILGUN_API_URL
    api_key = MAILGUN_API_KEY
    from_email = MAILGUN_FROM_EMAIL

    response = requests.post(
        api_url,
        auth=("api", api_key),
        data={
            "from": from_email,
            "to": to_email,
            "subject": subject,
            "text": text
        }
    )

    if response.status_code == 200:
        return {'success': True, 'message': 'Email sent successfully'}
    else:
        return {'success': False, 'error': response.json()}

def get_db_connection():
    conn = sqlite3.connect("./database/database.db")
    conn.row_factory = sqlite3.Row
    return conn

def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def is_strong_password(password):
    return len(password) >= 8 and any(c.isdigit() for c in password) and any(c.isupper() for c in password) and any(c.islower() for c in password)

@app.route("/")
def home():
    return "Cocoon V2"

@app.route("/login", methods=["POST"])
def login():
    session.clear()

    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"message": "Email and Password are required"}), 400

    if not is_valid_email(email):
        return jsonify({"message": "Invalid email format"}), 400

    try:
        conn = get_db_connection()
        user = conn.execute(
            "SELECT * FROM credentials WHERE email = ?", (email,)
        ).fetchone()

        if user:
            if user["blocked"] == 1:
                return jsonify({"message": "Account is blocked. Please contact support."}), 403

            if check_password_hash(user["password"], password):
                session['user_id'] = user['id']
                session['user_type'] = user['userType']

                return jsonify({"message": "Login successful", "user": user["userType"]}), 200
            else:
                return jsonify({"message": "Invalid email or password"}), 401
        else:
            return jsonify({"message": "Invalid email or password"}), 401

    except sqlite3.Error as e:
        return jsonify({"message": f"Database error: {str(e)}"}), 500

    finally:
        conn.close()

@app.route("/session-status", methods=["GET"])
def session_status():
    try:
        if 'user_id' in session and 'user_type' in session:
            return jsonify({
                "message": "User is logged in",
                "user_id": session['user_id'],
                "user_type": session['user_type']
            }), 200
        else:
            return jsonify({"message": "No user is logged in"}), 401

    except Exception as e:
        return jsonify({"message": "An error occurred."}), 500

@app.route("/logout", methods=["GET"])
def logout():
    session.clear()  
    return jsonify({"message": "Logged out successfully"}), 200    

#remove the route later --- only for debugging
@app.route("/users")
def users():
    try:
        conn = get_db_connection()
        users = conn.execute("""
            SELECT c.id, c.username, c.email, c.userType,
                   CASE 
                       WHEN c.userType = 'customer' THEN cu.full_name 
                       WHEN c.userType = 'professional' THEN p.full_name 
                   END AS full_name,
                   CASE 
                       WHEN c.userType = 'customer' THEN cu.address 
                       WHEN c.userType = 'professional' THEN p.service_provided 
                   END AS additional_info,
                   CASE 
                       WHEN c.userType = 'customer' THEN cu.pincode 
                       WHEN c.userType = 'professional' THEN p.pincode 
                   END AS pincode
            FROM credentials c
            LEFT JOIN customers cu ON c.id = cu.credential_id
            LEFT JOIN professionals p ON c.id = p.credential_id
        """).fetchall()

        if not users:
            return jsonify({"message": "No users found"}), 404

        users_list = [dict(user) for user in users]
        return jsonify(users_list), 200

    except sqlite3.Error as e:
        return jsonify({"message": f"Database error: {str(e)}"}), 500

    except Exception as e:
        return jsonify({"message": f"An unexpected error occurred: {str(e)}"}), 500

    finally:
        conn.close()

@app.route("/signup-customer", methods=["POST"])
def signup_customer():
    data = request.get_json()

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    full_name = data.get("fullName")
    address = data.get("address")
    pin_code = data.get("pinCode")
    phone = data.get("phone")

    if not all([username, email, password, full_name, pin_code, phone]):
        return jsonify({"success": False, "message": "All fields are required."}), 400

    if not is_valid_email(email):
        return jsonify({"success": False, "message": "Invalid email format."}), 400

    if not is_strong_password(password):
        return jsonify({
            "success": False,
            "message": "Password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, and one digit."
        }), 400

    if len(str(pin_code)) != 6:  
        return jsonify({"success": False, "message": "Pin code must be a 6-digit number."}), 400

    if len(str(phone)) != 10:  
        return jsonify({"success": False, "message": "PHone number must be a 10-digit number."}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM credentials WHERE username = ? OR email = ?",
            (username, email),
        )
        existing_user = cursor.fetchone()

        if existing_user:
            return jsonify({"success": False, "message": "Username or email already exists."}), 409

        hashed_password = generate_password_hash(password)
        cursor.execute(
            "INSERT INTO credentials (username, password, email, userType) VALUES (?, ?, ?, ?)",
            (username, hashed_password, email, "customer"),
        )
        credential_id = cursor.lastrowid

        cursor.execute(
            "INSERT INTO customers (credential_id, full_name, address, pincode, phone) VALUES (?, ?, ?, ?, ?)",
            (credential_id, full_name, address, pin_code, phone),
        )

        conn.commit()
        return jsonify({"success": True, "message": "Customer registered successfully."}), 201

    except sqlite3.IntegrityError:
        return jsonify({"success": False, "message": "Database integrity error, please check your inputs."}), 409

    except sqlite3.Error as e:
        conn.rollback()
        return jsonify({"success": False, "message": f"Database error: {str(e)}"}), 500

    finally:
        conn.close()

@app.route("/signup-professional", methods=["POST"])
def signup_professional():
    data = request.get_json()

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    full_name = data.get("fullName")
    service_provided = data.get("serviceProvided")
    pin_code = data.get("pinCode")
    experience = data.get("experience")
    link = data.get("link")
    phone = data.get("phone")


    if not all([username, email, password, full_name, service_provided, pin_code, experience, phone, link]):
        return jsonify({"success": False, "message": "All fields are required"}), 400

    if not is_valid_email(email):
        return jsonify({"success": False, "message": "Invalid email format"}), 400

    if not is_strong_password(password):
        return jsonify({"success": False, "message": "Password must be at least 8 characters long and contain uppercase, lowercase, and numeric characters"}), 400

    if len(str(pin_code)) != 6:  
        return jsonify({"success": False, "message": "Pin code must be a 6-digit number."}), 400

    if len(str(phone)) != 10:  
        return jsonify({"success": False, "message": "Phone number must be a 10-digit number."}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM credentials WHERE username = ? OR email = ?", (username, email)
        )
        existing_user = cursor.fetchone()

        if existing_user:
            return jsonify({"success": False, "message": "Username or email already exists"}), 409

        hashed_password = generate_password_hash(password)
        cursor.execute(
            "INSERT INTO credentials (username, password, email, userType) VALUES (?, ?, ?, ?)",
            (username, hashed_password, email, "professional"),
        )
        credential_id = cursor.lastrowid

        cursor.execute(
            "INSERT INTO professionals (credential_id, full_name, service_provided, pincode, experience, documents, phone) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (credential_id, full_name, service_provided, pin_code, experience, link, phone),
        )

        conn.commit()
        return jsonify({"success": True, "message": "Professional registered successfully"}), 201

    except sqlite3.Error as e:
        conn.rollback()
        return jsonify({"success": False, "message": "Database error occurred. Please try again later."}), 500

    except Exception as e:

        return jsonify({"success": False, "message": "An unexpected error occurred. Please try again later."}), 500

    finally:
        conn.close()

@app.route("/services", methods=["GET"])
def services():
    try:
        conn = get_db_connection()
        services = conn.execute("SELECT id, name, price, description FROM services").fetchall()
        services_list = [{"id": service["id"], "name": service["name"], "price": service["price"], "description": service["description"]} for service in services]
        return jsonify(services_list), 200
    
    except sqlite3.Error:
        return jsonify({"success": False, "message": "Failed to fetch services. Please try again later."}), 500
    
    except Exception as e:
        return jsonify({"success": False, "message": "An unexpected error occurred. Please try again later."}), 500
    
    finally:
        conn.close()

@app.route('/customer/profile', methods=['GET'])
def get_customer_profile():
    try:
        user_id = session.get('user_id')
        user_type = session.get('user_type')

        if not user_id:
            return jsonify({"success": False, "error": "User ID not found in session", "message": "Please log in."}), 400
        if user_type != 'customer':
            return jsonify({"success": False, "error": "Unauthorized access", "message": "You do not have permission to access this resource."}), 403

        try:
            conn = get_db_connection()
            user_info = conn.execute(
                """SELECT c.full_name, c.address, c.pincode, cr.email, cr.username, c.phone
                   FROM customers AS c
                   JOIN credentials AS cr ON c.credential_id = cr.id
                   WHERE c.credential_id = ?""",
                (user_id,)
            ).fetchone()

            if user_info is None:
                return jsonify({"success": False, "error": "User not found", "message": "No user profile found."}), 404

            return jsonify(dict(user_info)), 200

        finally:
            conn.close()

    except sqlite3.Error as e:
        return jsonify({"success": False, "error": "Database error", "message": str(e)}), 500

@app.route("/customer/profile", methods=["PUT"])
def update_customer_profile():
    try:
        user_id = session.get('user_id')
        user_type = session.get('user_type')

        if not user_id:
            return jsonify({"success": False, "error": "User not authenticated", "message": "Please log in."}), 401
        if user_type != 'customer':
            return jsonify({"success": False, "error": "Unauthorized access", "message": "You do not have permission to access this resource."}), 403

        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "Invalid input", "message": "No data provided."}), 400

        full_name = data.get("full_name")
        address = data.get("address")
        pincode = data.get("pincode")
        password = data.get("password")
        phone = data.get("phone")

        if not full_name or not address or not pincode:
            return jsonify({"success": False, "error": "Missing fields", "message": "Full name, address, and pincode are required."}), 400

        if len(str(pincode)) != 6:
            return jsonify({"success": False, "error": "Invalid pin code", "message": "Pin code must be a 6-digit number."}), 400

        try:
            conn = get_db_connection()
            conn.execute(
                "UPDATE customers SET full_name = ?, address = ?, pincode = ?, phone = ? WHERE credential_id = ?",
                (full_name, address, pincode, phone, user_id)
            )

            if password:
                if not is_strong_password(password):
                    return jsonify({"success": False, "error": "Weak password", "message": "Password must be at least 8 characters long and contain uppercase, lowercase, and numeric characters."}), 400
                
                hashed_password = generate_password_hash(password)
                conn.execute(
                    "UPDATE credentials SET password = ? WHERE id = ?",
                    (hashed_password, user_id)
                )

            conn.commit()
            return jsonify({"success": True, "message": "Profile updated successfully."}), 200

        except sqlite3.Error as e:
            conn.rollback()
            return jsonify({"success": False, "error": "Database error", "message": str(e)}), 500

        finally:
            conn.close()

    except sqlite3.Error as e:
        return jsonify({"success": False, "error": "Database error", "message": str(e)}), 500

@app.route('/professional/profile', methods=['GET'])
def get_professional_profile():
    try:
        user_id = session.get('user_id')
        user_type = session.get('user_type')

        if not user_id:
            return jsonify({
                "success": False,
                "message": "User ID not found in session. Please log in.",
                "error": "User ID missing",
                "code": 400
            }), 400

        if user_type != 'professional':
            return jsonify({
                "success": False,
                "message": "Unauthorized access. You do not have permission to access this resource.",
                "error": "Unauthorized",
                "code": 403
            }), 403

        try:
            conn = get_db_connection()
            professional_info = conn.execute(
                """SELECT p.full_name, p.service_provided, p.pincode, cr.email, cr.username, p.experience, p.phone, p.verified  
                   FROM professionals AS p
                   JOIN credentials AS cr ON p.credential_id = cr.id
                   WHERE p.credential_id = ?""",
                (user_id,)
            ).fetchone()

            if professional_info is None:
                return jsonify({
                    "success": False,
                    "message": "Professional not found.",
                    "error": "Not Found",
                    "code": 404
                }), 404

            return jsonify(dict(professional_info)), 200

        finally:
            conn.close()

    except sqlite3.Error as e:
        return jsonify({
            "success": False,
            "message": "Database error",
            "error": str(e),
            "code": 500
        }), 500

@app.route("/professional/profile", methods=["PUT"])
def update_professional_profile():
    try:
        user_id = session.get('user_id')
        user_type = session.get('user_type')

        if not user_id:
            return jsonify({
                "success": False,
                "message": "User not authenticated.",
                "error": "Unauthorized",
                "code": 401
            }), 401

        if user_type != 'professional':
            return jsonify({
                "success": False,
                "message": "Unauthorized access.",
                "error": "Unauthorized",
                "code": 403
            }), 403

        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "message": "Invalid input.",
                "error": "Bad Request",
                "code": 400
            }), 400

        full_name = data.get("full_name")
        service_provided = data.get("service_provided")
        pincode = data.get("pincode")
        password = data.get("password")
        experience = data.get("experience")
        phone = data.get("phone")

        if not full_name or not service_provided or not pincode:
            return jsonify({
                "success": False,
                "message": "Full name, service provided, and pincode are required.",
                "error": "Validation Error",
                "code": 400
            }), 400

        try:
            conn = get_db_connection()

            try:
                conn.execute(
                    "UPDATE professionals SET full_name = ?, service_provided = ?, pincode = ?, experience = ?, phone = ? WHERE credential_id = ?",
                    (full_name, service_provided, pincode,  experience, phone, user_id)
                )

                if password:
                    if not is_strong_password(password):
                        return jsonify({
                            "success": False,
                            "message": "Password must be at least 8 characters long and contain uppercase, lowercase, and numeric characters.",
                            "error": "Weak Password",
                            "code": 400
                        }), 400

                    hashed_password = generate_password_hash(password)
                    conn.execute(
                        "UPDATE credentials SET password = ? WHERE id = ?",
                        (hashed_password, user_id)
                    )

                conn.commit()
                return jsonify({
                    "success": True,
                    "message": "Profile updated successfully."
                }), 200

            except sqlite3.Error as e:
                conn.rollback()
                return jsonify({
                    "success": False,
                    "message": "Database error",
                    "error": str(e),
                    "code": 500
                }), 500

        finally:
            conn.close()

    except sqlite3.Error as e:
        return jsonify({
            "success": False,
            "message": "Database error",
            "error": str(e),
            "code": 500
        }), 500

@app.route('/get_services', methods=['GET'])
def get_services():
    try:
        conn = get_db_connection()
        services = conn.execute('''
            SELECT 
                p.full_name AS professionalName,
                s.name AS serviceName,
                p.pincode,
                s.id AS id,
                p.credential_id AS professional_id,
                s.price,
                p.phone as p_phone,
                (SELECT AVG(sr.rating) 
                FROM service_requests sr 
                WHERE sr.professional_id = p.credential_id   
                AND sr.service_status = 'closed') AS average_rating
             FROM 
                professionals p
            JOIN 
                services s ON p.service_provided = s.name
            JOIN 
                credentials cr ON cr.id = p.credential_id
            WHERE 
                p.verified = 1 AND
                cr.blocked = 0
            ORDER BY
                average_rating DESC
        ''').fetchall()
        
        services_list = [dict(service) for service in services]
        return jsonify(services_list), 200

    except sqlite3.Error as e:
        return jsonify({"success": False, "error": "Database error", "message": str(e), "code": 500}), 500

    finally:
        conn.close()

@app.route('/book_service', methods=['POST'])
def book_service():
    conn = get_db_connection()
    try:
        user_type = session.get('user_type')
        user_id = session.get('user_id') 

        if user_type != 'customer' or not user_id:
            return jsonify({"success": False, "error": "Unauthorized access", "message": "User must be authenticated as a customer", "code": 403}), 403

        data = request.get_json()
    
        if not data or 'service_id' not in data or 'professional_id' not in data or 'price' not in data or 'service_date' not in data or 'service_description' not in data:
            return jsonify({"success": False, "error": "Invalid input", "message": "Required fields are missing", "code": 400}), 400

        service_id = data['service_id']
        professional_id = data['professional_id']
        price = data['price']
        service_date = data['service_date']
        service_description = data['service_description']

        service_date_obj = datetime.strptime(service_date, '%Y-%m-%d')
        current_date = datetime.now().date()

        if service_date_obj.date() < current_date:
            return jsonify({"success": False, "error": "Invalid date", "message": "Service date cannot be before the current date.", "code": 400}), 400


        customer = conn.execute('''
            SELECT c.credential_id
            FROM customers AS c
            WHERE c.credential_id = ?
        ''', (user_id,)).fetchone()

        if not customer:
            return jsonify({"success": False, "error": "Customer not found", "message": "No customer found with the provided ID", "code": 404}), 404

        professional = conn.execute('''
            SELECT * FROM professionals WHERE credential_id = ?
        ''', (professional_id,)).fetchone()

        if not professional:
            return jsonify({"success": False, "error": "Professional not found", "message": "No professional found with the provided ID", "code": 404}), 404

        conn.execute(
            '''INSERT INTO service_requests (service_id, customer_id, professional_id, price, service_status, date_of_service, service_description)
               VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (service_id, customer["credential_id"], professional_id, price, 'requested', service_date, service_description)
        )
        conn.commit()

        return jsonify({"success": True, "message": "Service booked successfully", "code": 201}), 201

    except sqlite3.Error as e:
        return jsonify({"success": False, "error": "Database error", "message": str(e), "code": 500}), 500

    finally:
        conn.close()

@app.route('/service-requests/<status>', methods = ['GET'])
def get_service_requests(status):
    user_id, user_type = session.get('user_id'), session.get('user_type')

    if user_type != 'customer' and user_type != 'professional':
        return jsonify({"success": False, "error": "Unauthorized", "message": "Login to Request", "code": 403}), 403

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT 
                sr.id AS request_id,
                p.full_name AS professional_name,
                c.full_name AS customer_name,
                c.address,
                c.pincode as customer_pincode,
                p.pincode as professional_pincode,
                sr.price,
                sr.date_of_service,
                sr.service_description,
                p.service_provided,
                s.name as service_name,
                p.credential_id as professional_id,
                c.phone as c_phone,
                p.phone p_phone
            FROM service_requests sr
            JOIN professionals p ON sr.professional_id = p.credential_id
            JOIN customers c ON sr.customer_id = c.credential_id
            JOIN services s on s.id = sr.service_id
            WHERE (sr.customer_id = ? OR sr.professional_id = ?) AND sr.service_status = ?
        """, (user_id, user_id, status))
        services = cursor.fetchall()

        return jsonify([dict(service) for service in services]), 200
    
    except sqlite3.Error as e:
        return jsonify({"success": False, "error": "Database error", "message": str(e), "code": 500}), 500

    finally:
        conn.close()

@app.route('/generate-report/professional', methods=['GET'])
def generate_professional_report():
    professional_id, user_type = session.get('user_id'), session.get('user_type')
    if user_type != 'professional':
        return jsonify({"success": False, "error": "Unauthorized", "message": "Login to generate report", "code": 403}), 403
    query = """
    SELECT 
        sr.id AS request_id,
        c.full_name AS customer_name,
        c.address AS customer_address,
        c.pincode AS customer_pincode,
        c.phone AS customer_phone,
        sr.price,
        sr.date_of_service,
        sr.service_description,
        sr.service_status,
        sr.rating,
        sr.review,
        s.name AS service_name    
    FROM service_requests sr
    JOIN customers c ON sr.customer_id = c.credential_id
    JOIN services s ON s.id = sr.service_id
    WHERE sr.professional_id = ? 
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, (professional_id,))
        rows = cursor.fetchall()

        if not rows:
            raise Exception("No service requests found for the specified professional.")

    except sqlite3.Error as e:
        raise Exception("Database query error: " + str(e))
    except Exception as e:
        raise Exception("Error fetching data: " + str(e))
    finally:
        conn.close()

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Service Requests Report", ln=True, align='C')

    for row in rows:
        pdf.cell(0, 10, txt=f"Request ID: {row['request_id']}", ln=True)
        pdf.cell(0, 10, txt=f"Customer Name: {row['customer_name']}", ln=True)
        pdf.cell(0, 10, txt=f"Customer Address: {row['customer_address']}", ln=True)
        pdf.cell(0, 10, txt=f"Customer Pincode: {row['customer_pincode']}", ln=True)
        pdf.cell(0, 10, txt=f"Customer Phone: {row['customer_phone']}", ln=True)
        pdf.cell(0, 10, txt=f"Price: {row['price']:.2f}", ln=True)
        pdf.cell(0, 10, txt=f"Date of Service: {row['date_of_service']}", ln=True)
        pdf.cell(0, 10, txt=f"Service Description: {row['service_description']}", ln=True)
        pdf.cell(0, 10, txt=f"Service Status: {row['service_status']}", ln=True)
        pdf.cell(0, 10, txt=f"Rating: {row['rating']}", ln=True)
        pdf.cell(0, 10, txt=f"Review: {row['review']}", ln=True)
        pdf.cell(0, 10, txt=f"Service Name: {row['service_name']}", ln=True)
        pdf.cell(0, 10, txt="", ln=True) 

    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
        pdf.output(temp_file.name)  
        temp_file.seek(0)  

        return send_file(temp_file.name, as_attachment=True, download_name='professional_report.pdf', mimetype='application/pdf')

@app.route('/generate-report/customer/', methods=['GET'])
def generate_customer_report():
    customer_id, user_type = session.get('user_id'), session.get('user_type')
    if user_type != 'customer':
        return jsonify({"success": False, "error": "Unauthorized", "message": "Login to generate report", "code": 403}), 403
    query = """
    SELECT 
        sr.id AS request_id,
        p.full_name AS professional_name,
        p.service_provided AS professional_service,
        p.pincode AS professional_pincode,
        p.phone AS professional_phone,
        sr.price,
        sr.date_of_service,
        sr.service_description,
        sr.service_status,
        sr.rating,
        sr.review,
        s.name AS service_name    
    FROM service_requests sr
    JOIN professionals p ON sr.professional_id = p.credential_id
    JOIN services s ON s.id = sr.service_id
    WHERE sr.customer_id = ? 
    """
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, (customer_id,))
        rows = cursor.fetchall()

        if not rows:
            raise Exception("No service requests found for the specified customer.")

    except sqlite3.Error as e:
        raise Exception("Database query error: " + str(e))
    except Exception as e:
        raise Exception("Error fetching data: " + str(e))
    finally:
        conn.close()

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Service Requests Report", ln=True, align='C')

    for row in rows:
        pdf.cell(0, 10, txt=f"Request ID: {row['request_id']}", ln=True)
        pdf.cell(0, 10, txt=f"Professional Name: {row['professional_name']}", ln=True)
        pdf.cell(0, 10, txt=f"Professional Service: {row['professional_service']}", ln=True)
        pdf.cell(0, 10, txt=f"Professional Pincode: {row['professional_pincode']}", ln=True)
        pdf.cell(0, 10, txt=f"Professional Phone: {row['professional_phone']}", ln=True)
        pdf.cell(0, 10, txt=f"Price: {row['price']:.2f}", ln=True)
        pdf.cell(0, 10, txt=f"Date of Service: {row['date_of_service']}", ln=True)
        pdf.cell(0, 10, txt=f"Service Description: {row['service_description']}", ln=True)
        pdf.cell(0, 10, txt=f"Service Status: {row['service_status']}", ln=True)
        pdf.cell(0, 10, txt=f"Rating: {row['rating']}", ln=True)
        pdf.cell(0, 10, txt=f"Review: {row['review']}", ln=True)
        pdf.cell(0, 10, txt=f"Service Name: {row['service_name']}", ln=True)
        pdf.cell(0, 10, txt="", ln=True)  

    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
        pdf.output(temp_file.name)  
        temp_file.seek(0)  

        return send_file(temp_file.name, as_attachment=True, download_name='customer_report.pdf', mimetype='application/pdf')

@app.route('/generate-report/admin/', methods=['GET'])
def generate_admin_report():
    user_type = session.get('user_type')
    if user_type != 'admin':
        return jsonify({"success": False, "error": "Unauthorized", "message": "Login to generate report", "code": 403}), 403
    query = """
        SELECT 
            sr.id AS request_id,
            sr.date_of_request,
            sr.date_of_service,
            sr.service_description,
            sr.price,
            sr.service_status,
            sr.rating,
            sr.review,
            cn.customer_id,
            cn.full_name AS customer_name,
            cn.customer_username,
            cn.address AS customer_address,
            cn.pincode AS customer_pincode,
            cn.phone AS customer_phone,
            cn.customer_mail,
            pn.professional_id,
            pn.full_name AS professional_name,
            pn.service_provided AS professional_service,
            pn.pincode AS professional_pincode,
            pn.experience AS professional_experience,
            pn.phone AS professional_phone,
            pn.professional_mail,
            pn.professional_username
        FROM 
            service_requests sr
        JOIN 
            (SELECT 
                cr.id AS customer_id, 
                cr.email as customer_mail,
                cr.username as customer_username,
                c.full_name, 
                c.address, 
                c.pincode, 
                c.phone 
            FROM 
                customers c 
            JOIN 
                credentials cr ON c.credential_id = cr.id) AS cn
        ON 
            sr.customer_id = cn.customer_id
        LEFT JOIN 
            (SELECT 
                cr.id AS professional_id, 
                cr.email as professional_mail,
                cr.username as professional_username,
                p.full_name, 
                p.service_provided, 
                p.pincode, 
                p.experience, 
                p.phone 
            FROM 
                professionals p 
            JOIN 
                credentials cr ON p.credential_id = cr.id) AS pn
        ON 
            sr.professional_id = pn.professional_id
    """
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()

        if not rows:
            raise Exception("No service requests found for the specified customer.")

        df = pd.read_sql_query(query, conn)

        output = io.BytesIO()
        df.to_csv(output, index=False)
        output.seek(0)

        return Response(
            output,
            mimetype='text/csv',
            headers={"Content-Disposition": "attachment;filename=service_requests.csv"}
        )

    except sqlite3.Error as e:
        raise Exception("Database query error: " + str(e))
    except Exception as e:
        raise Exception("Error fetching data: " + str(e))
    finally:
        conn.close()

@app.route('/delete-service-request/<int:request_id>', methods=['DELETE'])
def delete_service_request(request_id):
    user_id, user_type = session.get('user_id'), session.get('user_type')

    if user_type != 'customer' and user_type != 'professional':
        return jsonify({"success": False, "error": "Unauthorized", "message": "Login to delete request", "code": 403}), 403

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT * FROM service_requests WHERE id = ? AND (customer_id = ? OR professional_id = ?) AND service_status != 'closed' AND service_status != 'assigned'", 
            (request_id, user_id, user_id)
        )
        request = cursor.fetchone()
        
        if not request:
            return jsonify({"success": False, "error": "Request not found", "message": "Request not found or unauthorized", "code": 404}), 404

        cursor.execute("DELETE FROM service_requests WHERE id = ?", (request_id,))
        conn.commit()
        return jsonify({"success": True, "message": "Request deleted successfully", "code": 200}), 200

    except sqlite3.Error as e:
        return jsonify({"success": False, "error": "Database error", "message": str(e), "code": 500}), 500

    finally:
        conn.close()

@app.route('/accept-service-request/<int:request_id>', methods=['GET'])
def accept_service_request(request_id):
    user_id, user_type = session.get('user_id'), session.get('user_type')

    if user_type != 'professional' and user_type != 'customer':
        return jsonify({"success": False, "error": "Unauthorized", "message": "Login to Send Request", "code": 403}), 403

    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "SELECT * FROM service_requests WHERE id = ? AND service_status != 'closed' AND service_status != 'assigned' AND (professional_id = ? OR customer_id = ?)", 
            (request_id,user_id, user_id))
        request = cursor.fetchone()
        
        if not request:
            return jsonify({"success": False, "error": "Request not found", "message": "Request not found or already accepted", "code": 404}), 404

        cursor.execute("UPDATE service_requests SET service_status = 'assigned' WHERE id = ?", (request_id,))
        conn.commit()
        return jsonify({"success": True, "message": "Request accepted successfully", "code": 200}), 200
    
    except sqlite3.Error as e:
        return jsonify({"success": False, "error": "Database error", "message": str(e), "code": 500}), 500
    
    finally:
        conn.close()

@app.route('/close-service-request/<int:request_id>', methods=['POST', 'PUT'])
def close_service_request(request_id):
    user_id, user_type = session.get('user_id'), session.get('user_type')

    data = request.get_json()
    rating = data["rating"]
    review = data["review"]

    if user_type != 'customer':
        return jsonify({"success": False, "error": "Unauthorized", "message": "User must be a customer to close request", "code": 403}), 403

    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "SELECT * FROM service_requests WHERE customer_id = ? AND id = ? AND service_status = 'assigned'", 
            (user_id, request_id,))
        request_ = cursor.fetchone()
        
        if not request_:
            return jsonify({"success": False, "error": "Request not found", "message": "Request not found or unauthorized", "code": 404}), 404

        cursor.execute("UPDATE service_requests SET service_status = 'closed', rating = ?, review = ? WHERE id = ?", (rating, review, request_id))
        conn.commit()
        return jsonify({"success": True, "message": "Request accepted successfully", "code": 200}), 200
    
    except sqlite3.Error as e:
        return jsonify({"success": False, "error": "Database error", "message": str(e), "code": 500}), 500
    except Exception as e:
        return jsonify({"success": False, "error": "Database error", "message": str(e), "code": 500}), 500
    finally:
        conn.close()

@app.route('/update-service-request/<int:request_id>', methods = ['PUT'])
def update_service_request(request_id):
    user_id, user_type = session.get('user_id'), session.get('user_type')

    if user_type != 'customer' and user_type != 'professional':
        return jsonify({"success": False, "error": "Unauthorized", "message": "Login to update", "code": 403}), 403

    data = request.get_json()
    service_price = data['service_price']
    service_date = data['service_date']
    service_description = data['service_description']
    quote = data['quote']

    if not service_date or not service_description:
        return jsonify({"success": False, "error": "Invalid input", "message": "Service date, description and price are required", "code": 400}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "SELECT * FROM service_requests WHERE id = ? AND (customer_id = ? or professional_id = ?) AND service_status != 'assigned' AND service_status != 'closed'", 
            (request_id,user_id, user_id)
        )
        service_request = cursor.fetchone()

        if not service_request:
            return jsonify({"success": False, "error": "Request not found", "message": "Request not found or unauthorized", "code": 404}), 404

        service_date_obj = datetime.strptime(service_date, '%Y-%m-%d')
        current_date = datetime.now().date()

        if service_date_obj.date() < current_date:
            return jsonify({"success": False, "error": "Invalid date", "message": "Service date cannot be before the current date", "code": 400}), 400

        cursor.execute("""
            UPDATE service_requests
            SET date_of_service = ?, service_description = ?, price = ?
            WHERE id = ?
        """, (service_date, service_description, service_price, request_id))

        if quote:
            cursor.execute("""
                UPDATE service_requests
                SET service_status = 'quoted'
                WHERE id = ?
            """, (request_id,))
        
        conn.commit()
        return jsonify({"success": True, "message": "Request updated successfully", "code": 200}), 200

    except sqlite3.Error as e:
        return jsonify({"success": False, "error": "Database error", "message": str(e), "code": 500}), 500
    
    finally:
        conn.close()

@app.route('/admin/professionals', methods=['GET'])
def admin_get_professionals():
    user_id, user_type = session.get('user_id'), session.get('user_type')

    if user_type != 'admin':
        return jsonify({"success": False, "error": "Unauthorized", "message": "Admin access required", "code": 403}), 403

    conn = get_db_connection()
    try:
        professionals = conn.execute("""
            SELECT 
                p.credential_id AS id,
                p.full_name,
                p.service_provided,
                p.pincode,
                p.experience,
                p.phone,
                p.verified,
                cr.email,
                cr.username
            FROM professionals p
            JOIN credentials cr ON p.credential_id = cr.id
        """).fetchall()

        if not professionals:
            return jsonify({"success": False, "message": "No professionals found", "code": 404}), 404

        professionals_list = [dict(professional) for professional in professionals]
        return jsonify(professionals_list), 200

    except sqlite3.Error as e:
        return jsonify({"success": False, "error": "Database error", "message": str(e), "code": 500}), 500

    finally:
        conn.close()

@app.route('/admin/customers', methods=['GET'])
def admin_get_customers():
    user_id, user_type = session.get('user_id'), session.get('user_type')

    if user_type != 'admin':
        return jsonify({"success": False, "error": "Unauthorized", "message": "Admin access required", "code": 403}), 403

    conn = get_db_connection()
    try:
        customers = conn.execute("""
            SELECT 
                c.credential_id AS id,
                c.full_name,
                c.address,
                c.pincode,
                c.phone,
                cr.email,
                cr.username
            FROM customers c
            JOIN credentials cr ON c.credential_id = cr.id
        """).fetchall()

        if not customers:
            return jsonify({"success": False, "message": "No customers found", "code": 404}), 404

        customers_list = [dict(customer) for customer in customers]
        return jsonify(customers_list), 200

    except sqlite3.Error as e:
        return jsonify({"success": False, "error": "Database error", "message": str(e), "code": 500}), 500

    finally:
        conn.close()

@app.route('/admin/professional/<int:professional_id>', methods=['GET'])
def admin_get_professional(professional_id):
    user_id, user_type = session.get('user_id'), session.get('user_type')

    if user_type != 'admin':
        return jsonify({"success": False, "error": "Unauthorized", "message": "Admin access required", "code": 403}), 403

    conn = get_db_connection()
    try:
        professional = conn.execute("""
            SELECT 
                p.credential_id AS id,
                p.full_name,
                p.service_provided,
                p.pincode,
                p.experience,
                p.phone,
                p.verified,
                cr.email,
                cr.username,
                (SELECT AVG(sr.rating) 
                    FROM service_requests sr 
                    WHERE sr.professional_id = p.credential_id 
                    AND sr.service_status = 'closed') AS average_rating,
                cr.blocked,
                p.documents
            FROM professionals p
            JOIN credentials cr ON p.credential_id = cr.id
            WHERE p.credential_id = ?
        """, (professional_id,)).fetchone()

        if not professional:
            return jsonify({"success": False, "message": "Professional not found", "code": 404}), 404

        service_requests = conn.execute("""
            SELECT sr.id, sr.service_id, sr.customer_id, sr.price, sr.service_status, sr.date_of_service, sr.service_description, sr.rating, sr.review, c.full_name, c.pincode, c.address, c.phone
            FROM service_requests sr
            JOIN customers as c 
            ON c.credential_id = sr.customer_id
            WHERE sr.professional_id = ?
        """, (professional_id,)).fetchall()

        professional_details = dict(professional)
        service_requests_list = [dict(request) for request in service_requests]

        return jsonify({"success": True, "professional": professional_details, "service_requests": service_requests_list, "code": 200}), 200

    except sqlite3.Error as e:
        return jsonify({"success": False, "error": "Database error", "message": str(e), "code": 500}), 500

    finally:
        conn.close()

@app.route('/admin/customer/<int:customer_id>', methods=['GET'])
def admin_get_customer(customer_id):
    user_id, user_type = session.get('user_id'), session.get('user_type')

    if user_type != 'admin':
        return jsonify({"success": False, "error": "Unauthorized", "message": "Admin access required", "code": 403}), 403

    conn = get_db_connection()
    try:
        customer = conn.execute("""
            SELECT 
                c.credential_id AS id,
                c.full_name,
                c.address,
                c.pincode,
                c.phone,
                cr.email,
                cr.username,
                cr.blocked
            FROM customers c
            JOIN credentials cr ON c.credential_id = cr.id
            WHERE c.credential_id = ?
        """, (customer_id,)).fetchone()

        if not customer:
            return jsonify({"success": False, "message": "Customer not found", "code": 404}), 404

        service_requests = conn.execute("""
            SELECT sr.id, sr.service_id, sr.professional_id, sr.price, sr.service_status, sr.date_of_service, sr.service_description, sr.rating, sr.review, p.full_name, p.pincode, p.phone
            FROM service_requests sr            
            JOIN professionals as p
            ON p.credential_id = sr.professional_id
            WHERE sr.customer_id = ?
        """, (customer_id,)).fetchall()

        customer_details = dict(customer)
        service_requests_list = [dict(request) for request in service_requests]

        return jsonify({"success": True, "customer": customer_details, "service_requests": service_requests_list, "code": 200}), 200

    except sqlite3.Error as e:
        return jsonify({"success": False, "error": "Database error", "message": str(e), "code": 500}), 500

    finally:
        conn.close()

@app.route('/admin/delete-service-request/<int:request_id>', methods=['DELETE'])
def admin_delete_service_request(request_id):
    user_id, user_type = session.get('user_id'), session.get('user_type')

    if user_type != 'admin':
        return jsonify({"success": False, "error": "Unauthorized", "message": "Admin access required", "code": 403}), 403

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM service_requests WHERE id = ?", (request_id,))
        request = cursor.fetchone()

        if not request:
            return jsonify({"success": False, "error": "Request not found", "message": "Request not found", "code": 404}), 404

        cursor.execute("DELETE FROM service_requests WHERE id = ?", (request_id,))
        conn.commit()
        return jsonify({"success": True, "message": "Request deleted successfully", "code": 200}), 200

    except sqlite3.Error as e:
        return jsonify({"success": False, "error": "Database error", "message": str(e), "code": 500}), 500

    finally:
        conn.close()

@app.route('/admin/block-user/<int:user_id>', methods=['PUT'])
def admin_block_user(user_id):
    admin_id, user_type = session.get('user_id'), session.get('user_type')

    if user_type != 'admin':
        return jsonify({"success": False, "error": "Unauthorized", "message": "Admin access required", "code": 403}), 403

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM credentials WHERE id = ?", (user_id,))
        user = cursor.fetchone()

        if not user:
            return jsonify({"success": False, "error": "User not found", "message": "User not found", "code": 404}), 404

        # Block the user
        cursor.execute("UPDATE credentials SET blocked = 1 WHERE id = ?", (user_id,))
        conn.commit()

        # Get user email
        user_email = user['email']  # Ensure your database returns the email

        # Send email notification
        email_result = send_email(
            to_email=user_email,
            subject='Account Blocked Notification',
            text='Your account has been blocked by an admin. If you believe this is an error, please contact support.'
        )

        return jsonify({"success": True, "message": "User blocked successfully", "email_status": email_result}), 200

    except sqlite3.Error as e:
        return jsonify({"success": False, "error": "Database error", "message": str(e), "code": 500}), 500

    finally:
        conn.close()

@app.route('/admin/unblock-user/<int:user_id>', methods=['PUT'])
def admin_unblock_user(user_id):
    admin_id, user_type = session.get('user_id'), session.get('user_type')

    if user_type != 'admin':
        return jsonify({"success": False, "error": "Unauthorized", "message": "Admin access required", "code": 403}), 403

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM credentials WHERE id = ?", (user_id,))
        user = cursor.fetchone()

        if not user:
            return jsonify({"success": False, "error": "User not found", "message": "User not found", "code": 404}), 404

        cursor.execute("UPDATE credentials SET blocked = 0 WHERE id = ?", (user_id,))
        conn.commit()

        # Get user email
        user_email = user['email']  # Ensure your database returns the email

        # Send email notification
        email_result = send_email(
            to_email=user_email,
            subject='Account Unblocked Notification',
            text='Your account has been unblocked. You can now log in.'
        )

        return jsonify({"success": True, "message": "User unblocked successfully", "email_status": email_result}), 200

    except sqlite3.Error as e:
        return jsonify({"success": False, "error": "Database error", "message": str(e), "code": 500}), 500

    finally:
        conn.close()

@app.route('/admin/verify-professional/<int:professional_id>', methods=['PUT'])
def verify_professional(professional_id):
    admin_id, user_type = session.get('user_id'), session.get('user_type')

    if user_type != 'admin':
        return jsonify({"success": False, "error": "Unauthorized", "message": "Admin access required", "code": 403}), 403

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM credentials WHERE id = ? and userType = 'professional'", (professional_id,))
        professional = cursor.fetchone()

        if not professional:
            return jsonify({"success": False, "error": "Professional not found", "message": "Professional not found", "code": 404}), 404
        
        # Update verification status
        cursor.execute("UPDATE professionals SET verified = 1 WHERE credential_id = ?", (professional_id,))
        conn.commit()

        # Get professional email (assuming it's stored in the professionals table)
        professional_email = professional['email']  # Adjust this based on your schema

        # Send email notification
        email_result = send_email(
            to_email=professional_email,
            subject='Professional Profile Verified',
            text='Congratulations! Your professional profile has been successfully verified.'
        )

        return jsonify({"success": True, "message": "Professional verified successfully", "email_status": email_result}), 200

    except sqlite3.Error as e:
        return jsonify({"success": False, "error": "Database error", "message": str(e), "code": 500}), 500

    finally:
        conn.close()

@app.route('/admin/update-service-price/<int:service_id>', methods=['PUT'])
def update_service_price(service_id):
    user_id, user_type = session.get('user_id'), session.get('user_type')

    if user_type != 'admin':
        return jsonify({"success": False, "error": "Unauthorized", "message": "Admin access required", "code": 403}), 403

    data = request.get_json()
    new_price = data.get('new_price')
    new_description = data.get('new_description')

    if new_price is None:
        return jsonify({"success": False, "error": "Invalid input", "message": "New price is required", "code": 400}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM services WHERE id = ?", (service_id,))
        service = cursor.fetchone()

        if not service:
            return jsonify({"success": False, "error": "Service not found", "message": "Service not found", "code": 404}), 404

        cursor.execute("UPDATE services SET price = ?, description = ? WHERE id = ?", (new_price, new_description, service_id))
        conn.commit()
        return jsonify({"success": True, "message": "Service price updated successfully", "code": 200}), 200

    except sqlite3.Error as e:
        return jsonify({"success": False, "error": "Database error", "message": str(e), "code": 500}), 500

    finally:
        conn.close()

@app.route('/admin/create-service', methods=['POST'])
def create_service():
    user_id, user_type = session.get('user_id'), session.get('user_type')

    if user_type != 'admin':
        return jsonify({"success": False, "error": "Unauthorized", "message": "Admin access required", "code": 403}), 403

    data = request.get_json()
    service_name = data.get('name')
    service_price = data.get('price')
    description = data.get('description')

    if not service_name or service_price is None:
        return jsonify({"success": False, "error": "Invalid input", "message": "Service name and price are required", "code": 400}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM services WHERE name = ?", (service_name,))
        existing_service = cursor.fetchone()

        if existing_service:
            return jsonify({"success": False, "error": "Service already exists", "message": "A service with this name already exists", "code": 409}), 409

        cursor.execute("INSERT INTO services (name, price, description) VALUES (?, ?, ?)", (service_name, service_price, description))
        conn.commit()
        return jsonify({"success": True, "message": "Service created successfully", "code": 201}), 201

    except sqlite3.Error as e:
        return jsonify({"success": False, "error": "Database error", "message": str(e), "code": 500}), 500

    finally:
        conn.close()

if __name__ == "__main__":
    app.run(debug=True)
    celery.start()
