# Team Project & Problem Tracker

A Streamlit application for tracking team projects and problems, with features for user management, project tracking, and problem resolution.

## Features

- User authentication and registration
- Project management with team assignments
- Problem tracking with categories and points
- Analytics dashboard
- User role management

## Project Structure

```
src/
├── database/
│   └── db.py           # Database connection and initialization
├── auth/
│   └── auth.py         # Authentication and user management
├── models/
│   └── constants.py    # Application constants
├── ui/
│   ├── components.py   # Reusable UI components
│   └── pages.py        # Page-specific UI components
└── app.py             # Main application file
```

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run src/app.py
```

## Usage

1. Register a new user account
2. Log in with your credentials
3. Navigate through different sections using the sidebar:
   - Dashboard: Overview of open projects and problems
   - Projects: Create and manage projects
   - Problems: Track and resolve problems
   - Categories: Manage problem categories
   - Users: View user details and assignments
   - Analytics: View project and problem statistics

## Development

The application is structured into several modules:

- `database/`: Database connection and schema management
- `auth/`: User authentication and session management
- `models/`: Data models and constants
- `ui/`: User interface components and pages

To add new features:

1. Add necessary database tables in `database/db.py`
2. Create UI components in `ui/components.py`
3. Add page-specific logic in `ui/pages.py`
4. Update the main application in `app.py`
