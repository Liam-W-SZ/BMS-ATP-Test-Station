# BMS ATP Test Station

This repository contains a program designed for performing final checks on Battery Management Systems (BMS). It provides tools for managing test results, analyzing data, and interacting with the system through both graphical and web-based interfaces.

---

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Folder Structure](#folder-structure)
- [Requirements](#requirements)
- [Setup](#setup)
- [Usage](#usage)
  - [1. Running the Tkinter GUI](#1-running-the-tkinter-gui)
  - [2. Processing Data](#2-processing-data)
  - [3. Managing Test Results](#3-managing-test-results)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

The **BMS Final Check** program is a comprehensive solution for validating and managing Battery Management Systems (BMS). It is designed to:
- Automate the processing of test results for both production and RMA (Return Merchandise Authorization) units.
- Provide user-friendly interfaces for interacting with the system.
- Enable easy customization through configuration files.

This program is implemented in Python and supports both command-line and graphical interfaces.

---

## Features

- **Tkinter GUI**: A desktop-based graphical user interface for local use.
- **Data Processing Tools**: Scripts for analyzing and managing test results.
- **Customizable Configurations**: JSON-based configuration files for production and RMA settings.
- **Test Result Management**: Organized storage and processing of test results for production and RMA units.

---

## Folder Structure

The repository is organized as follows:

```
BMS_Final_Check/
├── Action.sh                     # Shell script for automated actions
├── config.json                   # Configuration file for production
├── configRMA.json                # Configuration file for RMA
├── Login.json                    # Login credentials/configuration
├── main.py                       # Main entry point for the program
├── README.md                     # Documentation file
├── tkinter_gui.py                # Tkinter-based GUI interface
├── tv_tools.py                   # Utility tools for data processing
├── Complete_Pack_Info_dump/      # Folder for storing complete pack info
│   ├── Production/
│   └── RMA/
├── data/                         # Data folder
│   └── pack_info.json            # JSON file containing pack information
├── source/                       # Source files
│   └── Communications Records 20241105_1421 1.txt
├── Test_Result_Dump_New/         # Test result dumps
│   ├── Production/
│   └── RMA/
└── __pycache__/                  # Python cache files
```

---

## Requirements

To run this program, you need the following:

- **Python**: Version 3.8 or higher.
- **Required Libraries**: Install the dependencies using the following command:
  ```bash
  pip install -r requirements.txt
  ```
  If a `requirements.txt` file is not provided, ensure the following libraries are installed:
  - `tkinter` (built-in with Python)
  - `json`
  - Any other dependencies used in the scripts.

---

## Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-repo/BMS_Final_Check.git
   cd BMS_Final_Check
   ```

2. **Install Dependencies**:
   Install the required Python libraries:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the System**:
   - Update `config.json` for production settings.
   - Update `configRMA.json` for RMA settings.
   - Ensure test result files are placed in the appropriate directories:
     - `Test_Result_Dump_New/Production/` for production results.
     - `Test_Result_Dump_New/RMA/` for RMA results.

---

## Usage


### 1. Running the Tkinter GUI

The Tkinter GUI provides a desktop-based graphical interface. To launch the GUI, run:
```bash
python tkinter_gui.py
```

Follow the on-screen instructions to interact with the system.

### 2. Processing Data

The `tv_tools.py` script includes utility functions for processing and analyzing test data. To use it, run:
```bash
python tv_tools.py
```

You can modify the script to suit your specific data processing needs.

### 3. Managing Test Results

- Place production test results in the `Test_Result_Dump_New/Production/` directory.
- Place RMA test results in the `Test_Result_Dump_New/RMA/` directory.
- Use the provided scripts to process and analyze the results.

---

## Configuration

The program uses JSON configuration files for customization:

- **`config.json`**: Contains settings for production units.
- **`configRMA.json`**: Contains settings for RMA units.
- **`Login.json`**: Stores login credentials or other authentication details.

To modify the configuration:
1. Open the respective JSON file in a text editor.
2. Update the fields as needed.
3. Save the file.

---

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository.
2. Create a new branch for your feature or bug fix:
   ```bash
   git checkout -b feature-name
   ```
3. Commit your changes:
   ```bash
   git commit -m "Description of changes"
   ```
4. Push to your fork:
   ```bash
   git push origin feature-name
   ```
5. Submit a pull request.

---
