from flask import Blueprint, request, jsonify
from src.models.user import db, Boat, LogFile, Polar
from src.routes.auth import token_required

boats_bp = Blueprint('boats', __name__)

@boats_bp.route('/boats', methods=['GET'])
@token_required
def get_boats(current_user):
    """Get all boats for the current user"""
    try:
        boats = Boat.query.filter_by(user_id=current_user.id).all()
        return jsonify({
            'boats': [boat.to_dict() for boat in boats]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@boats_bp.route('/boats', methods=['POST'])
@token_required
def create_boat(current_user):
    """Create a new boat"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('name') or not data.get('boat_type'):
            return jsonify({'error': 'Name and boat type are required'}), 400
        
        # Create new boat
        boat = Boat(
            user_id=current_user.id,
            name=data['name'],
            boat_type=data['boat_type'],
            class_name=data.get('class_name'),
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
            rating_system=data.get('rating_system'),
            rating_value=data.get('rating_value'),
            crew_size=data.get('crew_size'),
            notes=data.get('notes')
        )
        
        db.session.add(boat)
        db.session.commit()
        
        return jsonify({
            'message': 'Boat created successfully',
            'boat': boat.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@boats_bp.route('/boats/<int:boat_id>', methods=['GET'])
@token_required
def get_boat(current_user, boat_id):
    """Get a specific boat"""
    try:
        boat = Boat.query.filter_by(id=boat_id, user_id=current_user.id).first()
        
        if not boat:
            return jsonify({'error': 'Boat not found'}), 404
        
        return jsonify({
            'boat': boat.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@boats_bp.route('/boats/<int:boat_id>', methods=['PUT'])
@token_required
def update_boat(current_user, boat_id):
    """Update a boat"""
    try:
        boat = Boat.query.filter_by(id=boat_id, user_id=current_user.id).first()
        
        if not boat:
            return jsonify({'error': 'Boat not found'}), 404
        
        data = request.get_json()
        
        # Update allowed fields
        updatable_fields = [
            'name', 'boat_type', 'class_name', 'year_built',
            'loa', 'lwl', 'beam', 'draft', 'displacement', 'sail_area',
            'keel_type', 'rig_type', 'hull_material',
            'rating_system', 'rating_value', 'crew_size', 'notes'
        ]
        
        for field in updatable_fields:
            if field in data:
                setattr(boat, field, data[field])
        
        db.session.commit()
        
        return jsonify({
            'message': 'Boat updated successfully',
            'boat': boat.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@boats_bp.route('/boats/<int:boat_id>', methods=['DELETE'])
@token_required
def delete_boat(current_user, boat_id):
    """Delete a boat"""
    try:
        boat = Boat.query.filter_by(id=boat_id, user_id=current_user.id).first()
        
        if not boat:
            return jsonify({'error': 'Boat not found'}), 404
        
        db.session.delete(boat)
        db.session.commit()
        
        return jsonify({
            'message': 'Boat deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@boats_bp.route('/boats/<int:boat_id>/files', methods=['GET'])
@token_required
def get_boat_files(current_user, boat_id):
    """Get all log files for a boat"""
    try:
        boat = Boat.query.filter_by(id=boat_id, user_id=current_user.id).first()
        
        if not boat:
            return jsonify({'error': 'Boat not found'}), 404
        
        files = LogFile.query.filter_by(boat_id=boat_id).order_by(LogFile.upload_date.desc()).all()
        
        return jsonify({
            'files': [file.to_dict() for file in files]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@boats_bp.route('/boats/<int:boat_id>/polars', methods=['GET'])
@token_required
def get_boat_polars(current_user, boat_id):
    """Get all polars for a boat"""
    try:
        boat = Boat.query.filter_by(id=boat_id, user_id=current_user.id).first()
        
        if not boat:
            return jsonify({'error': 'Boat not found'}), 404
        
        polars = Polar.query.filter_by(boat_id=boat_id).order_by(Polar.version.desc()).all()
        
        return jsonify({
            'polars': [polar.to_dict() for polar in polars]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@boats_bp.route('/boats/<int:boat_id>/current-polar', methods=['GET'])
@token_required
def get_current_polar(current_user, boat_id):
    """Get the current polar for a boat"""
    try:
        boat = Boat.query.filter_by(id=boat_id, user_id=current_user.id).first()
        
        if not boat:
            return jsonify({'error': 'Boat not found'}), 404
        
        current_polar = Polar.query.filter_by(boat_id=boat_id, is_current=True).first()
        
        if not current_polar:
            return jsonify({'error': 'No current polar found'}), 404
        
        return jsonify({
            'polar': current_polar.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@boats_bp.route('/boats/<int:boat_id>/stats', methods=['GET'])
@token_required
def get_boat_stats(current_user, boat_id):
    """Get statistics for a boat"""
    try:
        boat = Boat.query.filter_by(id=boat_id, user_id=current_user.id).first()
        
        if not boat:
            return jsonify({'error': 'Boat not found'}), 404
        
        # Get file statistics
        total_files = LogFile.query.filter_by(boat_id=boat_id).count()
        processed_files = LogFile.query.filter_by(boat_id=boat_id, processing_status='completed').count()
        total_data_points = db.session.query(db.func.sum(LogFile.clean_data_points)).filter_by(boat_id=boat_id).scalar() or 0
        
        # Get polar statistics
        total_polars = Polar.query.filter_by(boat_id=boat_id).count()
        current_polar = Polar.query.filter_by(boat_id=boat_id, is_current=True).first()
        
        # Get data coverage
        wind_range = db.session.query(
            db.func.min(LogFile.wind_range_min),
            db.func.max(LogFile.wind_range_max)
        ).filter_by(boat_id=boat_id).first()
        
        angle_range = db.session.query(
            db.func.min(LogFile.angle_range_min),
            db.func.max(LogFile.angle_range_max)
        ).filter_by(boat_id=boat_id).first()
        
        return jsonify({
            'stats': {
                'total_files': total_files,
                'processed_files': processed_files,
                'total_data_points': int(total_data_points),
                'total_polars': total_polars,
                'current_polar_version': current_polar.version if current_polar else None,
                'wind_range': [wind_range[0], wind_range[1]] if wind_range[0] is not None else None,
                'angle_range': [angle_range[0], angle_range[1]] if angle_range[0] is not None else None,
                'last_upload': LogFile.query.filter_by(boat_id=boat_id).order_by(LogFile.upload_date.desc()).first().upload_date.isoformat() if LogFile.query.filter_by(boat_id=boat_id).first() else None
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

