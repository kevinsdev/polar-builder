# Polar Builder - Racing Sailor Performance Analysis Platform

A comprehensive web application for racing sailors to build polar models from actual performance data logged in Expedition software.

## Features

- **Multi-User Platform**: Secure user registration and authentication
- **Fleet Management**: Create and manage multiple boat profiles
- **Log File Processing**: Upload and analyze Expedition log files
- **Polar Generation**: Automatically generate polar tables from sailing data
- **Progressive Development**: Continuously improve polars with new data
- **Cloud Storage**: Secure file storage and management
- **Professional Interface**: Modern, responsive design for racing sailors

## Architecture

### Backend (`/backend`)
- **Framework**: Flask with SQLAlchemy ORM
- **Authentication**: JWT-based secure authentication
- **Database**: SQLite with proper relationships (Users → Boats → LogFiles → Polars)
- **Cloud Storage**: S3-compatible storage for log files and generated polars
- **API**: RESTful API with comprehensive endpoints

### Frontend (`/frontend`)
- **Framework**: React with modern UI components
- **Styling**: Tailwind CSS with responsive design
- **State Management**: React hooks and context
- **Authentication**: JWT token management
- **File Upload**: Drag-and-drop interface for log files

## Deployment

### Production Environment
- **Server**: Digital Ocean droplet with Docker containers
- **Reverse Proxy**: Nginx with SSL certificates
- **Database**: SQLite (easily upgradeable to PostgreSQL)
- **File Storage**: AWS S3 for scalable file management
- **CI/CD**: GitHub Actions for automated deployments

### Environment Variables
```bash
# Backend
FLASK_ENV=production
SECRET_KEY=your-secret-key
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
S3_BUCKET_NAME=polar-builder-files
S3_REGION=us-east-1

# Frontend
VITE_API_BASE_URL=https://your-domain.com/api
```

## Local Development

### Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python src/main.py
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/profile` - Get user profile

### Boats
- `GET /api/boats` - List user's boats
- `POST /api/boats` - Create new boat
- `GET /api/boats/{id}` - Get boat details
- `PUT /api/boats/{id}` - Update boat
- `DELETE /api/boats/{id}` - Delete boat

### File Management
- `POST /api/boats/{id}/upload` - Upload log files
- `GET /api/boats/{id}/files` - List boat files
- `DELETE /api/boats/{id}/files/{file_id}` - Delete file

### Polar Generation
- `POST /api/boats/{id}/generate-polar` - Generate polar from logs
- `GET /api/boats/{id}/polars` - List generated polars
- `GET /api/boats/{id}/polars/{polar_id}/download` - Download polar

## Polar Generation Engine

The application includes a sophisticated polar generation engine that:

1. **Processes Expedition Log Files**: Parses CSV format with wind speed, wind angle, and boat speed data
2. **Filters Performance Data**: Removes invalid data points and outliers
3. **Calculates Target Speeds**: Determines optimal boat speeds for different wind conditions
4. **Generates Polar Tables**: Creates Expedition-compatible polar files
5. **Progressive Improvement**: Combines multiple sailing sessions for better accuracy

## Security Features

- **Password Hashing**: Secure password storage with bcrypt
- **JWT Authentication**: Stateless authentication with secure tokens
- **CORS Configuration**: Proper cross-origin request handling
- **Input Validation**: Comprehensive data validation and sanitization
- **File Upload Security**: Secure file handling and storage

## Monitoring and Maintenance

- **Health Checks**: API health monitoring endpoints
- **Error Logging**: Comprehensive error tracking and logging
- **Performance Monitoring**: Response time and resource usage tracking
- **Automated Backups**: Regular database and file backups

## Contributing

This application is designed for racing sailors and sailing performance analysis. Future enhancements may include:

- Advanced polar analysis and visualization
- Weather routing integration
- Race performance analytics
- Mobile application development
- Integration with other sailing software

## License

Proprietary software for racing sailor performance analysis.

## Support

For technical support and feature requests, contact the development team.

---

**Built for Racing Sailors, by Sailing Enthusiasts** ⛵🏆

