# Getting Started with Python Generators

This exercise sets up a MySQL database and uses a Python generator to stream rows from the table one at a time.

## Files

*   `seed.py`  
    Contains functions to bootstrap the database:
    
    *   `connect_db()` – connect to MySQL server
        
    *   `create_database(connection)` – create the `ALX_prodev` database
        
    *   `connect_to_prodev()` – connect to the `ALX_prodev` database
        
    *   `create_table(connection)` – create the `user_data` table
        
    *   `insert_data(connection, data_path)` – load data from CSV into the table
        
*   `0-main.py`  
    Driver script that:
    
    1.  Connects to the server
        
    2.  Creates the database and table
        
    3.  Imports data from `user_data.csv`
        
    4.  Verifies the database and prints the first 5 rows
        
*   `user_data.csv`  
    Sample data file with columns: `user_id`, `name`, `email`, `age`.
    

## Prerequisites

*   Python 3.6+
    
*   MySQL server running locally
    
*   `mysql-connector-python` Python package
    

## Setup

1.  **Install dependencies**
    
        pip install mysql-connector-python
        
    
2.  **Download the sample data**
    
        curl -L "https://s3.amazonaws.com/alx-intranet.hbtn.io/uploads/misc/2024/12/3888260f107e3701e3cd81af49ef997cf70b6395.csv" \
          -o user_data.csv
        
    
3.  **Set your MySQL password**
    
    Export the root password so the scripts can connect:
    
        export MYSQL_PASSWORD='your_mysql_root_password'
        
    
4.  **Make the driver executable**
    
        chmod +x 0-main.py
        
    

## Usage

Run the bootstrap and streaming script:

    ./0-main.py
    

You should see output similar to:

    connection successful
    Table 'user_data' created successfully or already exists.
    Database ALX_prodev is present
    [('00234e50-34eb-4ce2-94ec-26e3fa749796', 'Dan Altenwerth Jr.', ...)]
    

This confirms that the database is created, the table is populated, and the first five rows are printed.

## Notes

*   The generator in `seed.py` (if implemented) can be used to stream rows without loading the entire table into memory.
    
*   You can inspect or extend the `seed.stream_user_data()` function to yield rows one by one for larger datasets.