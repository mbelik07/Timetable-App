# Timetable-App

A standalone desktop application for managing timetables, teachers, courses, and units, built with Python and Tkinter.

## How to Run the Application

### 1. Install Python

If you don't have a stable version of Python installed, download it from the [official Python website](https://www.python.org/downloads/macos/). This is recommended over the version of Python that may come with macOS, as it includes a stable GUI toolkit required by the app.

During installation, make sure to check the box that says "Add Python to PATH."

### 2. Install Required Libraries

This application requires the `reportlab` library to export timetables to PDF. Open your terminal and run the following command to install it.

**Important:** If you installed Python from the official website, use the `python3 -m pip` command to ensure the library is installed for the correct Python version.

```bash
# For the official Python.org installation
/usr/local/bin/python3 -m pip install reportlab

# If you are using the system Python (not recommended, may cause crashes)
# pip3 install reportlab
```

### 3. Download and Run the App

1.  **Download the Code:**
    Download the `database.py` and `app.py` files from this repository and save them in the **same folder** on your computer.

2.  **Open a Terminal:**
    Navigate to the folder where you saved the files. For example:
    ```bash
    cd Desktop/TimeTableApp
    ```

3.  **Run the App:**
    Use the full path to the Python you installed from python.org to avoid issues with the native macOS version.
    ```bash
    /usr/local/bin/python3 app.py
    ```

The application window should now appear. A `timetable.db` file will be created in the same folder to store your data.

## Features

-   **Multi-College Management:** Add and manage timetables for different colleges (e.g., Moss Vale, Goulburn).
-   **Granular Timetable:** Schedule classes in 1-hour time slots.
-   **Teacher, Course, and Unit Management:** Add, delete, and manage your staff and curriculum.
-   **Workload Tracking:** Automatically calculates and displays the weekly scheduled hours for each teacher.
-   **Print to PDF:** Export the timetable for any college to a clean, printable PDF document.
