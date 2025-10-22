# 🏨 Reservation Export Automation

A Python automation tool that logs into a booking dashboard, applies custom date filters, and downloads reservation data as a CSV — then automatically converts it into a clean JSON file. 🚀

> **Note:** This script interacts with the web interface of your booking platform. It may break if the platform updates its layout or security features.

---

## Features

- Automated login using saved credentials.  
- Interactive date filter selection.  
- Downloads reservations as a CSV file.  
- Cleans and converts data to JSON format.  
- Fully hands-free once launched.

---

## Requirements

- Python 3.x  
- Google Chrome browser  
- `chromedriver` installed (compatible with your browser version)  
- A `.env` file containing your credentials  
- Required Python packages:
  - `selenium`
  - `python-dotenv`
  - `requests`
  - `pandas`

---

## Installation

1. **Clone the repository**:

    ```bash
    git clone https://github.com/hamzidevv/Reservation-Export-Automation.git
    cd Reservation-Export-Automation

2. **Install dependencies:**

    ```bash
    pip install -r requirements.txt
   
3. **Add your credentials:** Simply rename .env.example to .env and fill in your details:

    ```bash
    WEBSITE_URL="https://example.com"
    USER_EMAIL="you@example.com"
    USER_PASS="yourpassword"
   
4. **Download the appropriate version of `chromedriver` for your OS and Chrome version:**
   [Chrome Driver](https://chromedriver.chromium.org/downloads)
   Place the driver in the project directory or your system PATH.

5. **Run the script:**
   
    ```bash
    python main.py

## How It Works
1. Logs into booking dashboard using your credentials.
2. Prompts for start and end dates.
3. Applies the selected date filters on the reservations page.
4. Downloads the CSV through the export link.
5. Parses and converts it to JSON format.
6. Saves the file as
   ```bash
    reservations_STARTDATE_to_ENDDATE.json

## Example Output
    [
      {
        "Status": "Confirmed",
        "Guest first name": "John",
        "Guest last name": "Doe",
        "Booking reference": "ABC123",
        "Check in date": "2025-10-20",
        "Check out date": "2025-10-22",
        "Guest email": "john@example.com",
        "Guest phone number": null
      }
    ]

🎉 That’s it — just run and relax while it does all the work for you.
