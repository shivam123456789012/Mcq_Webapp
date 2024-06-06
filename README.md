# Mcq_Webapp
# OBJECTIVE :
The objective of this project project implements a web-based MCQ (Multiple Choice Questions) management system using the Flask framework. The system allows administrators to upload questions in bulk via CSV files, stores them in a database, and provides functionalities to manage candidates and their test results.
# TECHNOLOGIES USED :
 1. Flask: A lightweight web framework for Python.
 2. SQLAlchemy: An ORM for database operations.
 3. SQLite: A lightweight database for storing application data.
 4. Pandas: A data manipulation library used for exporting results to Excel.
 5. Tempfile: A module for creating temporary files.
 6. Werkzeug: A library for secure file handling.
 7. Secrets: A module for generating secure tokens for session management.
 8. SMTP: Simple mail transfer protocol
 9. URLSafeTimedSerializer: A library component which provides a way to serialize data into a URL-safe format.
# OPERATING INSTRUCTIONS :
 1. Configure email ID and password of recipient in config.cfg.
 2. Provide the candidate's email ID and upload the question file (in CSV format) on the upload page.
 3. The candidate will receive an email containing the registration form link.
 4. Complete the form using the provided link and submit it.
 5. Proceed to the MCQ test.
 6. The results will be updated in a CSV file on the result page.
