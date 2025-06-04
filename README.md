# Team Project & Problem Tracker

A comprehensive, lightweight, internal team application for tracking projects and problems, including detailed analytics. Built with Python, Streamlit, and SQLite.

## Features

- Project Management
  - Create and track projects with different durations (1-4 weeks)
  - Assign team members to projects
  - Update project status (Open, In Progress, Completed)
  - Track project completion times

- Problem Management
  - Create and track problems
  - Link problems to projects
  - Assign categories with point values
  - Claim/unclaim problems
  - Update problem status
  - Track problem completion times

- Category Management
  - Create categories with point values
  - Track problem completion by category

- User Management
  - Add team members
  - Track problem assignments and completions

- Analytics Dashboard
  - Overall progress metrics
  - Problem completion by category
  - Problem completion time analysis
  - Project status breakdown
  - Problem status by user

## Requirements

- Python 3.x
- streamlit
- pandas
- sqlite3 (included in Python standard library)

## Installation

1. Clone the repository or download the source code.

2. Install the required packages:
```bash
pip install streamlit pandas
```

## Running the Application

1. Navigate to the project directory in your terminal.

2. Run the Streamlit application:
```bash
streamlit run app.py
```

3. The application will open in your default web browser at `http://localhost:8501`.

## Usage

1. First, add users using the "Add New User" section in the sidebar.

2. Create categories with point values in the Categories page.

3. Create projects and assign team members in the Projects page.

4. Create problems, assign categories, and link them to projects in the Problems page.

5. Use the Dashboard to view open projects and problems.

6. Monitor progress and analyze data in the Analytics page.

## Database

The application uses SQLite as its database, stored in `tracker.db`. The database is automatically created and initialized when you first run the application.

## Contributing

Feel free to submit issues and enhancement requests!
