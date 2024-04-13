import streamlit as st
import ast
import sqlite3
import base64

# Function to create a new database if it doesn't exist
def create_new_database(db_name):
    con = sqlite3.connect(db_name)
    cur = con.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS db(name TEXT, letters TEXT, note TEXT)')
    con.commit()
    return con

# Create databases for each button
db1_con = create_new_database('db1.db')
db2_con = create_new_database('db2.db')
db3_con = create_new_database('db3.db')
db4_con = create_new_database('db4.db')  # New database

# Function to add a new row to a specific database
def add_new_row(con):
    cur = con.cursor()
    cur.execute('INSERT INTO db(name, letters, note) VALUES(?,?,?)', ('', '[]', ''))
    con.commit()

# Function to duplicate a row to the fourth database
def duplicate_row_to_fourth_database(row, source_con, dest_con):
    if dest_con is None:
        st.warning("Destination database connection is not provided.")
        return
    cur_source = source_con.cursor()
    cur_dest = dest_con.cursor()
    cur_source.execute('SELECT name, letters, note FROM db WHERE rowid=?;', (row[0],))
    data = cur_source.fetchone()
    if data:
        cur_dest.execute('INSERT INTO db(name, letters, note) VALUES(?,?,?)', data)
        dest_con.commit()



def db_index_to_name(db_index):
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

    contents = ""
    for i, db_con in enumerate([db1_con, db2_con, db3_con, db4_con], start=1):
        db_name = db_index_to_name(i)
        contents += f"{db_name}:\n"
        cur = db_con.cursor()
        for row in cur.execute('SELECT name, letters, note FROM db ORDER BY name'):
            contents += f"  Task: {row[0]}\n"
            contents += f"  Type: {', '.join(ast.literal_eval(row[1]))}\n"
            contents += f"  Description: {row[2]}\n"
            contents += "\n"

    return contents

# Function to download database contents as a text file
def download_database_contents():
    contents = generate_database_contents_text()

    # Convert contents to bytes
    contents = contents.encode('utf-8')
    b64 = base64.b64encode(contents).decode()
    href = f'<a href="data:file/txt;base64,{b64}" download="database_contents.txt">Download Database Contents</a>'
    st.sidebar.markdown(href, unsafe_allow_html=True)

# Function to display and manage forms for a specific database
def display_forms(con, db_index, other_db_con):
    cur = con.cursor()
    for row in cur.execute('SELECT rowid, name, letters, note FROM db ORDER BY name'):
        with st.expander(f'{row[1]} -  {db_index_to_name(db_index)}'):
            with st.form(f'ID-{db_index}-{row[0]}'):
                name = st.text_input('Task', row[1])
                letters = st.multiselect('Type', ['QA', 'Bug Fix', 'Research','Client Request','Implementation','Rework'], ast.literal_eval(row[2]))
                note = st.text_area('Description', row[3])
                col1, col2 = st.columns([2, 1])
                with col1:
                    if st.form_submit_button(f'Save'):
                        cur.execute(
                            'UPDATE db SET name=?, letters=?, note=? WHERE rowid=?;', 
                            (name, str(letters), note, row[0])
                        )
                        con.commit()
                        st.experimental_rerun()
                with col2:
                    if st.form_submit_button(f"Delete"):
                        cur.execute('DELETE FROM db WHERE rowid=?;', (row[0],))
                        con.commit()
                        st.experimental_rerun()
                    if db_index != 4:  # Only show the button if not in Database 4
                        if st.form_submit_button(f"Mark Done"):
                            # Duplicate row to the fourth database
                            duplicate_row_to_fourth_database(row, con, other_db_con)
                            # Delete the row from the current database
                            cur.execute('DELETE FROM db WHERE rowid=?;', (row[0],))
                            con.commit()
                            st.experimental_rerun()

# Set the page layout to wide
st.set_page_config(layout="wide")

# Add a button to download database contents in the sidebar
download_database_contents()

# Layout for displaying databases in columns with wider columns
col1, col2, col3, col4 = st.columns([1, 1, 1, 1])  # Adjusted layout with wider columns

# Add buttons for each database
with col1:
    st.header('Backlog')
    if st.button('Add to Backlog'):  # Adjusted button width
        add_new_row(db1_con)
    display_forms(db1_con, 1, db4_con)  # Pass db4 connection for duplication

with col2:
    st.header('To Do')
    if st.button('Add to To Do'):  # Adjusted button width
        add_new_row(db2_con)
    display_forms(db2_con, 2, db4_con)  # Pass db4 connection for duplication

with col3:
    st.header('Doing')
    if st.button('Add to Doing'):  # Adjusted button width
        add_new_row(db3_con)
    display_forms(db3_con, 3, db4_con)  # Pass db4 connection for duplication

with col4:
    st.header('Done')  # New column for the fourth database
    if st.button('Add to Done'):  # Adjusted button width
        add_new_row(db4_con)
    display_forms(db4_con, 4, None)  # No need to pass another database connection
