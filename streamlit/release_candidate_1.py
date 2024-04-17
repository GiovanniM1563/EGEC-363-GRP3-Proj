import streamlit as st
import ast
import sqlite3
import base64
import datetime

# Function to create a new database if it doesn't exist
import sqlite3

def create_new_database(db_name):
    """
    Creates a new SQLite database with the given name and returns the connection object.

    Parameters:
    db_name (str): The name of the database to be created.

    Returns:
    con (sqlite3.Connection): The connection object to the newly created database.
    """
    con = sqlite3.connect(db_name)
    cur = con.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS db(name TEXT, letters TEXT, note TEXT, due_date TEXT)')
    con.commit()
    return con

# Create databases for each button
db1_con = create_new_database('db1.db')
db2_con = create_new_database('db2.db')
db3_con = create_new_database('db3.db')
db4_con = create_new_database('db4.db')  # New database

# Function to add a new row to a specific database
def add_new_row(con):
    """
    Adds a new row to the 'db' table in the database.
    where DB is one of the categories of the Kanban Table (Backlog, To Do, Doing, Done)

    Parameters:
    - con: The database connection object.

    Returns:
    None
    """
    cur = con.cursor()
    cur.execute('INSERT INTO db(name, letters, note, due_date) VALUES(?,?,?,?)', ('', '[]', '', ''))
    con.commit()
    st.experimental_rerun()  # Trigger rerun after adding a new row

# Function to duplicate a row to the fourth database
def duplicate_row_to_fourth_database(row, source_con, dest_con):
    """
    Duplicate a row from the source database to the destination database.
    IN this case, the source database is the current database and the destination database is the done (fourth) database.
    Args:
        row (tuple): The row to be duplicated.
        source_con: The connection to the source database.
        dest_con: The connection to the destination database.

    Returns:
        None
    """
    if dest_con is None:
        st.warning("Destination database connection is not provided.")
        return
    cur_source = source_con.cursor()
    cur_dest = dest_con.cursor()
    cur_source.execute('SELECT name, letters, note, due_date FROM db WHERE rowid=?;', (row[0],))
    data = cur_source.fetchone()
    if data:
        cur_dest.execute('INSERT INTO db(name, letters, note, due_date) VALUES(?,?,?,?)', data)
        dest_con.commit()
        cur_source.execute('DELETE FROM db WHERE rowid=?;', (row[0],))  # Delete the row from the source database
        source_con.commit()
        st.experimental_rerun()  # Trigger rerun after duplicating and deleting the row

# Function to convert database index to name
def db_index_to_name(db_index):
    """
    Converts a database index to its corresponding name.

    Args:
        db_index (int): The index of the database entry.

    Returns:
        str: The name corresponding to the given database index.
             Returns 'Unknown' if the index is not recognized.
    """
    if db_index == 1:
        return 'Backlog'
    elif db_index == 2:
        return 'To Do'
    elif db_index == 3:
        return 'Doing'
    elif db_index == 4:
        return 'Done'
    else:
        return 'Unknown'

# Function to generate human-readable text for database contents
def generate_database_contents_text():
    """
    Generates a formatted text representation of the contents of multiple databases.

    Returns:
        str: The formatted text representation of the database contents.
    """
    contents = ""
    for i, db_con in enumerate([db1_con, db2_con, db3_con, db4_con], start=1):
        db_name = db_index_to_name(i)
        contents += f"{db_name}:\n"
        cur = db_con.cursor()
        for row in cur.execute('SELECT name, letters, note, due_date FROM db ORDER BY name'):
            due_date = row[3] if row[3] else ""  # Convert None to empty string
            contents += f"  Task: {row[0]}\n"
            contents += f"  Type: {', '.join(ast.literal_eval(row[1]))}\n"
            contents += f"  Description: {row[2]}\n"
            contents += f"  Due Date: {due_date}\n"
            contents += "\n"
    return contents

# Function to download database contents as a text file
def download_database_contents():
    """
    Downloads the contents of the database as a text file.

    Returns:
        None
    """
    contents = generate_database_contents_text()
    # Convert contents to bytes
    contents = contents.encode('utf-8')
    b64 = base64.b64encode(contents).decode()
    href = f'<a href="data:file/txt;base64,{b64}" download="database_contents.txt">Download Database Contents</a>'
    st.sidebar.markdown(href, unsafe_allow_html=True)

