import streamlit as st
from bckend import create_new_database, add_new_row, display_forms, db_index_to_name
from chatbot import kanbot
import ast

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

def display_database_contents():
    """
    Displays the contents of the database in an expander within the sidebar as markdown.

    Returns:
        None
    """
    contents = generate_database_contents_text()
    with st.sidebar.expander("Kanban List", expanded=False):  # Adjust the `expanded` parameter as needed
        st.text_area("Contents", value=contents, height=300)

st.set_page_config(layout="wide", page_title="Kanban Board",initial_sidebar_state="collapsed")

# Create databases for each button
db1_con = create_new_database('db1.db')
db2_con = create_new_database('db2.db')
db3_con = create_new_database('db3.db')
db4_con = create_new_database('db4.db')  # New database



kanbot(generate_database_contents_text())
display_database_contents()
# Layout for displaying databases in columns, number denotes ratio of width compared to each other. IE 1:1:1:1 means each column is the same width
col1, col2, col3, col4 = st.columns([1, 1, 1, 1])  

# Display forms and "Add to" buttons for each database, each col represents a column IE Column One being the location where all of the Backlog items are displayed and so on    
with col1:
    st.header('Backlog')
    display_forms(db1_con, 1, db4_con)  # Pass db4 connection for duplication
    if st.button('Add to Backlog'): 
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
    st.header('Done')  
    display_forms(db4_con, 4, None)  # No need to pass another database connection (Done is Done :) )
    if st.button('Add to Done'):  
        add_new_row(db4_con)
