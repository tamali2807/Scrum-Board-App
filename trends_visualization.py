import streamlit as st
import pandas as pd
import plotly.express as px
from create_stories import get_stories

def trends_visualization():
    st.header("Trends Visualization")

    # Fetch stories from the database
    stories = get_stories()

    if stories.any:
        ticket_df = pd.DataFrame(stories)

        # Status count bar chart
        status_count = ticket_df["status"].value_counts().reset_index()
        status_count.columns = ["Status", "Count"]

        fig_status = px.bar(status_count, x="Status", y="Count", color="Status",
                            title="Number of Stories by Status", text="Count")
        fig_status.update_traces(textposition='outside')
        st.plotly_chart(fig_status)

        # Time allotted by assignee pie chart
        time_by_assignee = ticket_df.groupby("assignee")["time_allotted"].sum().reset_index()

        fig_time = px.pie(time_by_assignee, values="time_allotted", names="assignee",
                          title="Time Allotted by Assignee")
        st.plotly_chart(fig_time)

        # Timeline visualization
        ticket_df["start_date"] = pd.to_datetime(ticket_df["start_date"])
        ticket_df["end_date"] = pd.to_datetime(ticket_df["end_date"])

        fig_timeline = px.timeline(ticket_df, x_start="start_date", x_end="end_date", y="title",
                                   color="status", title="story_timelines", labels={"Title": "Story"})
        fig_timeline.update_yaxes(categoryorder="total ascending")
        st.plotly_chart(fig_timeline)
    else:
        st.info("No stories available. Please create stories in the 'Create Stories' tab.")
