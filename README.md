# ALX Backend Python 

This repository contains a series of Python exercises focused on using generators to process data from a MySQL database without loading everything into memory. Each exercise lives in its own folder under `python-generators-0x00/` and comes with a driver script to demonstrate the result.

## Repo structure

alx-backend-python/  
├── python-generators-0x00/  
│ ├── seed.py  
│ ├── 0-main.py  
│ ├── 0-stream\_users.py  
│ ├── 1-main.py  
│ ├── 1-batch\_processing.py  
│ ├── 2-lazy\_paginate.py  
│ ├── 3-main.py  
│ ├── 4-stream\_ages.py  
│ ├── user\_data.csv  
│ └── README.md ← exercise-specific readme  
└── README.md ← this file

    
## Prerequisites

- **Python 3.7 or newer**  
- **MySQL server** accessible on `localhost`  
- A MySQL user with permissions to create databases and tables  
- Environment variable `MYSQL_PASSWORD` set to your MySQL user’s password  
- `pip` packages:
  ```bash
  pip install mysql-connector-python pandas


## Setup

1.  **Clone the repo**
    
        git clone https://github.com/your-username/alx-backend-python.git
        cd alx-backend-python
        
    
2.  **Export your password**
    
        export MYSQL_PASSWORD='your_mysql_password'
        
    
3.  **Download the CSV**  
    Inside `python-generators-0x00/`:
    
    Download the sample data from [this S3 URL](https://s3.amazonaws.com/alx-intranet.hbtn.io/uploads/misc/2024/12/3888260f107e3701e3cd81af49ef997cf70b6395.csv?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIARDDGGGOUSBVO6H7D%2F20250706%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20250706T082325Z&X-Amz-Expires=86400&X-Amz-SignedHeaders=host&X-Amz-Signature=a04d19421890243e499a32a27ed516a2aa816bda9faddca964c64cc65c9e52eb). 
    If you want to fetch it from the terminal, use:
    
        curl -L "https://s3.amazonaws.com/alx-intranet.hbtn.io/uploads/misc/2024/12/3888260f107e3701e3cd81af49ef997cf70b6395.csv?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIARDDGGGOUSBVO6H7D%2F20250706%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20250706T082325Z&X-Amz-Expires=86400&X-Amz-SignedHeaders=host&X-Amz-Signature=a04d19421890243e499a32a27ed516a2aa816bda9faddca964c64cc65c9e52eb" -o user_data.csv
        
    

## Exercises

Each folder under `python-generators-0x00/` has its own instructions and a driver script.

1.  **Getting started with generators**
    
    *   **File**: `seed.py`, `0-main.py`
        
    *   **What it does**: Creates database `ALX_prodev`, table `user_data`, loads CSV, then prints first 5 rows.
        
2.  **Stream users one by one**
    
    *   **File**: `0-stream_users.py`, `1-main.py`
        
    *   **What it does**: Implements `stream_users()` generator that yields one user dict at a time.
        
3.  **Batch processing**
    
    *   **File**: `1-batch_processing.py`, `2-main.py`
        
    *   **What it does**: Fetches rows in batches, filters users over age 25, prints them.
        
4.  **Lazy pagination**
    
    *   **File**: `2-lazy_paginate.py`, `3-main.py`
        
    *   **What it does**: Fetches pages of users on demand, yields each page only when iterated.
        
5.  **Memory-efficient aggregation**
    
    *   **File**: `4-stream_ages.py`
        
    *   **What it does**: Streams only the `age` column, computes average age without loading all rows.
        

## How to run

Inside `python-generators-0x00/`, pick the exercise number:

    # Exercise 0
    ./0-main.py
    
    # Exercise 1
    ./1-main.py
    
    # Exercise 2
    ./2-main.py
    
    # Exercise 3
    ./3-main.py
    
    # Exercise 4
    ./4-stream_ages.py
    

If a script is not executable, run:

    python3 <script>.py
    

## Notes

*   All generators use at most one or two loops and never pull the entire result set into memory.
    
*   Cleanup of database connections is handled where safe; in early-exit cases you may see open-cursor warnings. Those can be ignored for these exercises.
    

* * *