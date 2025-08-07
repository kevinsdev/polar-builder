from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import jwt
import os

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    boats = db.relationship('Boat', backref='owner', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)

    def generate_token(self):
        """Generate JWT token for authentication"""
        payload = {
            'user_id': self.id,
            'username': self.username,
            'exp': datetime.utcnow().timestamp() + 86400  # 24 hours
        }
        return jwt.encode(payload, os.environ.get('SECRET_KEY', 'default-secret'), algorithm='HS256')

    @staticmethod
    def verify_token(token):
        """Verify JWT token and return user"""
        try:
            payload = jwt.decode(token, os.environ.get('SECRET_KEY', 'default-secret'), algorithms=['HS256'])
            return User.query.get(payload['user_id'])
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'name': self.name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'boat_count': len(self.boats)
        }

class Boat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    boat_type = db.Column(db.String(50), nullable=False)  # monohull, catamaran, trimaran
    class_name = db.Column(db.String(100))
    year_built = db.Column(db.Integer)
    
    # Specifications
    loa = db.Column(db.Float)  # Length Overall
    lwl = db.Column(db.Float)  # Length Waterline
    beam = db.Column(db.Float)
    draft = db.Column(db.Float)
    displacement = db.Column(db.Float)
    sail_area = db.Column(db.Float)
    
    # Configuration
    keel_type = db.Column(db.String(50))
    rig_type = db.Column(db.String(50))
    hull_material = db.Column(db.String(50))
    
    # Racing Information
    rating_system = db.Column(db.String(50))
    rating_value = db.Column(db.String(50))
    crew_size = db.Column(db.Integer)
    
    # Metadata
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    log_files = db.relationship('LogFile', backref='boat', lazy=True, cascade='all, delete-orphan')
    polars = db.relationship('Polar', backref='boat', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Boat {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'boat_type': self.boat_type,
            'class_name': self.class_name,
            'year_built': self.year_built,
            'loa': self.loa,
            'lwl': self.lwl,
            'beam': self.beam,
            'draft': self.draft,
            'displacement': self.displacement,
            'sail_area': self.sail_area,
            'keel_type': self.keel_type,
            'rig_type': self.rig_type,
            'hull_material': self.hull_material,
            'rating_system': self.rating_system,
            'rating_value': self.rating_value,
            'crew_size': self.crew_size,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'log_file_count': len(self.log_files),
            'polar_count': len(self.polars)
        }

class LogFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    boat_id = db.Column(db.Integer, db.ForeignKey('boat.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer)
    
    # Data Statistics
    raw_data_points = db.Column(db.Integer)
    clean_data_points = db.Column(db.Integer)
    wind_range_min = db.Column(db.Float)
    wind_range_max = db.Column(db.Float)
    angle_range_min = db.Column(db.Float)
    angle_range_max = db.Column(db.Float)
    speed_range_min = db.Column(db.Float)
    speed_range_max = db.Column(db.Float)
    
    # Processing Status
    processing_status = db.Column(db.String(50), default='pending')  # pending, processing, completed, error
    processing_error = db.Column(db.Text)
    
    # Metadata
    session_notes = db.Column(db.Text)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    processed_date = db.Column(db.DateTime)

    def __repr__(self):
        return f'<LogFile {self.filename}>'

    def to_dict(self):
        return {
            'id': self.id,
            'boat_id': self.boat_id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_size': self.file_size,
            'raw_data_points': self.raw_data_points,
            'clean_data_points': self.clean_data_points,
            'wind_range': [self.wind_range_min, self.wind_range_max] if self.wind_range_min is not None else None,
            'angle_range': [self.angle_range_min, self.angle_range_max] if self.angle_range_min is not None else None,
            'speed_range': [self.speed_range_min, self.speed_range_max] if self.speed_range_min is not None else None,
            'processing_status': self.processing_status,
            'processing_error': self.processing_error,
            'session_notes': self.session_notes,
            'upload_date': self.upload_date.isoformat() if self.upload_date else None,
            'processed_date': self.processed_date.isoformat() if self.processed_date else None
        }

class Polar(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    boat_id = db.Column(db.Integer, db.ForeignKey('boat.id'), nullable=False)
    version = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(100))
    
    # Polar Data
    polar_data = db.Column(db.Text)  # Store the actual polar content
    data_summary = db.Column(db.Text)  # Store summary information
    file_url = db.Column(db.String(500))  # Cloud storage URL
    
    # Generation info
    generation_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Statistics
    total_data_points = db.Column(db.Integer)
    sessions_used = db.Column(db.Integer)
    wind_bins_with_data = db.Column(db.Integer)
    angle_speed_pairs = db.Column(db.Integer)
    
    # Coverage
    wind_range_min = db.Column(db.Float)
    wind_range_max = db.Column(db.Float)
    angle_coverage = db.Column(db.String(100))
    
    # Metadata
    generated_date = db.Column(db.DateTime, default=datetime.utcnow)
    is_current = db.Column(db.Boolean, default=True)
    notes = db.Column(db.Text)

    def __repr__(self):
        return f'<Polar {self.boat.name} v{self.version}>'

    def to_dict(self):
        return {
            'id': self.id,
            'boat_id': self.boat_id,
            'version': self.version,
            'name': self.name,
            'polar_data': self.polar_data,
            'data_quality': self.data_quality,
            'total_data_points': self.total_data_points,
            'sessions_used': self.sessions_used,
            'wind_bins_with_data': self.wind_bins_with_data,
            'angle_speed_pairs': self.angle_speed_pairs,
            'wind_range': [self.wind_range_min, self.wind_range_max] if self.wind_range_min is not None else None,
            'angle_coverage': self.angle_coverage,
            'generated_date': self.generated_date.isoformat() if self.generated_date else None,
            'is_current': self.is_current,
            'notes': self.notes
        }

