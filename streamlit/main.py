import streamlit as st
import sqlite3

# Back End
con = sqlite3.connect("db.db")
cur = con.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS tasks(title TEXT, desc TEXT, type TEXT)")

# Function to add a new task
def add_task(title, description, task_type):
    try:
        cur.execute('INSERT INTO tasks(title, desc, type) VALUES(?,?,?)', (title, description, task_type))
        con.commit()
        st.sidebar.success("Task added successfully")
    except sqlite3.Error as e:
        st.sidebar.error(f"Error adding task to database: {e}")

# Function to update an existing task
def update_task(new_title, new_description, task_type, task_id):
    try:
        cur.execute('UPDATE tasks SET title=?, desc=?, type=? WHERE rowid=?', (new_title, new_description, task_type, task_id))
        con.commit()
        st.sidebar.success("Task updated successfully")
        st.rerun()
    except sqlite3.Error as e:
        st.sidebar.error(f"Error updating task in database: {e}")
    

# Function to delete an existing task
def delete_task(task_id):
    try:
        cur.execute('DELETE FROM tasks WHERE rowid=?', (task_id,))
        con.commit()
        st.sidebar.success("Task deleted successfully")
        st.rerun()
    except sqlite3.Error as e:
        st.sidebar.error(f"Error deleting task from database: {e}")

def done_task(task_id):
    try:
        cur.execute('UPDATE tasks SET type=? WHERE rowid=?', ('completed', task_id))
        con.commit()
        st.sidebar.success("Task updated successfully")
        st.rerun()
    except sqlite3.Error as e:
        st.sidebar.error(f"Error updating task in database: {e}")
# Front End
#Add task

st.set_page_config(layout="wide")
st.sidebar.header("Add New Task")
title = st.sidebar.text_input("Title")
description = st.sidebar.text_area("Description")
options = ["todo", "inprogress", "completed", "dropped"]
dropdown_value = st.sidebar.selectbox("Select an option", options)

submit_button_clicked = st.sidebar.button("Submit")

if submit_button_clicked:
    add_task(title, description, dropdown_value)

# Display the kanban board
st.header("Kanban Board")
cols = st.columns(4)
for index, task_type in enumerate(options):
    with cols[index]:
        st.subheader(task_type.capitalize())
        cur.execute("SELECT rowid, title, desc FROM tasks WHERE type=?", (task_type,))
        tasks = cur.fetchall()
        for task in tasks:
            task_id = task[0]
            with st.expander(f"{task[1]}"):
                new_title = st.text_input(f"Title:", value=task[1], key=f"title_{task_id}")
                new_description = st.text_area(f"Description:", value=task[2], key=f"description_{task_id}")
                new_task_type = st.selectbox(f"Task Type:", options, index=options.index(task_type), key=f"type_{task_id}")

                update_button = st.button(f"Save", key=f"update_{task[0]}")
                delete_button = st.button(f"Delete", key=f"delete_{task[0]}")
                if update_button:
                    update_task(new_title, new_description, new_task_type, task_id)       
                if delete_button:
                    delete_task(task_id)

