from functools import wraps
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
import jwt
import config
from flask_cors import CORS
from flask_migrate import Migrate
from models import User, Domain, SSLInfo, UptimeEvent, DomainExpiry, db
from urllib.parse import urlparse

from monitor import get_ssl_info, check_website, get_domain_expiry, send_email


app = Flask(__name__)
app.config.from_object(config)


app.config["SECRET_KEY"] = "your-secret-key"


db.init_app(app)
migrate = Migrate(app, db)
ALERT_SSL_DAYS_LEFT = 7


# ---------------------------
# JWT Auth Decorator
# ---------------------------
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split(" ")[-1]

        if not token:
            return jsonify({"error": "Token is missing!"}), 401

        try:
            data = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            current_user = User.query.get(data["user_id"])
            if not current_user:
                raise Exception("User not found")
        except Exception as e:
            return jsonify({"error": "Invalid or expired token"}), 401

        return f(current_user, *args, **kwargs)

    return decorated


CORS(app, resources={r"/*": {"origins": "*"}})


@app.route("/")
def index():
    return ""


# ---------------------------
# Register
# ---------------------------
@app.route("/auth/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    phone_number = data.get("phone_number")
    password = data.get("password")

    if not all([username, email, password]):
        return jsonify({"error": "Username, email, and password are required"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 409

    new_user = User(
        username=username,
        email=email,
        phone_number=phone_number,
    )
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201


# ---------------------------
# Login (returns JWT)
# ---------------------------
@app.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not all([email, password]):
        return jsonify({"error": "Email and password are required"}), 400

    user = User.query.filter_by(email=email).first()
    if user and user.check_password(password):
        token = jwt.encode(
            {
                "user_id": user.id,
                "exp": datetime.utcnow() + timedelta(hours=2),
            },
            app.config["SECRET_KEY"],
            algorithm="HS256",
        )

        return jsonify(
            {
                "message": "Login successful",
                "token": token,
                "user": {"id": user.id, "username": user.username, "email": user.email},
            }
        )

    return jsonify({"error": "Invalid email or password"}), 401


@app.route("/user/profile", methods=["GET"])
@token_required
def get_profile(current_user):
    profile_data = {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "phone_number": current_user.phone_number,
    }

    return jsonify(profile_data), 200


@app.route("/target", methods=["POST"])
@token_required
def add_domain(current_user):
    data = request.get_json()
    name = data.get("name")
    url = data.get("url")

    if not all([name, url]):
        return jsonify({"error": "Name and URL required"}), 400

    # ✅ Block if user already has at least one domain
    existing_domain = Domain.query.filter_by(user_id=current_user.id).first()
    if existing_domain:
        return jsonify({"error": "You can only add one domain."}), 403  # Forbidden

    # Save new domain
    domain = Domain(name=name, url=url, user_id=current_user.id)
    db.session.add(domain)
    db.session.commit()

    return jsonify({"message": "Domain added", "domain_id": domain.id}), 201


@app.route("/target", methods=["GET"])
@token_required
def list_domains(current_user):
    domains = Domain.query.filter_by(user_id=current_user.id).all()
    result = [{"id": d.id, "name": d.name, "url": d.url} for d in domains]
    return jsonify(result)


@app.route("/history/ssl/<int:domain_id>", methods=["GET"])
@token_required
def check_ssl(current_user, domain_id):
    domain = Domain.query.filter_by(id=domain_id, user_id=current_user.id).first()
    if not domain:
        return jsonify({"error": "Domain not found"}), 404

    hostname = urlparse(domain.url).hostname
    ssl_data = get_ssl_info(hostname)

    if "error" in ssl_data:
        return jsonify({"error": ssl_data["error"]}), 500

    # Store or update SSLInfo
    ssl_info = SSLInfo.query.filter_by(domain_id=domain.id).first()
    if not ssl_info:
        ssl_info = SSLInfo(domain_id=domain.id)
    ssl_info.start_date = ssl_data["valid_from"]
    ssl_info.expiration_date = ssl_data["valid_until"]

    db.session.add(ssl_info)
    db.session.commit()

    return jsonify(
        {
            "start_date": ssl_data["valid_from"].isoformat(),
            "expiration_date": ssl_data["valid_until"].isoformat(),
        }
    )


@app.route("/monitor/uptime/<int:domain_id>", methods=["GET"])
@token_required
def check_uptime(current_user, domain_id):
    domain = Domain.query.filter_by(id=domain_id, user_id=current_user.id).first()
    if not domain:
        return jsonify({"error": "Domain not found"}), 404

    uptime_info = check_website(domain.url)

    # Log uptime status in DB
    response_code = uptime_info.get("response_time_ms")
    status = uptime_info.get("status", "DOWN")
    log = UptimeEvent(
        domain_id=domain.id,
        status=status,
        response_time=response_code,
        checked_at=datetime.utcnow(),
    )
    db.session.add(log)
    db.session.commit()

    return jsonify(uptime_info)


@app.route("/monitor/expiry/<int:domain_id>", methods=["GET"])
@token_required
def check_expiry(current_user, domain_id):
    domain = Domain.query.filter_by(id=domain_id, user_id=current_user.id).first()
    if not domain:
        return jsonify({"error": "Domain not found"}), 404

    hostname = urlparse(domain.url).hostname
    expiry_date = get_domain_expiry(hostname)

    if isinstance(expiry_date, str) and expiry_date.startswith("WHOIS failed"):
        return jsonify({"error": expiry_date}), 500

    if not expiry_date:
        return (
            jsonify(
                {"error": "WHOIS did not return an expiration date for this domain"}
            ),
            404,
        )

    # Handle list or datetime directly here
    if isinstance(expiry_date, list):
        expiry_date = expiry_date[0]  # Take the first element if it's a list

    # Convert to string if datetime object
    if isinstance(expiry_date, datetime):
        expiry_date_str = expiry_date.strftime("%Y-%m-%d")
    else:
        expiry_date_str = str(expiry_date)

    expiry_record = DomainExpiry.query.filter_by(domain_id=domain.id).first()
    if not expiry_record:
        expiry_record = DomainExpiry(domain_id=domain.id)

    expiry_record.expiration_date = expiry_date_str
    db.session.add(expiry_record)
    db.session.commit()

    return jsonify({"expiration_date": expiry_date_str})


@app.route("/history/all/<int:domain_id>", methods=["GET"])
@token_required
def full_monitor(current_user, domain_id):
    ssl_resp = check_ssl(current_user, domain_id)
    uptime_resp = check_uptime(current_user, domain_id)
    expiry_resp = check_expiry(current_user, domain_id)

    # If these are Response objects, get their JSON content
    ssl_data = ssl_resp.get_json() if hasattr(ssl_resp, "get_json") else ssl_resp
    uptime_data = (
        uptime_resp.get_json() if hasattr(uptime_resp, "get_json") else uptime_resp
    )
    expiry_data = (
        expiry_resp.get_json() if hasattr(expiry_resp, "get_json") else expiry_resp
    )

    return jsonify({"ssl": ssl_data, "uptime": uptime_data, "expiry": expiry_data})


@app.route("/history/<int:domain_id>", methods=["GET"])
@token_required
def run_monitoring(current_user, domain_id):
    domain = Domain.query.filter_by(id=domain_id, user_id=current_user.id).first()
    print(domain)
    if not domain:
        return jsonify({"error": "Domain not found"}), 404

    url = domain.url
    parsed_url = urlparse(url)
    hostname = parsed_url.hostname

    status = check_website(url)

    # If website is DOWN, send alert and return JSON immediately
    if status.get("status") == "DOWN":
        msg = f"Website {url} is currently not reachable."
        send_email(f"ALERT: {url} is DOWN", msg)

        return (
            jsonify(
                {
                    "url": url,
                    "monitoring_status": status,
                    "ssl_info": None,
                    "domain_expiry": None,
                    "alerts_triggered": ["Website is DOWN - alert email sent."],
                    "log_saved": True,
                }
            ),
            200,
        )

    # Continue normal checks if site is up
    ssl_info = get_ssl_info(hostname)
    domain_expiry = get_domain_expiry(hostname)

    alerts = []
    if isinstance(ssl_info.get("valid_until"), datetime):
        days_left = (ssl_info["valid_until"] - datetime.utcnow()).days
        if days_left < ALERT_SSL_DAYS_LEFT:
            msg = f"The SSL certificate for {hostname} expires in {days_left} days."
            send_email(f"ALERT: SSL Expiring Soon for {hostname}", msg)
            alerts.append(f"SSL expires in {days_left} days - alert email sent.")

    return jsonify(
        {
            "url": url,
            "monitoring_status": status,
            "ssl_info": {
                "valid_from": str(ssl_info.get("valid_from")),
                "valid_until": str(ssl_info.get("valid_until")),
                "issuer": ssl_info.get("issuer"),
            },
            "domain_expiry": str(domain_expiry),
            "alerts_triggered": alerts,
            "log_saved": True,
        }
    )


if __name__ == "__main__":
    app.run(debug=True)
