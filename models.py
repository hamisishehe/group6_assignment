from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


db = SQLAlchemy()


# ----------------------------
# User Model
# ----------------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone_number = db.Column(db.String(14))
    password_hash = db.Column(db.Text(), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    domains = db.relationship("Domain", backref="user", lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# ----------------------------
# Domain Model
# ----------------------------
class Domain(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    ssl_info = db.relationship("SSLInfo", backref="domain", uselist=False)
    uptime_events = db.relationship("UptimeEvent", backref="domain", lazy=True)
    expiry_info = db.relationship("DomainExpiry", backref="domain", uselist=False)


# ----------------------------
# SSL Certificate Info
# ----------------------------
class SSLInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    domain_id = db.Column(db.Integer, db.ForeignKey("domain.id"), nullable=False)
    issuer = db.Column(db.String(255))
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    days_remaining = db.Column(db.Integer)
    last_checked = db.Column(db.DateTime, default=datetime.utcnow)


# ----------------------------
# Uptime / Downtime Events
# ----------------------------
class UptimeEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    domain_id = db.Column(db.Integer, db.ForeignKey("domain.id"), nullable=False)
    status = db.Column(db.String(50))  # "UP" or "DOWN"
    response_time = db.Column(db.Float)
    checked_at = db.Column(db.DateTime, default=datetime.utcnow)


# ----------------------------
# Domain Expiry Info (Whois)
# ----------------------------
class DomainExpiry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    domain_id = db.Column(db.Integer, db.ForeignKey("domain.id"), nullable=False)
    registrar = db.Column(db.String(255))
    creation_date = db.Column(db.DateTime)
    expiration_date = db.Column(db.DateTime)
    last_checked = db.Column(db.DateTime, default=datetime.utcnow)
