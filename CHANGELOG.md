# Changelog

All notable changes to the Task Dashboard application will be documented in this file.

## [1.3.0] - 2025-07-26

### Added
- **Docker Support**: Complete Docker containerization for easy deployment
- **Docker Compose**: Simplified deployment with docker-compose.yml for both development and production
- **Docker Documentation**: Comprehensive DOCKER.md with usage instructions for containerized deployment
- **Startup Script**: Added startup.sh for easy application startup with configurable database
- **Docker Ignore**: .dockerignore file to exclude unnecessary files from Docker builds
- **Environment Example**: Added .env.example file with clear configuration examples for both SQLite and MySQL

### Technical Improvements
- **Container Configuration**: Optimized Dockerfile with multi-stage build and proper environment handling
- **Database Flexibility**: Docker containers support both SQLite (development) and MySQL (production) via environment variables
- **Data Persistence**: Docker volume support for persistent SQLite database storage
- **Port Configuration**: Exposes both 3000 (frontend) and 8000 (backend API) ports for containerized deployment

## [1.2.0] - 2025-07-23

### Added
- **Rate Limiting**: Implemented API rate limiting using slowapi to prevent abuse
- **Enhanced Security**: Added password strength validation and secure password hashing
- **Security Tests**: New test suite for authentication security validation
- **Password Migration**: Script to migrate existing passwords to bcrypt hashing

### Changed
- **Authentication**: Enhanced authentication with bcrypt password hashing
- **API Security**: Added rate limiting to all authentication endpoints
- **Password Validation**: Strengthened password requirements (min 6 characters)
- **Dependency Management**: Added slowapi for rate limiting functionality

### Fixed
- **Security Vulnerabilities**: Addressed potential security issues in authentication
- **Test Suite**: Updated tests to handle new security features
- **Rate Limiting**: Fixed test failures related to rate limiting implementation

## [1.1.0] - 2025-07-24

### Added
- **Deployment Configuration**: Added nginx and systemd service configuration files for production deployment
- **Automated Deployment Script**: Shell script to automate deployment with environment variable configuration
- **Environment Configuration**: Added .env.production file for production MySQL configuration
- **Database Flexibility**: Support for both SQLite (development) and MySQL (production) databases
- **Security Enhancement**: Removed private server information from configuration files for safer version control

### Changed
- **Configuration Files**: Replaced private information with generic placeholders in all deployment files
- **Documentation**: Updated README and CLAUDE.md with deployment instructions

## [1.0.2] - 2025-07-23

### Added
- **Clickable Status Buttons**: Direct status changes with one-click buttons instead of dropdown
- **Bilingual Status Buttons**: English/Chinese support for status buttons
- **Visual Status Indicators**: Active status highlighted with color-coded buttons
- **Enhanced User Experience**: Instant status changes without dropdown interaction

### Changed
- **Status Selection**: Replaced dropdown with direct click buttons (Todo, In Progress, Done)
- **Button Design**: Color-coded status buttons (Orange for todo, Yellow for in-progress, Green for done)
- **Visual Feedback**: Active status shows solid background, inactive shows ghost buttons

### Fixed
- **Edit/Delete Buttons**: Fixed broken task editing and deletion functionality
- **Task ID Handling**: Fixed type conversion issues for task identification
- **ORM Compatibility**: Resolved Pydantic ORM mode configuration issues

## [1.0.1] - 2025-07-23

### Added
- **Ultra-light Task Cards**: Pastel gradient backgrounds for better visibility
- **Enhanced Readability**: Improved text contrast and darker colors on light backgrounds
- **Subtle Borders**: Added light gray borders for card definition
- **Status-based Colors**: Consistent color scheme matching statistics page

### Changed
- **Card Design**: Moved from dark gradients to ultra-light pastel backgrounds
- **Text Colors**: Updated to darker shades for better readability on light backgrounds
- **Shadow Effects**: Reduced intensity for cleaner appearance

### Fixed
- **Button Functionality**: Restored edit and delete button operations
- **Database Session**: Fixed session management for task operations
- **Type Handling**: Improved task ID parameter handling

## [1.0.0] - 2025-07-23

### Added
- **Multi-page Navigation System**: New navigation between Tasks and Statistics pages
- **Modern Statistics Dashboard**: Completely redesigned with gradient cards and circular progress indicators
- **Responsive Grid Layout**: Adaptive layouts for mobile and desktop viewing
- **Enhanced Visual Design**: Modern UI with hover effects and professional styling

### Changed
- **Statistics Panel**: Upgraded from basic text display to modern gradient cards with icons
- **Progress Indicators**: Added circular progress indicators for completion rates
- **Layout Structure**: Separated statistics and task management into dedicated pages
- **Visual Hierarchy**: Improved typography and spacing throughout the interface

### Fixed
- **Reflex Warnings**: Fixed Var to string conversion warnings in statistics display
- **Progress Bar Width**: Fixed progress bars to properly fill available space
- **Text Alignment**: Improved alignment in breakdown panels for better readability
- **Duplicate Content**: Removed redundant summary row from statistics panel

### Technical Improvements
- **State Management**: Added navigation state for multi-page functionality
- **Translation Support**: Extended translation keys for new navigation elements
- **Responsive Design**: Implemented Tailwind CSS grid system for all screen sizes
- **Performance**: Optimized reactive variable handling in statistics calculations