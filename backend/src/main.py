import os
import logging
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import jwt
import bcrypt
import boto3
from botocore.exceptions import ClientError
from werkzeug.utils import secure_filename
import tempfile
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'polar-builder-secret-key-2024')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://polaruser:polarpass123@database:5432/polarbuilder')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
CORS(app)

# AWS S3 Configuration
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_BUCKET_NAME = os.environ.get('AWS_BUCKET_NAME', 'polar-builder-files')
AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')

# Initialize S3 client
s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

# Database Models
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    full_name = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    boats = db.relationship('Boat', backref='user', lazy=True, cascade='all, delete-orphan')

class Boat(db.Model):
    __tablename__ = 'boats'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    boat_type = db.Column(db.String(50), nullable=False)
    class_design = db.Column(db.String(100))
    year_built = db.Column(db.Integer)
    loa = db.Column(db.Float)
    lwl = db.Column(db.Float)
    beam = db.Column(db.Float)
    draft = db.Column(db.Float)
    displacement = db.Column(db.Float)
    sail_area = db.Column(db.Float)
    keel_type = db.Column(db.String(50))
    rig_type = db.Column(db.String(50))
    hull_material = db.Column(db.String(50))
    crew_size = db.Column(db.Integer)
    rating_system = db.Column(db.String(50))
    rating_value = db.Column(db.String(50))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    log_files = db.relationship('LogFile', backref='boat', lazy=True, cascade='all, delete-orphan')
    polars = db.relationship('Polar', backref='boat', lazy=True, cascade='all, delete-orphan')