# Function to display and manage forms for a specific database
def display_forms(con, db_index, other_db_con):
    """
    Display forms for each row in the database and handle form submissions.

    This function retrieves rows from a database table and displays a form for each row. The form allows users to edit
    the task name, type, due date, and description. The function also handles form submissions, updating the database
    with the edited values.

    Args:
        con (connection): The database connection.
        db_index (int): The index of the current database AKA Which Database (Backlog = 1, To Do = 2, Doing = 2, Done = 4)
        other_db_con (connection): The connection to the other database (Which database we would move data to when marking done (In this Case database 4 for Done)).

    Returns:
        None
    """
    cur = con.cursor()
    for row in cur.execute('SELECT rowid, name, letters, note, due_date FROM db ORDER BY name'):
        # Check if there's a date in the description and calculate days until that date
        days_until = days_until_date(row[4])
        with st.expander(f'{row[1]} -  {db_index_to_name(db_index)} - {days_until}'):
            days_until_text = f" - {days_until}" if days_until is not None else ""
            with st.form(f'ID-{db_index}-{row[0]}{days_until_text}'):  # Include days until text in the form title
                name = st.text_input('Task', row[1])
                letters = st.multiselect('Type', ['QA', 'Bug Fix', 'Research','Client Request','Implementation','Rework'], ast.literal_eval(row[2]))
                due_date = None
                if row[4]:
                    try:
                        due_date = datetime.datetime.strptime(row[4], '%Y-%m-%d')
                    except ValueError:
                        st.warning("Invalid due date format in database.")
                due_date = st.date_input('Due Date', due_date,format="MM/DD/YYYY")
                note = st.text_area('Description', row[3])
                col1, col2 = st.columns([2, 1])
                with col1:
                    if st.form_submit_button(f'Save'):
                        cur.execute(
                            'UPDATE db SET name=?, letters=?, note=?, due_date=? WHERE rowid=?;', 
                            (name, str(letters), note, due_date.strftime('%Y-%m-%d') if due_date else None, row[0])
                        )
                        con.commit()
                        st.experimental_rerun()  # Trigger rerun after saving changes
                with col2:
                    if st.form_submit_button(f"Delete"):
                        cur.execute('DELETE FROM db WHERE rowid=?;', (row[0],))
                        con.commit()
                        st.experimental_rerun()  # Trigger rerun after deleting row
                    if db_index != 4:  # Only show the button if not in Database 4
                        if st.form_submit_button(f"Mark Done"):
                            # Duplicate row to the fourth database
                            duplicate_row_to_fourth_database(row, con, other_db_con)
                            # Delete the row from the current database
                            cur.execute('DELETE FROM db WHERE rowid=?;', (row[0],))
                            con.commit()
                            st.experimental_rerun()  # Trigger rerun after marking as done



# Function to calculate days until a given date and return formatted string
def days_until_date(date_str):
    """
    Calculate the number of days until a given date.

    Args:
        date_str (str): The date string in the format 'YYYY-MM-DD'.

    Returns:
        str: A string indicating the number of days until the date.
             - If the date is today, it returns "Due Today".
             - If the date is tomorrow, it returns "Due Tomorrow".
             - If the date is in the future, it returns "Due in X days" where X is the number of days.
             - If the date is in the past, it returns "Overdue".
        None: If the date string is empty or the date format is incorrect.
    """
    if not date_str:
        return None  # Return None if the date string is empty

    try:
        date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        today = datetime.datetime.today().date()
        delta = (date_obj - today).days
        if delta == 0:
            return "Due Today"
        elif delta == 1:
            return "Due Tomorrow"
        elif delta > 1:
            return f"Due in {delta} days"
        else:
            return "Overdue"
    except ValueError:
        st.warning("Invalid date format in database.")
        return None  # Return None if the date format is incorrect

        
st.set_page_config(layout="wide")

# Add a button to download database contents in the sidebar
download_database_contents()

# Layout for displaying databases in columns with wider columns
col1, col2, col3, col4 = st.columns([1, 1, 1, 1])  # Adjusted layout with wider columns

# Display forms and "Add to" buttons for each database, each col represents a column IE Column One being the location where all of the Backlog items are displayed and so on    
with col1:
    st.header('Backlog')
    display_forms(db1_con, 1, db4_con)  # Pass db4 connection for duplication
    if st.button('Add to Backlog'):  # 
        add_new_row(db1_con)

with col2:
    st.header('To Do')
    display_forms(db2_con, 2, db4_con)  # Pass db4 connection for duplication
    if st.button('Add to To Do'):  
        add_new_row(db2_con)

with col3:
    st.header('Doing')
    display_forms(db3_con, 3, db4_con)  # Pass db4 connection for duplication
    if st.button('Add to Doing'):
        add_new_row(db3_con) 

with col4:
    st.header('Done')  # New column for the fourth database
    display_forms(db4_con, 4, None)  # No need to pass another database connection
    if st.button('Add to Done'):  
        add_new_row(db4_con)
