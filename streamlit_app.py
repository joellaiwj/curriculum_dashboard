from numpy import *
import plotly.express as px
import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd
import os
from wordcloud import WordCloud
import plotly.graph_objects as go

st.set_page_config(page_title="Curriculum Planning Dashboard",page_icon=":books:",layout="wide")

st.title(":books: NTU Curriculum Planning Dashboard")

filename = os.chdir(r"C:\Users\joellai\Desktop\Curriculum Planning Dashboard")
files = "students_courses.xlsx"
df_student = pd.read_excel(files,sheet_name="student-course")
df_course = pd.read_excel(files,sheet_name="course-skill")
df_ga = pd.read_excel(files,sheet_name="course-GA")
df_industry = pd.read_excel(files,sheet_name="industry-skill")
df_details = pd.read_excel(files,sheet_name="course-info")

# Iterate over the DataFrame rows to populate the dictionary
course_data = {}

for index, row in df_details.iterrows():
    code = row[0]
    title = row[1]
    units = row[2]
    description = row[4]
    
    # Add the course data to the dictionary
    course_data[code] = {"Course title": title, "Academic units": units, "Course description": description}

N = int(0.5*len(df_student['Student'].unique()))

Program = ":orange[Bachelor of Science (Physics and Applied Physics)]"
industry = df_industry['Industry'].unique()
yos = df_student['Year'].unique()
st.sidebar.header("Customization")

with st.sidebar:
    selected_options = st.multiselect('Select specific industry combinations:', industry, default=[])

    selected_yos = st.multiselect('Select year of graduation:', yos, default=[])
    
    st.sidebar.markdown('---')
    st.sidebar.subheader("Course Information")
    
    # Display courses in the sidebar with an interactive way to show details
    selected_course = st.sidebar.selectbox('Select a course code to see more details:', list(course_data.keys()))
    
    course_details = course_data[selected_course]
    st.sidebar.write(f"**Course Title:** {course_details['Course title']}")
    st.sidebar.write(f"**Academic Units:** {course_details['Academic units']}")
    st.sidebar.write(f"**Description:** {course_details['Course description']}")
    
if len(selected_options) == 0:
    selected_options = industry
    industry_title = "all industries"
else:
    industry_title = "selected industries"

if len(selected_yos) == 0:
    selected_yos = yos
    yos_title = "all years of graduation"
else:
    yos_title = "selected years of graduation"



st.header("Overview for "+Program)

col1,col2 = st.columns((2))

with col1:
    st.subheader("Graduate Attributes")
    fig = px.histogram(df_ga, x="Attribute",color="Level")
    st.plotly_chart(fig,use_container_width=True,height=400)

with col2:
    st.subheader("Programme Skills Word Cloud")
    def excel_column_to_string(df, column_name):
        df = df_course
        # Convert the specified column to a string, with each item separated by a comma
        text = ', '.join(f'"{item.replace("skills", "").strip()}"' for item in df[column_name].astype(str)).lower()
        return text
    
    text = excel_column_to_string(df_course, 'Skill')

    # Create and generate a word cloud image:
    wordcloud = WordCloud().generate(text)
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    st.pyplot(plt)
    
    st.set_option('deprecation.showPyplotGlobalUse', False)


st.header("Comparison to :green[Industry Data]")
course_types = df_details['Type'].unique()
course_type = st.multiselect('Type of course:', course_types, default=course_types)
col3,col4 = st.columns((2))

def filter_skills_by_industry(dataframe, industry, s_type):
    # Filter by industry
    industry_df = dataframe[dataframe['Industry'].isin(industry)]
    
    for _ in s_type:
        # Filter emerging skills, assuming '1' indicates emerging skills
        skills_df = industry_df[industry_df[s_type] == 1]
    
    return skills_df


