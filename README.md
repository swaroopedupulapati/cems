# 🚨 Crime Evidence Management System (CEMS)

> CEMS is a secure web application built on **Flask** and **MongoDB** designed to manage, track, and secure case files and evidence for law enforcement agencies. It features user authentication, a two-level organizational hierarchy, secure file storage via GridFS, detailed activity logging, and email notifications for sensitive operations.

## ✨ Key Features

  * **Multi-Level User Access:** Separate login and functionalities for **Higher Officials (HIO)** and **Lower Officials (LOO)**.
  * **MongoDB & GridFS Integration:** Uses **MongoDB** for user and case metadata, and **GridFS** for storing large evidence files (images, PDFs, videos, etc.) securely.
  * **OTP Verification:** Secure login/form submission workflow using **6-digit One-Time Passwords (OTP)** sent via email.
  * **Comprehensive Case Management:**
      * **Add Case:** Lower officials can register new cases with custom data labels (text and file uploads).
      * **View Case:** Officials can search, view, download, and render case details and embedded media.
      * **Edit Case:** Update existing case details and evidence.
      * **Remove Case:** Secure deletion of cases.
  * **Audit/Ledger Log:** Tracks all major system activities (user registration, case removal/addition) with timestamps (Asia/Kolkata timezone).
  * **Automated Email Alerts:** Sends registration credentials to new officials and case update summaries (with before/after PDFs) to all Higher Officials.
  * **Dynamic PDF Generation:** Generates comprehensive case summary PDFs on demand, including embedded images and text file contents, using **ReportLab** and **PyMuPDF (fitz)**.

-----

## ⚙️ Technology Stack

| Category | Tools / Libraries | Purpose |
| :--- | :--- | :--- |
| **Backend Framework** | `Flask` | Routing, request handling, and application structure. |
| **Database** | `PyMongo`, `GridFS` | Persistent data storage for case metadata, credentials, and evidence files. |
| **Email/Security** | `smtplib`, `email` | Sending OTPs and notification emails for secure and auditable actions. |
| **PDF Generation** | `reportlab`, `fitz` (PyMuPDF) | Creating structured PDF reports from case data and rendering embedded file types. |
| **Utilities** | `datetime`, `pytz`, `random`, `base64` | Handling timezones, generating OTPs, and encoding file data. |

-----

## 💻 Getting Started

### Prerequisites

You must have **Python 3.x** and access to a MongoDB instance.

### Installation

1.  **Clone the repository:**
    ```bash
    git clone [YOUR_REPOSITORY_URL]
    cd crime-evidence-management-system
    ```
2.  **Install the required libraries:**
    ```bash
    pip install Flask PyMongo gridfs reportlab PyMuPDF pytz
    ```

### Configuration

You must configure the following in `app.py`:

1.  **MongoDB Connection:** Update the connection details:

    ```python
    mydb = "mongodb://..." # Replace with your actual connection string
    client = MongoClient(mydb)
    my_db = client["swaroopdb"]
    ```

2.  **Email Credentials:** Update the sender's details for OTP and alert emails:

    ```python
    SENDER_EMAIL = "your_mail_id@gmail.com"
    SENDER_PASSWORD = "your_app_password_or_key" # Use an App Password for Gmail!
    ```

3.  **Default User:** The system automatically checks and inserts a default "police" user for initial access if the collections are empty.

      * **ID:** `100`
      * **Password:** `police@1234`

### Running the App

1.  **Run the Flask application:**
    ```bash
    python app.py
    ```
2.  Navigate to `http://127.0.0.1:5000/` to access the home page and login interface.

-----

## 🚦 Application Workflow

### Authentication and User Management

  * **Login:** Users choose between **Higher Officials (HIO)** and **Lower Officials (LOO)** login pages.
  * **OTP Generation/Verification:** An AJAX-backed route handles generating an OTP (stored in `session`) and verifying it against user input.
  * **Registration (`/reghio`, `/regloo`):** HIOs can register new officials. Credentials (`ID@123`) are auto-generated and sent via email.
  * **Password Change:** Dedicated routes for both HIOs and LOOs to update their passwords.

### Case and Evidence Management

  * **Adding a Case (`/add_case`):** Lower Officials can enter a unique `case_number` and dynamically add multiple pieces of evidence, each with a custom label (text) and an optional file upload (stored in **GridFS**).
  * **Viewing a Case (`/view`):** Users can retrieve cases by number. File evidence is fetched from GridFS and rendered directly on the web page (images, PDFs, text) or offered for download.
  * **Editing a Case (`/edit_case`):** Allows updating existing case details. Upon successful update, **two PDFs** are generated (one of the previous state, one of the updated state) and emailed to all Higher Officials for auditing.

### Auditing and Reporting

  * **Ledger (`/viewledger`):** A dedicated route to view the chronological log of all sensitive actions performed in the system, including case additions and removals.
  * **PDF Download (`/download_pdf/<case_number>`):** Generates a comprehensive, printable PDF report of all case details and embedded evidence (images and text content) for official documentation.

-----

## 🤝 Contribution

Feel free to fork the repository and submit pull requests for enhancements, such as:

  * Integrating strong password hashing (e.g., bcrypt) instead of plain text storage.
  * Implementing user roles within the HIO/LOO levels.
  * Adding a search function for case details beyond the case number.
