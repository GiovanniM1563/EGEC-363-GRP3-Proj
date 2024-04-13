import streamlit as st #pip install streamlit
import ast #standard library
import sqlite3 #standard library


#Back End

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

# Function to add a new row to a specific database
def add_new_row(con):
    cur = con.cursor()
    cur.execute('INSERT INTO db(name, letters, note) VALUES(?,?,?)', ('', '[]', ''))
    con.commit()



# Front End

# Function to display and manage forms for a specific database
def display_forms(con, db_index):
    cur = con.cursor()
    for row in cur.execute('SELECT rowid, name, letters, note FROM db ORDER BY name'):
        with st.expander(f'{row[1]} - Database {db_index}'):
            with st.form(f'ID-{db_index}-{row[0]}'):
                name = st.text_input('Name', row[1])
                letters = st.multiselect('Letters', ['A', 'B', 'C'], ast.literal_eval(row[2]))
                note = st.text_area('Note', row[3])
                if st.form_submit_button(f'Save-{db_index}-{row[0]}'):
                    cur.execute(
                        'UPDATE db SET name=?, letters=?, note=? WHERE rowid=?;', 
                        (name, str(letters), note, row[0])
                    )
                    con.commit()
                    st.experimental_rerun()
                if st.form_submit_button(f"Delete-{db_index}-{row[0]}"):
                    cur.execute('DELETE FROM db WHERE rowid=?;', (row[0],))
                    con.commit()
                    st.experimental_rerun()

# Layout for displaying databases in columns
col1, col2, col3 = st.columns(3)

# Add buttons for each database
with col1:
    st.header('Database 1')
    if st.button('Add New Row - Database 1'):
        add_new_row(db1_con)
    display_forms(db1_con, 1)

with col2:
    st.header('Database 2')
    if st.button('Add New Row - Database 2'):
        add_new_row(db2_con)
    display_forms(db2_con, 2)

with col3:
    st.header('Database 3')
    if st.button('Add New Row - Database 3'):
        add_new_row(db3_con)
    display_forms(db3_con, 3)