with col3:
    st.subheader("Emerging Industry Skills")
    
    emerging_skills_df = filter_skills_by_industry(df_industry, selected_options, "Emerging")["Skill"]
    emerging_skills_df = emerging_skills_df.sort_values(ascending=False)

    # Create a course to skill mapping
    courses = {}
    for index, row in df_course.iterrows():
        course, skill = row['Course'], row['Skill']  # Adjust column names as necessary
        if course in courses:
            courses[course].append(skill)
        else:
            courses[course] = [skill]
    
    courses = {k: courses[k] for k in sorted(courses)}
    
    merged_df = pd.merge(df_student, df_details, on='Course_Code')

    filtered_df = merged_df[(merged_df['Year'].isin(selected_yos)) & (merged_df['Type'].isin(course_type))]
    
    # Initialize the emerging skills matrix with courses as columns and emerging skills as rows
    emerging_skills_matrix = pd.DataFrame(0, index=emerging_skills_df, columns=courses.keys())
    
    # Populate the matrix
    for index, row in filtered_df.iterrows():
        course = row['Course_Code']  # Adjust the column name as necessary
        if course in courses:
            for skill in courses[course]:
                if skill in emerging_skills_matrix.index:
                    emerging_skills_matrix.loc[skill, course] += 1
    
    course_counts = filtered_df.groupby('Course_Code').size()
    
    # Generate the heatmap
    fig = go.Figure(data=go.Heatmap(
                       z=emerging_skills_matrix,
                       x=course_counts.index,  # Student names as columns
                       y=emerging_skills_df,  # Skills as rows
                       hoverongaps=False,
                       colorscale="Viridis",  # Color scale can be adjusted as needed
                       showscale=True,
                       zmin=0,
                       zmax=N))  # Hide the color scale
    
    # Update layout
    fig.update_layout(title="Showing data for "+industry_title+" and "+yos_title)
    
    # Show the heatmap in Streamlit
    st.plotly_chart(fig,use_container_width=True,height=400)


with col4:
    st.subheader("Important Industry Skills")
   
    important_skills_df = filter_skills_by_industry(df_industry, selected_options, "Important")["Skill"]
    important_skills_df = important_skills_df.sort_values(ascending=False)
    
    # Initialize an empty dictionary to store the course-skill mapping
    courses = {}
    
    # Create a course to skill mapping
    courses = {}
    for index, row in df_course.iterrows():
        course, skill = row['Course'], row['Skill']  # Adjust column names as necessary
        if course in courses:
            courses[course].append(skill)
        else:
            courses[course] = [skill]
    
    courses = {k: courses[k] for k in sorted(courses)}
    
    merged_df = pd.merge(df_student, df_details, on='Course_Code')

    filtered_df = merged_df[(merged_df['Year'].isin(selected_yos)) & (merged_df['Type'].isin(course_type))]
    
    # Initialize the emerging skills matrix with courses as columns and emerging skills as rows
    important_skills_matrix = pd.DataFrame(0, index=important_skills_df, columns=courses.keys())
    
    # Populate the matrix
    for index, row in filtered_df.iterrows():
        course = row['Course_Code']  # Adjust the column name as necessary
        if course in courses:
            for skill in courses[course]:
                if skill in important_skills_matrix.index:
                    important_skills_matrix.loc[skill, course] += 1
    
    course_counts = filtered_df.groupby('Course_Code').size()
    
    # Generate the heatmap
    fig = go.Figure(data=go.Heatmap(
                       z=important_skills_matrix,
                       x=course_counts.index,  # Student names as columns
                       y=important_skills_df,  # Skills as rows
                       hoverongaps=False,
                       colorscale="Viridis",  # Color scale can be adjusted as needed
                       showscale=True,
                       zmin=0,
                       zmax=N))  # Hide the color scale
    
    # Update layout
    fig.update_layout(title="Showing data for "+industry_title+" and "+yos_title)
    
    # Show the heatmap in Streamlit
    st.plotly_chart(fig,use_container_width=True,height=400)
