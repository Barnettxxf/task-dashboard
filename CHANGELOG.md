# Changelog

All notable changes to the Task Dashboard application will be documented in this file.

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

## [1.0.0] - 2025-07-23

### Initial Release
- Basic task management functionality
- User authentication system
- Multi-language support (English/Chinese)
- Responsive design foundation
- REST API integration