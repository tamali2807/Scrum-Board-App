import streamlit as st
import pandas as pd
from sqlalchemy.exc import SQLAlchemyError
import time
from st_aggrid import AgGrid, GridOptionsBuilder

def get_connection():
    """Establish connection to MySQL Database."""
    # Initialize connection.
    return st.connection('mysql', type='sql')

def init_db():
    """Initialize the stories table if it does not exist."""
    conn = get_connection()
    conn.session.execute('''
        CREATE TABLE IF NOT EXISTS stories (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            assignee VARCHAR(255) NOT NULL,
            time_allotted INT NOT NULL,
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,
            status ENUM('To Do', 'In Progress', 'Completed') NOT NULL
        );
    ''')
    conn.session.commit()

def create_story(title, assignee, time_allotted, start_date, end_date, status):

    try:
        conn = get_connection()        
        with conn.session as session:
            session.execute('''
                INSERT INTO stories (title, assignee, time_allotted, start_date, end_date, status)
                VALUES (:title, :assignee, :time_allotted, :start_date, :end_date, :status);
            ''', 
            {
                "title": title,
                "assignee": assignee,
                "time_allotted": time_allotted,
                "start_date": start_date,
                "end_date": end_date,
                "status": status
            }
            )
            session.commit()
            st.rerun()

    except SQLAlchemyError as e:
        st.error(f"Database error: {str(e)}")
        print(f"Database error: {str(e)}")

    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")
        print(f"Unexpected error: {str(e)}")


def get_stories():
    conn = get_connection()
    rows = conn.query("SELECT * FROM stories",ttl=0)
    return rows

def delete_story(story_id):
    conn = get_connection()
    with conn.session as session:
        result=session.execute('''
                        DELETE FROM stories where id=(:story_id)''',
                        {
                            "story_id":story_id
                        })
        session.commit()


        if result.rowcount==0:
            st.warning("Story ID not available!")
        else:
            st.success("Story Deleted Successfully!")
            time.sleep(2)
            st.rerun()


def update_story(story_id, status):
    conn = get_connection()
    with conn.session as session:
        result=session.execute('''UPDATE stories SET status=(:status) where id=(:story_id)''',{"status":status,"story_id":story_id})
        session.commit()

        if result.rowcount==0:
            st.warning("Story Id not available!")
        else:
            st.success("Story updated successfully!")
            time.sleep(2)
            st.rerun()
         
    
def create_stories():
    st.header("Create a New Story")

    # Form to create a new ticket
    with st.form("ticket_form"):
        title = st.text_input("Story Title")
        assignee = st.text_input("Assignee")
        time_allotted = st.number_input("Time Allotted (in hours)", min_value=1, step=1)
        start_date = st.date_input("Start Date")
        end_date = st.date_input("End Date")
        status = st.selectbox("Status", ["To Do", "In Progress", "Completed"])
        submit = st.form_submit_button("Create Story")

        if submit:
            if title and assignee:
                create_story(title, assignee, time_allotted, start_date, end_date, status)
                st.success("Story created successfully!")
            else:
                st.error("Please fill in all required fields.")

    # Display current tickets
    stories = get_stories()
    if stories.any:
        st.subheader("Current Stories")
        ticket_df = pd.DataFrame(stories)

        
        # Format date columns
        if 'start_date' in ticket_df.columns:
            ticket_df['start_date'] = pd.to_datetime(ticket_df['start_date']).dt.strftime('%Y-%m-%d')
        if 'end_date' in ticket_df.columns:
            ticket_df['end_date'] = pd.to_datetime(ticket_df['end_date']).dt.strftime('%Y-%m-%d')

        # Configure AgGrid with filtering enabled for all columns
        gb = GridOptionsBuilder.from_dataframe(ticket_df)

        for col in ticket_df.columns:
            if ticket_df[col].dtype == "object":  # Text columns
                gb.configure_column(col, filter="agTextColumnFilter")
            else:  # Numeric or Date columns
                gb.configure_column(col, filter="agNumberColumnFilter")

        # Configure AgGrid with consistent filter icon positioning and specific column widths
        gb = GridOptionsBuilder.from_dataframe(ticket_df)
        for col in ticket_df.columns:
            gb.configure_column(col, filter=True, headerClass='align-filter-right')

        grid_options = gb.build()

        # Apply custom CSS to align filter icons consistently
        st.markdown(
            """
            <style>
                .align-filter-right .ag-header-cell-filter { justify-content: right !important; }
                .align-filter-right .ag-header-cell-label { justify-content: right !important; }
            </style>
            """, unsafe_allow_html=True
        )

        # Display dataframe with AgGrid
        AgGrid(ticket_df,gridOptions=grid_options, fit_columns_on_grid_load=False)

        #st.dataframe(ticket_df,hide_index=True)


        # Option to delete or update a story
        with st.expander("Manage Stories",expanded=st.session_state.get("expander_open", True)):
            story_id = st.number_input("Story ID to delete/update", min_value=1, step=1)
            action = st.radio("Action", ["Delete", "Update Status"])

            if action == "Update Status":
                new_status = st.selectbox("New Status", ["To Do", "In Progress", "Completed"])
                if st.button("Update Story"):
                    update_story(story_id, new_status)

            elif action == "Delete":
                if st.button("Delete Story"):
                    delete_story(story_id)