class LogFile(db.Model):
    __tablename__ = 'log_files'
    
    id = db.Column(db.Integer, primary_key=True)
    boat_id = db.Column(db.Integer, db.ForeignKey('boats.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    s3_key = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    processed = db.Column(db.Boolean, default=False)
    processing_status = db.Column(db.String(50), default='pending')

class Polar(db.Model):
    __tablename__ = 'polars'
    
    id = db.Column(db.Integer, primary_key=True)
    boat_id = db.Column(db.Integer, db.ForeignKey('boats.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    s3_key = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    log_files_used = db.Column(db.Text)  # JSON string of log file IDs used

# Utility functions
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(password, password_hash):
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

def generate_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

def verify_token(token):
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def token_required(f):
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        if token.startswith('Bearer '):
            token = token[7:]
        
        user_id = verify_token(token)
        if not user_id:
            return jsonify({'message': 'Token is invalid or expired'}), 401
        
        current_user = User.query.get(user_id)
        if not current_user:
            return jsonify({'message': 'User not found'}), 401
        
        return f(current_user, *args, **kwargs)
    
    decorated.__name__ = f.__name__
    return decorated

# Routes
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()}), 200

@app.route('/api/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        if not all(k in data for k in ['username', 'email', 'password', 'full_name']):
            return jsonify({'message': 'Missing required fields'}), 400
        
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'message': 'Username already exists'}), 409
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'message': 'Email already exists'}), 409
        
        user = User(
            username=data['username'],
            email=data['email'],
            password_hash=hash_password(data['password']),
            full_name=data['full_name']
        )
        
        db.session.add(user)
        db.session.commit()
        
        token = generate_token(user.id)
        
        return jsonify({
            'message': 'User created successfully',
            'token': token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'full_name': user.full_name
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Registration error: {str(e)}")
        return jsonify({'message': 'Registration failed', 'error': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data.get('username') or not data.get('password'):
            return jsonify({'message': 'Username and password are required'}), 400
        
        user = User.query.filter_by(username=data['username']).first()
        
        if not user or not check_password(data['password'], user.password_hash):
            return jsonify({'message': 'Invalid credentials'}), 401
        
        token = generate_token(user.id)
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'full_name': user.full_name
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'message': 'Login failed', 'error': str(e)}), 500

@app.route('/api/boats', methods=['GET'])
@token_required
def get_boats(current_user):
    try:
        boats = Boat.query.filter_by(user_id=current_user.id).all()
        
        boats_data = []
        for boat in boats:
            boats_data.append({
                'id': boat.id,
                'name': boat.name,
                'boat_type': boat.boat_type,
                'class_design': boat.class_design,
                'year_built': boat.year_built,
                'created_at': boat.created_at.isoformat(),
                'log_files_count': len(boat.log_files),
                'polars_count': len(boat.polars)
            })
        
        return jsonify({'boats': boats_data}), 200
        
    except Exception as e:
        logger.error(f"Get boats error: {str(e)}")
        return jsonify({'message': 'Failed to retrieve boats', 'error': str(e)}), 500

@app.route('/api/boats/<int:boat_id>', methods=['GET'])
@token_required
def get_boat(current_user, boat_id):
    try:
        boat = Boat.query.filter_by(id=boat_id, user_id=current_user.id).first()
        
        if not boat:
            return jsonify({'message': 'Boat not found'}), 404
        
        boat_data = {
            'id': boat.id,
            'name': boat.name,
            'boat_type': boat.boat_type,
            'class_design': boat.class_design,
            'year_built': boat.year_built,
            'loa': boat.loa,
            'lwl': boat.lwl,
            'beam': boat.beam,
            'draft': boat.draft,
            'displacement': boat.displacement,
            'sail_area': boat.sail_area,
            'keel_type': boat.keel_type,
            'rig_type': boat.rig_type,
            'hull_material': boat.hull_material,
            'crew_size': boat.crew_size,
            'rating_system': boat.rating_system,
            'rating_value': boat.rating_value,
            'notes': boat.notes,
            'created_at': boat.created_at.isoformat(),
            'updated_at': boat.updated_at.isoformat(),
            'log_files': [{
                'id': lf.id,
                'filename': lf.original_filename,
                'upload_date': lf.upload_date.isoformat(),
                'processed': lf.processed,
                'processing_status': lf.processing_status,
                'file_size': lf.file_size
            } for lf in boat.log_files],
            'polars': [{
                'id': p.id,
                'name': p.name,
                'created_at': p.created_at.isoformat()
            } for p in boat.polars]
        }
        
        return jsonify({'boat': boat_data}), 200
        
    except Exception as e:
        logger.error(f"Get boat error: {str(e)}")
        return jsonify({'message': 'Failed to retrieve boat', 'error': str(e)}), 500

@app.route('/api/boats', methods=['POST'])
@token_required
def create_boat(current_user):
    try:
        data = request.get_json()
        
        if not data.get('name') or not data.get('boat_type'):
            return jsonify({'message': 'Boat name and type are required'}), 400
        
        boat = Boat(
            user_id=current_user.id,
            name=data['name'],
            boat_type=data['boat_type'],
            class_design=data.get('class_design'),
            year_built=data.get('year_built'),
            loa=data.get('loa'),
            lwl=data.get('lwl'),
            beam=data.get('beam'),
            draft=data.get('draft'),
            displacement=data.get('displacement'),
            sail_area=data.get('sail_area'),
            keel_type=data.get('keel_type'),
            rig_type=data.get('rig_type'),
            hull_material=data.get('hull_material'),
            crew_size=data.get('crew_size'),
            rating_system=data.get('rating_system'),
            rating_value=data.get('rating_value'),
            notes=data.get('notes')
        )
        
        db.session.add(boat)
        db.session.commit()
        
        return jsonify({
            'message': 'Boat created successfully',
            'boat': {
                'id': boat.id,
                'name': boat.name,
                'boat_type': boat.boat_type,
                'created_at': boat.created_at.isoformat()
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Create boat error: {str(e)}")
        return jsonify({'message': 'Failed to create boat', 'error': str(e)}), 500

@app.route('/api/boats/<int:boat_id>/upload', methods=['POST'])
@token_required
def upload_log_files(current_user, boat_id):
    try:
        boat = Boat.query.filter_by(id=boat_id, user_id=current_user.id).first()
        
        if not boat:
            return jsonify({'message': 'Boat not found'}), 404
        
        if 'files' not in request.files:
            return jsonify({'message': 'No files provided'}), 400
        
        files = request.files.getlist('files')
        uploaded_files = []
        
        for file in files:
            if file.filename == '':
                continue
                
            if not file.filename.lower().endswith(('.csv', '.txt', '.log')):
                return jsonify({'message': f'Invalid file type: {file.filename}. Only CSV, TXT, and LOG files are allowed.'}), 400
            
            # Generate unique filename
            file_extension = file.filename.rsplit('.', 1)[1].lower()
            unique_filename = f"{uuid.uuid4()}.{file_extension}"
            s3_key = f"boats/{boat_id}/logs/{unique_filename}"
            
            # Upload to S3
            try:
                s3_client.upload_fileobj(
                    file,
                    AWS_BUCKET_NAME,
                    s3_key,
                    ExtraArgs={'ContentType': file.content_type or 'application/octet-stream'}
                )
                
                # Get file size
                file.seek(0, 2)  # Seek to end
                file_size = file.tell()
                file.seek(0)  # Reset to beginning
                
                # Save to database
                log_file = LogFile(
                    boat_id=boat_id,
                    filename=unique_filename,
                    original_filename=secure_filename(file.filename),
                    s3_key=s3_key,
                    file_size=file_size,
                    processing_status='uploaded'
                )
                
                db.session.add(log_file)
                uploaded_files.append({
                    'id': log_file.id,
                    'filename': log_file.original_filename,
                    'size': file_size
                })
                
            except ClientError as e:
                logger.error(f"S3 upload error: {str(e)}")
                return jsonify({'message': f'Failed to upload {file.filename}', 'error': str(e)}), 500
        
        db.session.commit()
        
        return jsonify({
            'message': f'Successfully uploaded {len(uploaded_files)} files',
            'files': uploaded_files
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Upload error: {str(e)}")
        return jsonify({'message': 'Upload failed', 'error': str(e)}), 500

@app.route('/api/boats/<int:boat_id>/generate-polar', methods=['POST'])
@token_required
def generate_polar(current_user, boat_id):
    try:
        boat = Boat.query.filter_by(id=boat_id, user_id=current_user.id).first()
        
        if not boat:
            return jsonify({'message': 'Boat not found'}), 404
        
        log_files = LogFile.query.filter_by(boat_id=boat_id).all()
        
        if not log_files:
            return jsonify({'message': 'No log files found for this boat'}), 400
        
        # TODO: Implement polar generation logic here
        # For now, return a placeholder response
        
        return jsonify({
            'message': 'Polar generation started',
            'status': 'processing',
            'log_files_count': len(log_files)
        }), 202
        
    except Exception as e:
        logger.error(f"Generate polar error: {str(e)}")
        return jsonify({'message': 'Failed to generate polar', 'error': str(e)}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'message': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'message': 'Internal server error'}), 500

# Initialize database tables
with app.app_context():
    try:
        db.create_all()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {str(e)}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)

