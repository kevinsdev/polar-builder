from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from src.models.user import db, Boat, LogFile, Polar
from src.routes.auth import token_required
from src.polar_engine import process_log_files
from src.cloud_storage import cloud_storage
from datetime import datetime
import os
import json
import tempfile
import io

polars_bp = Blueprint('polars', __name__)

ALLOWED_EXTENSIONS = {'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@polars_bp.route('/boats/<int:boat_id>/upload', methods=['POST'])
@token_required
def upload_files(current_user, boat_id):
    """Upload log files for a boat using cloud storage"""
    try:
        boat = Boat.query.filter_by(id=boat_id, user_id=current_user.id).first()
        if not boat:
            return jsonify({'error': 'Boat not found'}), 404
        
        if 'files' not in request.files:
            return jsonify({'error': 'No files provided'}), 400
        
        files = request.files.getlist('files')
        if not files or files[0].filename == '':
            return jsonify({'error': 'No files selected'}), 400
        
        uploaded_files = []
        
        for file in files:
            if file and allowed_file(file.filename):
                # Read file content
                file_content = file.read()
                filename = secure_filename(file.filename)
                
                # Create cloud storage key
                cloud_key = f"boats/{boat_id}/logs/{filename}"
                
                # Upload to cloud storage
                file_stream = io.BytesIO(file_content)
                success = cloud_storage.upload_file(file_stream, cloud_key, 'text/csv')
                
                if success:
                    # Create log file record with cloud storage info
                    log_file = LogFile(
                        boat_id=boat_id,
                        filename=filename,
                        file_path=cloud_key,  # Store cloud key
                        file_size=len(file_content),
                        upload_date=datetime.now(),
                        status='uploaded'
                    )
                    
                    db.session.add(log_file)
                    uploaded_files.append({
                        'filename': filename,
                        'size': len(file_content),
                        'cloud_key': cloud_key
                    })
                else:
                    return jsonify({'error': f'Failed to upload {filename} to cloud storage'}), 500
        
        db.session.commit()
        
        return jsonify({
            'message': f'Successfully uploaded {len(uploaded_files)} files to cloud storage',
            'files': uploaded_files
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@polars_bp.route('/boats/<int:boat_id>/generate-polar', methods=['POST'])
@token_required
def generate_polar(current_user, boat_id):
    """Generate polar from cloud-stored log files"""
    try:
        boat = Boat.query.filter_by(id=boat_id, user_id=current_user.id).first()
        if not boat:
            return jsonify({'error': 'Boat not found'}), 404
        
        # Get all log files for this boat
        log_files = LogFile.query.filter_by(boat_id=boat_id).all()
        if not log_files:
            return jsonify({'error': 'No log files found for this boat'}), 400
        
        # Download files from cloud storage and create temporary files
        temp_files = []
        try:
            for lf in log_files:
                # Download file content from cloud storage
                file_content = cloud_storage.download_file(lf.file_path)
                if file_content:
                    # Create temporary file
                    temp_file = tempfile.NamedTemporaryFile(mode='w+b', suffix='.csv', delete=False)
                    temp_file.write(file_content)
                    temp_file.close()
                    temp_files.append(temp_file.name)
                else:
                    current_app.logger.warning(f"Could not download file: {lf.file_path}")
            
            if not temp_files:
                return jsonify({'error': 'No accessible log files found in cloud storage'}), 400
            
            # Generate polar using our engine
            polar_content, summary = process_log_files(temp_files, boat.name)
            
            if not polar_content:
                return jsonify({'error': f'Polar generation failed: {summary}'}), 400
            
            # Upload polar to cloud storage
            polar_filename = f"{boat.name}_.txt"
            polar_key = f"boats/{boat_id}/polars/{polar_filename}"
            
            polar_stream = io.BytesIO(polar_content.encode('utf-8'))
            success = cloud_storage.upload_file(polar_stream, polar_key, 'text/plain')
            
            if not success:
                return jsonify({'error': 'Failed to save polar to cloud storage'}), 500
            
            # Get existing polar count for versioning
            existing_polars = Polar.query.filter_by(boat_id=boat_id).count()
            version = existing_polars + 1
            
            # Create polar record
            polar = Polar(
                boat_id=boat_id,
                version=version,
                polar_data=polar_content,
                generation_date=datetime.now(),
                data_summary=json.dumps(summary) if isinstance(summary, dict) else str(summary),
                file_url=polar_key  # Store cloud key
            )
            
            db.session.add(polar)
            db.session.commit()
            
            return jsonify({
                'message': 'Polar generated successfully and saved to cloud storage',
                'polar_id': polar.id,
                'version': version,
                'summary': summary,
                'cloud_key': polar_key
            }), 200
            
        finally:
            # Clean up temporary files
            for temp_file in temp_files:
                try:
                    os.unlink(temp_file)
                except OSError:
                    pass
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@polars_bp.route('/boats/<int:boat_id>/polars', methods=['GET'])
@token_required
def get_polars(current_user, boat_id):
    """Get all polars for a boat"""
    try:
        boat = Boat.query.filter_by(id=boat_id, user_id=current_user.id).first()
        if not boat:
            return jsonify({'error': 'Boat not found'}), 404
        
        polars = Polar.query.filter_by(boat_id=boat_id).order_by(Polar.generation_date.desc()).all()
        
        polar_list = []
        for polar in polars:
            polar_list.append({
                'id': polar.id,
                'version': polar.version,
                'generation_date': polar.generation_date.isoformat(),
                'summary': json.loads(polar.data_summary) if polar.data_summary else {},
                'cloud_key': getattr(polar, 'file_url', None)
            })
        
        return jsonify({'polars': polar_list}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@polars_bp.route('/boats/<int:boat_id>/polars/<int:polar_id>/download', methods=['GET'])
@token_required
def download_polar(current_user, boat_id, polar_id):
    """Download a specific polar from cloud storage"""
    try:
        boat = Boat.query.filter_by(id=boat_id, user_id=current_user.id).first()
        if not boat:
            return jsonify({'error': 'Boat not found'}), 404
        
        polar = Polar.query.filter_by(id=polar_id, boat_id=boat_id).first()
        if not polar:
            return jsonify({'error': 'Polar not found'}), 404
        
        # Try to get from cloud storage first
        polar_content = polar.polar_data
        if hasattr(polar, 'file_url') and polar.file_url:
            cloud_content = cloud_storage.download_file(polar.file_url)
            if cloud_content:
                polar_content = cloud_content.decode('utf-8')
        
        return jsonify({
            'polar_content': polar_content,
            'filename': f"{boat.name}_.txt",
            'generation_date': polar.generation_date.isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@polars_bp.route('/boats/<int:boat_id>/polars/latest/download', methods=['GET'])
@token_required
def download_latest_polar(current_user, boat_id):
    """Download the latest polar for a boat from cloud storage"""
    try:
        boat = Boat.query.filter_by(id=boat_id, user_id=current_user.id).first()
        if not boat:
            return jsonify({'error': 'Boat not found'}), 404
        
        polar = Polar.query.filter_by(boat_id=boat_id).order_by(Polar.generation_date.desc()).first()
        if not polar:
            return jsonify({'error': 'No polars found for this boat'}), 404
        
        # Try to get from cloud storage first
        polar_content = polar.polar_data
        if hasattr(polar, 'file_url') and polar.file_url:
            cloud_content = cloud_storage.download_file(polar.file_url)
            if cloud_content:
                polar_content = cloud_content.decode('utf-8')
        
        return jsonify({
            'polar_content': polar_content,
            'filename': f"{boat.name}_.txt",
            'generation_date': polar.generation_date.isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@polars_bp.route('/boats/<int:boat_id>/files', methods=['GET'])
@token_required
def get_boat_files(current_user, boat_id):
    """Get all uploaded files for a boat"""
    try:
        boat = Boat.query.filter_by(id=boat_id, user_id=current_user.id).first()
        if not boat:
            return jsonify({'error': 'Boat not found'}), 404
        
        log_files = LogFile.query.filter_by(boat_id=boat_id).order_by(LogFile.upload_date.desc()).all()
        
        file_list = []
        for lf in log_files:
            file_list.append({
                'id': lf.id,
                'filename': lf.filename,
                'size': lf.file_size,
                'upload_date': lf.upload_date.isoformat(),
                'status': lf.status,
                'cloud_key': lf.file_path
            })
        
        return jsonify({'files': file_list}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

