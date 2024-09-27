import streamlit as st
import pandas as pd
from tabulate import tabulate

st.set_page_config(page_title="Blood Bowl GPT Prompt Generator", layout="wide")

st.title("Blood Bowl GPT Prompt Generator")

st.markdown("""
Welcome to the Blood Bowl GPT Prompt Generator! Fill in the details below, upload your data file, and generate a GPT prompt for creating engaging news and reports for your Blood Bowl League.
""")

# --- Logo or Image ---

st.sidebar.title("League Logo")

logo_option = st.sidebar.selectbox("Do you want to add a league logo?", ["No", "Yes"])

if logo_option == "Yes":
    logo_file = st.sidebar.file_uploader("Upload an image file", type=["jpg", "jpeg", "png"])
    if logo_file is not None:
        st.sidebar.image(logo_file, use_column_width=True)
else:
    st.sidebar.info("No logo will be added.")

# --- User Inputs ---

# Divide into two columns
col1, col2 = st.columns(2)

with col1:
    # Type of Report
    type_of_report = st.selectbox(
        "Type of Report:",
        ["Match Summary", "Player Statistics", "Injuries", "League Updates", "Scandals", "Tactical Analysis", "Other"]
    )

    # If 'Other' is selected, provide a text input
    if type_of_report == "Other":
        type_of_report = st.text_input("Please specify the type of report:")

    # League Name
    league_name = st.text_input("League Name:")

    # Tone and Style
    tone_style = st.text_input("Tone and Style:", help="e.g., humorous and satirical, serious and analytical, dramatic, etc.")

    # Format and Length
    format_length = st.text_input("Format and Length:", help="e.g., Newspaper article format, approximately 500 words.")

with col2:
    # Reporter Character Name and Description
    st.subheader("Reporter Character")
    reporter_name = st.text_input("Character Name:")
    reporter_description = st.text_area("Character Description:", height=100, help="Describe the personality, style, and any quirks.")

    # Additional Details
    additional_details = st.text_area("Additional Details:", height=150, help="Include any quotes, interviews, or specific events you want highlighted.")

# Narrative and Lore (full width)
st.subheader("Narrative and Lore")
narrative_lore = st.text_area("Add any specific narratives or lore to include:", height=150)

# --- File Upload ---

st.subheader("Upload League Information and Data")

uploaded_file = st.file_uploader("Choose a CSV file", type="csv", help="Upload a CSV file containing league data.")

if uploaded_file is not None:
    try:
        data_df = pd.read_csv(uploaded_file)
        st.success("File uploaded successfully!")
        st.dataframe(data_df)
    except Exception as e:
        st.error(f"Error reading the CSV file: {e}")
        data_df = None
else:
    data_df = None
    st.info("Awaiting CSV file upload.")

# --- Generate Prompt ---

if st.button("Generate GPT Prompt"):
    # Input Validation
    missing_fields = []
    if not type_of_report:
        missing_fields.append("Type of Report")
    if not league_name:
        missing_fields.append("League Name")
    if not reporter_name:
        missing_fields.append("Reporter Character Name")
    if not reporter_description:
        missing_fields.append("Reporter Character Description")
    if not tone_style:
        missing_fields.append("Tone and Style")
    if not format_length:
        missing_fields.append("Format and Length")

    if missing_fields:
        st.error(f"The following fields are required: {', '.join(missing_fields)}")
    else:
        # Prepare the data string
        if data_df is not None:
            # Option to select formatting
            data_format_option = st.selectbox(
                "Select data formatting for the prompt:",
                ["Markdown Table", "Bullet Points"]
            )

            if data_format_option == "Markdown Table":
                # Convert DataFrame to Markdown table
                data_str = tabulate(data_df, headers='keys', tablefmt='pipe', showindex=False)
            elif data_format_option == "Bullet Points":
                # Convert DataFrame to bullet points
                data_str = ""
                for index, row in data_df.iterrows():
                    row_items = [f"**{col}:** {row[col]}" for col in data_df.columns]
                    data_str += "- " + "; ".join(row_items) + "\n"
        else:
            data_str = "No data provided."

        # Compile the GPT prompt
        prompt = f"""
You are a seasoned sports journalist in the fantastical and brutal world of Blood Bowl. Your task is to write a **{type_of_report}** for the **{league_name}**. The report should be engaging and entertaining for both players in the league and fans of Blood Bowl in general. Assume the audience does not need an understanding of Blood Bowl mechanics to enjoy the content.

**Please use the following information to craft your report:**

1. **Type of Report:** {type_of_report}

2. **League Information and Data:**

{data_str}

3. **Narrative and Lore:**
{narrative_lore}

4. **Reporter Character:**
- **Character Name:** {reporter_name}
- **Character Description:** {reporter_description}

5. **Tone and Style:** {tone_style}

6. **Format and Length:** {format_length}

7. **Additional Details:**
{additional_details}

---
**Now, please write the report accordingly.**
"""

        st.subheader("Generated GPT Prompt")
        st.text_area("GPT Prompt:", value=prompt, height=500)
        st.markdown("**Copy the prompt above and paste it into your GPT interface to generate the report.**")
