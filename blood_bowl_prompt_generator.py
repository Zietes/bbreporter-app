import streamlit as st
import pandas as pd
import json
import os
import re
import time
from datetime import datetime
import plotly.express as px

# --- Set Up the Page ---
st.set_page_config(page_title="Blood Bowl GPT Prompt Generator", layout="wide")
st.title("Blood Bowl GPT Prompt Generator")

# --- Define Base Data Directory ---
BASE_DATA_DIR = os.path.join(os.getcwd(), 'data')

# Create the data directory if it doesn't exist
if not os.path.exists(BASE_DATA_DIR):
    os.makedirs(BASE_DATA_DIR)

# Create directories for images if they don't exist
team_logos_dir = os.path.join(BASE_DATA_DIR, 'team_logos')
player_photos_dir = os.path.join(BASE_DATA_DIR, 'player_photos')

if not os.path.exists(team_logos_dir):
    os.makedirs(team_logos_dir)

if not os.path.exists(player_photos_dir):
    os.makedirs(player_photos_dir)

# --- Function to Validate Filenames ---
def is_valid_filename(filename):
    # Allow only alphanumeric characters, underscores, hyphens, spaces, and periods
    return re.match(r'^[\w\-. ]+$', filename) is not None

# --- Functions to Save and Load Data ---
def save_data_to_file(data, filename):
    if not is_valid_filename(filename):
        st.error("Invalid filename. Use only letters, numbers, underscores, hyphens, spaces, and periods.")
        return

    file_path = os.path.join(BASE_DATA_DIR, filename)
    if os.path.exists(file_path):
        # Append timestamp to filename
        timestamp = int(time.time())
        base, ext = os.path.splitext(filename)
        filename = f"{base}_{timestamp}{ext}"
        file_path = os.path.join(BASE_DATA_DIR, filename)
        st.warning(f"File exists. Saving as {filename} instead.")

    with open(file_path, 'w') as f:
        json.dump(data, f)

def load_data_from_file(filename):
    file_path = os.path.join(BASE_DATA_DIR, filename)
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            return data
    except Exception as e:
        # st.error(f"Error loading JSON file: {e}")
        return None

def save_team_profiles(data, filename='team_profiles.json'):
    save_data_to_file(data, filename)

def load_team_profiles(filename='team_profiles.json'):
    data = load_data_from_file(filename)
    return data if data else []

def save_player_profiles(data, filename='player_profiles.json'):
    save_data_to_file(data, filename)

def load_player_profiles(filename='player_profiles.json'):
    data = load_data_from_file(filename)
    return data if data else []

# --- Initialize Session State ---
if 'league_info' not in st.session_state:
    st.session_state.league_info = {}
if 'matches' not in st.session_state:
    st.session_state.matches = []
if 'injuries' not in st.session_state:
    st.session_state.injuries = []
if 'narratives' not in st.session_state:
    st.session_state.narratives = []

# New session states for team and player profiles
if 'team_profiles' not in st.session_state:
    st.session_state.team_profiles = load_team_profiles()
if 'player_profiles' not in st.session_state:
    st.session_state.player_profiles = load_player_profiles()

# --- Sidebar for Global Settings ---
st.sidebar.title("Global Settings")
st.sidebar.info("Configure global settings for the app.")

# Reporter Details
st.sidebar.subheader("Reporter Character")
reporter_name = st.sidebar.text_input("Character Name", key="reporter_name")
reporter_description = st.sidebar.text_area("Character Description", height=100, key="reporter_description", help="Describe the personality, style, and quirks of the reporter.")

# Tone and Style
tone_style = st.sidebar.selectbox("Tone and Style", ["Humorous", "Serious", "Dramatic", "Satirical"], key="tone_style", help="Select the tone and style for the report.")

# Format and Length
format_length = st.sidebar.text_input("Format and Length", value="Approximately 500 words", key="format_length", help="Specify the format and desired length of the report.")

# --- Tabs for Navigation ---
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "League Info", "Team Profiles", "Player Profiles", "Match Reports",
    "Injury Reports", "Narratives", "Generate Prompt", "Help"
])

# --- League Information ---
with tab1:
    st.header("League Information")
    st.info(f"Data files are saved in: `{BASE_DATA_DIR}`")

    # Welcome Message
    st.write("Welcome to the Blood Bowl GPT Prompt Generator! Use this app to generate engaging reports for your Blood Bowl League.")

    # Save League Info Form
    with st.expander("Add or Edit League Information", expanded=True):
        with st.form("league_info_form"):
            league_name = st.text_input("League Name:", value=st.session_state.league_info.get('league_name', ''), help="Enter the name of your league.")
            league_description = st.text_area("League Description:", value=st.session_state.league_info.get('league_description', ''), help="Provide a description of your league.")
            save_filename = st.text_input("Save League Info As:", value="league_info.json", help="Specify the filename to save the league information.")
            submitted = st.form_submit_button("Save League Information")

            if submitted:
                if not is_valid_filename(save_filename):
                    st.error("Invalid filename. Use only letters, numbers, underscores, hyphens, spaces, and periods.")
                else:
                    st.session_state.league_info['league_name'] = league_name
                    st.session_state.league_info['league_description'] = league_description
                    save_data_to_file(st.session_state.league_info, save_filename)
                    st.success(f"League information saved as `{save_filename}`.")

    # Load League Info Form
    with st.expander("Load League Information"):
        with st.form("league_info_load_form"):
            uploaded_file = st.file_uploader("Choose a JSON file", type="json", key="league_info_upload")
            load_submitted = st.form_submit_button("Load League Information")

            if load_submitted:
                if uploaded_file is not None:
                    loaded_data = json.load(uploaded_file)
                    if loaded_data is not None:
                        st.session_state.league_info = loaded_data
                        st.success("League information loaded from file.")
                else:
                    st.error("Please upload a JSON file.")

# --- Team Profiles ---
with tab2:
    st.header("Team Profiles")
    st.info(f"Data files are saved in: `{BASE_DATA_DIR}`")

    # Add New Team Profile
    with st.expander("Add New Team Profile", expanded=True):
        with st.form("team_profile_form"):
            team_name = st.text_input("Team Name", help="Enter the team's name.")
            team_race = st.text_input("Team Race", help="Enter the race of the team.")
            coach_name = st.text_input("Coach Name", help="Enter the coach's name.")
            team_history = st.text_area("Team History", help="Provide a brief history of the team.")
            achievements = st.text_area("Achievements", help="List the team's achievements.")
            team_logo = st.file_uploader("Upload Team Logo", type=["png", "jpg", "jpeg"], key="team_logo_upload")
            submit_team = st.form_submit_button("Add Team Profile")

            if submit_team:
                errors = []
                if not team_name.strip():
                    errors.append("Team Name is required.")
                if errors:
                    for error in errors:
                        st.error(error)
                else:
                    # Save the uploaded logo image
                    if team_logo is not None:
                        logo_extension = team_logo.type.split('/')[-1]
                        logo_filename = f"{team_name.strip().replace(' ', '_')}_logo.{logo_extension}"
                        logo_path = os.path.join(team_logos_dir, logo_filename)
                        with open(logo_path, 'wb') as f:
                            f.write(team_logo.getbuffer())
                        team_logo_url = logo_path
                    else:
                        team_logo_url = ''

                    team_profile = {
                        'team_name': team_name.strip(),
                        'team_race': team_race.strip(),
                        'coach_name': coach_name.strip(),
                        'team_history': team_history.strip(),
                        'achievements': achievements.strip(),
                        'team_logo': team_logo_url
                    }
                    st.session_state.team_profiles.append(team_profile)
                    save_team_profiles(st.session_state.team_profiles)
                    st.success(f"Team profile for '{team_name}' added.")
                    st.rerun()

    # Display existing team profiles
    if st.session_state.team_profiles:
        st.subheader("Existing Team Profiles")
        for idx, team in enumerate(st.session_state.team_profiles):
            st.markdown(f"### {team['team_name']} ({team['team_race']})")
            if team['team_logo']:
                st.image(team['team_logo'], width=150)
            st.write(f"**Coach:** {team['coach_name']}")
            st.write(f"**History:** {team['team_history']}")
            st.write(f"**Achievements:** {team['achievements']}")

            # Edit and Delete Buttons
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"Edit Team {idx + 1}", key=f"edit_team_{idx}"):
                    st.session_state.edit_team_index = idx
                    st.session_state.show_edit_team_form = True
                    st.rerun()
            with col2:
                if st.button(f"Delete Team {idx + 1}", key=f"delete_team_{idx}"):
                    confirm_delete = st.checkbox(f"Confirm delete Team {idx + 1}", key=f"confirm_delete_team_{idx}")
                    if confirm_delete:
                        st.session_state.team_profiles.pop(idx)
                        save_team_profiles(st.session_state.team_profiles)
                        st.success(f"Team '{team['team_name']}' deleted.")
                        st.rerun()

    # Edit Team Form
    if st.session_state.get('show_edit_team_form', False):
        idx = st.session_state.edit_team_index
        team = st.session_state.team_profiles[idx]
        st.subheader(f"Edit Team '{team['team_name']}'")
        with st.form("edit_team_form"):
            team_name = st.text_input("Team Name", value=team['team_name'])
            team_race = st.text_input("Team Race", value=team['team_race'])
            coach_name = st.text_input("Coach Name", value=team['coach_name'])
            team_history = st.text_area("Team History", value=team['team_history'])
            achievements = st.text_area("Achievements", value=team['achievements'])
            team_logo = st.file_uploader("Upload New Team Logo (optional)", type=["png", "jpg", "jpeg"], key="edit_team_logo_upload")
            submit_edit_team = st.form_submit_button("Update Team Profile")

            if submit_edit_team:
                # Save the uploaded logo image if provided
                if team_logo is not None:
                    logo_extension = team_logo.type.split('/')[-1]
                    logo_filename = f"{team_name.strip().replace(' ', '_')}_logo.{logo_extension}"
                    logo_path = os.path.join(team_logos_dir, logo_filename)
                    with open(logo_path, 'wb') as f:
                        f.write(team_logo.getbuffer())
                    team_logo_url = logo_path
                else:
                    team_logo_url = team['team_logo']  # Keep existing logo

                updated_team = {
                    'team_name': team_name.strip(),
                    'team_race': team_race.strip(),
                    'coach_name': coach_name.strip(),
                    'team_history': team_history.strip(),
                    'achievements': achievements.strip(),
                    'team_logo': team_logo_url
                }
                st.session_state.team_profiles[idx] = updated_team
                save_team_profiles(st.session_state.team_profiles)
                st.success(f"Team '{team_name}' updated.")
                st.session_state.show_edit_team_form = False
                st.rerun()

# --- Player Profiles ---
with tab3:
    st.header("Player Profiles")
    st.info(f"Data files are saved in: `{BASE_DATA_DIR}`")

    # Add New Player Profile
    with st.expander("Add New Player Profile", expanded=True):
        with st.form("player_profile_form"):
            player_name = st.text_input("Player Name", help="Enter the player's name.")
            team_names = [team['team_name'] for team in st.session_state.team_profiles]
            if team_names:
                team_name = st.selectbox("Team Name", options=team_names, help="Select the player's team.")
            else:
                st.warning("No teams available. Please add a team first.")
                team_name = ''
            position = st.text_input("Position", help="Enter the player's position.")
            bio = st.text_area("Player Bio", help="Provide a brief bio of the player.")
            career_highlights = st.text_area("Career Highlights", help="List the player's career highlights.")
            player_photo = st.file_uploader("Upload Player Photo", type=["png", "jpg", "jpeg"], key="player_photo_upload")

            # Player Stats
            st.subheader("Player Statistics")
            matches_played = st.number_input("Matches Played", min_value=0, step=1, help="Number of matches played.")
            touchdowns = st.number_input("Touchdowns", min_value=0, step=1, help="Number of touchdowns scored.")
            interceptions = st.number_input("Interceptions", min_value=0, step=1, help="Number of interceptions made.")
            injuries_caused = st.number_input("Injuries Caused", min_value=0, step=1, help="Number of injuries caused to opponents.")
            mvp_awards = st.number_input("MVP Awards", min_value=0, step=1, help="Number of MVP awards received.")
            submit_player = st.form_submit_button("Add Player Profile")

            if submit_player:
                errors = []
                if not player_name.strip():
                    errors.append("Player Name is required.")
                if not team_name.strip():
                    errors.append("Team Name is required.")
                if errors:
                    for error in errors:
                        st.error(error)
                else:
                    # Save the uploaded player photo
                    if player_photo is not None:
                        photo_extension = player_photo.type.split('/')[-1]
                        photo_filename = f"{player_name.strip().replace(' ', '_')}_photo.{photo_extension}"
                        photo_path = os.path.join(player_photos_dir, photo_filename)
                        with open(photo_path, 'wb') as f:
                            f.write(player_photo.getbuffer())
                        player_photo_url = photo_path
                    else:
                        player_photo_url = ''

                    player_profile = {
                        'player_name': player_name.strip(),
                        'team_name': team_name.strip(),
                        'position': position.strip(),
                        'bio': bio.strip(),
                        'career_highlights': career_highlights.strip(),
                        'player_photo': player_photo_url,
                        'stats': {
                            'matches_played': matches_played,
                            'touchdowns': touchdowns,
                            'interceptions': interceptions,
                            'injuries_caused': injuries_caused,
                            'mvp_awards': mvp_awards
                        }
                    }
                    st.session_state.player_profiles.append(player_profile)
                    save_player_profiles(st.session_state.player_profiles)
                    st.success(f"Player profile for '{player_name}' added.")
                    st.rerun()

    # Display existing player profiles
    if st.session_state.player_profiles:
        st.subheader("Existing Player Profiles")
        for idx, player in enumerate(st.session_state.player_profiles):
            st.markdown(f"### {player['player_name']} ({player['position']})")
            if player['player_photo']:
                st.image(player['player_photo'], width=150)
            st.write(f"**Team:** {player['team_name']}")
            st.write(f"**Bio:** {player['bio']}")
            st.write(f"**Career Highlights:** {player['career_highlights']}")
            st.write(f"**Statistics:**")
            st.write(f"- Matches Played: {player['stats']['matches_played']}")
            st.write(f"- Touchdowns: {player['stats']['touchdowns']}")
            st.write(f"- Interceptions: {player['stats']['interceptions']}")
            st.write(f"- Injuries Caused: {player['stats']['injuries_caused']}")
            st.write(f"- MVP Awards: {player['stats']['mvp_awards']}")

            # Edit and Delete Buttons
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"Edit Player {idx + 1}", key=f"edit_player_profile_{idx}"):
                    st.session_state.edit_player_profile_index = idx
                    st.session_state.show_edit_player_profile_form = True
                    st.rerun()
            with col2:
                if st.button(f"Delete Player {idx + 1}", key=f"delete_player_profile_{idx}"):
                    confirm_delete = st.checkbox(f"Confirm delete Player {idx + 1}", key=f"confirm_delete_player_profile_{idx}")
                    if confirm_delete:
                        st.session_state.player_profiles.pop(idx)
                        save_player_profiles(st.session_state.player_profiles)
                        st.success(f"Player '{player['player_name']}' deleted.")
                        st.rerun()

    # Edit Player Profile Form
    if st.session_state.get('show_edit_player_profile_form', False):
        idx = st.session_state.edit_player_profile_index
        player = st.session_state.player_profiles[idx]
        st.subheader(f"Edit Player '{player['player_name']}'")
        with st.form("edit_player_profile_form"):
            player_name = st.text_input("Player Name", value=player['player_name'])
            team_names = [team['team_name'] for team in st.session_state.team_profiles]
            team_name = st.selectbox("Team Name", options=team_names, index=team_names.index(player['team_name']))
            position = st.text_input("Position", value=player['position'])
            bio = st.text_area("Player Bio", value=player['bio'])
            career_highlights = st.text_area("Career Highlights", value=player['career_highlights'])
            player_photo = st.file_uploader("Upload New Player Photo (optional)", type=["png", "jpg", "jpeg"], key="edit_player_photo_upload")

            # Player Stats
            st.subheader("Player Statistics")
            matches_played = st.number_input("Matches Played", min_value=0, step=1, value=player['stats']['matches_played'])
            touchdowns = st.number_input("Touchdowns", min_value=0, step=1, value=player['stats']['touchdowns'])
            interceptions = st.number_input("Interceptions", min_value=0, step=1, value=player['stats']['interceptions'])
            injuries_caused = st.number_input("Injuries Caused", min_value=0, step=1, value=player['stats']['injuries_caused'])
            mvp_awards = st.number_input("MVP Awards", min_value=0, step=1, value=player['stats']['mvp_awards'])
            submit_edit_player = st.form_submit_button("Update Player Profile")

            if submit_edit_player:
                # Save the uploaded player photo if provided
                if player_photo is not None:
                    photo_extension = player_photo.type.split('/')[-1]
                    photo_filename = f"{player_name.strip().replace(' ', '_')}_photo.{photo_extension}"
                    photo_path = os.path.join(player_photos_dir, photo_filename)
                    with open(photo_path, 'wb') as f:
                        f.write(player_photo.getbuffer())
                    player_photo_url = photo_path
                else:
                    player_photo_url = player['player_photo']  # Keep existing photo

                updated_player = {
                    'player_name': player_name.strip(),
                    'team_name': team_name.strip(),
                    'position': position.strip(),
                    'bio': bio.strip(),
                    'career_highlights': career_highlights.strip(),
                    'player_photo': player_photo_url,
                    'stats': {
                        'matches_played': matches_played,
                        'touchdowns': touchdowns,
                        'interceptions': interceptions,
                        'injuries_caused': injuries_caused,
                        'mvp_awards': mvp_awards
                    }
                }
                st.session_state.player_profiles[idx] = updated_player
                save_player_profiles(st.session_state.player_profiles)
                st.success(f"Player '{player_name}' updated.")
                st.session_state.show_edit_player_profile_form = False
                st.rerun()

# --- Match Reports ---
with tab4:
    st.header("Match Reports")
    st.info(f"Data files are saved in: `{BASE_DATA_DIR}`")

    # Add New Match Report
    with st.expander("Add New Match Report", expanded=True):
        with st.form("match_report_form"):
            match_date = st.date_input("Match Date", value=datetime.today(), help="Select the match date.")
            team_names = [team['team_name'] for team in st.session_state.team_profiles]
            col1, col2 = st.columns(2)
            with col1:
                if team_names:
                    team_a_name = st.selectbox("Team A Name", options=team_names, help="Select Team A.")
                else:
                    st.warning("No teams available. Please add a team first.")
                    team_a_name = ''
                # team_a_race = st.text_input("Team A Race", help="Enter the race of Team A.")
            with col2:
                if team_names:
                    team_b_name = st.selectbox("Team B Name", options=team_names, help="Select Team B.")
                else:
                    st.warning("No teams available. Please add a team first.")
                    team_b_name = ''
                # team_b_race = st.text_input("Team B Race", help="Enter the race of Team B.")
            final_score = st.text_input("Final Score", help="E.g., '2-1 to Team A'")
            key_events = st.text_area("Key Events", help="List significant events such as touchdowns, injuries.")
            save_filename = st.text_input("Save As", value="matches.json", help="Filename for saving the match report.")
            submit_match = st.form_submit_button("Add Match Report")

            if submit_match:
                errors = []
                if not team_a_name.strip():
                    errors.append("Team A Name is required.")
                if not team_b_name.strip():
                    errors.append("Team B Name is required.")
                if not final_score.strip():
                    errors.append("Final Score is required.")
                if errors:
                    for error in errors:
                        st.error(error)
                else:
                    # Get team races from profiles
                    team_a_race = next((team['team_race'] for team in st.session_state.team_profiles if team['team_name'] == team_a_name), '')
                    team_b_race = next((team['team_race'] for team in st.session_state.team_profiles if team['team_name'] == team_b_name), '')

                    match = {
                        'match_date': match_date.strftime('%B %d, %Y'),
                        'team_a_name': team_a_name.strip(),
                        'team_a_race': team_a_race.strip(),
                        'team_b_name': team_b_name.strip(),
                        'team_b_race': team_b_race.strip(),
                        'final_score': final_score.strip(),
                        'key_events': key_events.strip()
                    }
                    st.session_state.matches.append(match)
                    save_data_to_file(st.session_state.matches, save_filename)
                    st.success(f"Match report added and saved as `{save_filename}`.")
                    st.rerun()

    # Display existing match reports
    if st.session_state.matches:
        st.subheader("Existing Match Reports")
        matches_df = pd.DataFrame(st.session_state.matches)
        st.dataframe(matches_df)

        # Visualization of match outcomes
        if 'final_score' in matches_df.columns:
            fig = px.histogram(matches_df, x='final_score', title='Match Outcomes')
            st.plotly_chart(fig)

        # Edit and Delete Options
        for idx, match in enumerate(st.session_state.matches):
            st.markdown(f"**Match {idx + 1}:** {match['team_a_name']} vs {match['team_b_name']} on {match['match_date']}")
            st.write(f"Final Score: {match['final_score']}")
            st.write(f"Key Events: {match['key_events']}")

            # Edit and Delete Buttons
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"Edit Match {idx + 1}", key=f"edit_match_{idx}"):
                    st.session_state.edit_match_index = idx
                    st.session_state.show_edit_match_form = True
                    st.rerun()
            with col2:
                if st.button(f"Delete Match {idx + 1}", key=f"delete_match_{idx}"):
                    confirm_delete = st.checkbox(f"Confirm delete Match {idx + 1}", key=f"confirm_delete_match_{idx}")
                    if confirm_delete:
                        st.session_state.matches.pop(idx)
                        save_data_to_file(st.session_state.matches, save_filename)
                        st.success(f"Match {idx + 1} deleted.")
                        st.rerun()

        # Edit Match Form
        if st.session_state.get('show_edit_match_form', False):
            idx = st.session_state.edit_match_index
            match = st.session_state.matches[idx]
            st.subheader(f"Edit Match {idx + 1}")
            with st.form("edit_match_form"):
                match_date = st.date_input("Match Date", value=datetime.strptime(match['match_date'], '%B %d, %Y'))
                team_names = [team['team_name'] for team in st.session_state.team_profiles]
                col1, col2 = st.columns(2)
                with col1:
                    team_a_name = st.selectbox("Team A Name", options=team_names, index=team_names.index(match['team_a_name']))
                with col2:
                    team_b_name = st.selectbox("Team B Name", options=team_names, index=team_names.index(match['team_b_name']))
                final_score = st.text_input("Final Score", value=match['final_score'])
                key_events = st.text_area("Key Events", value=match['key_events'])
                submit_edit_match = st.form_submit_button("Update Match Report")

                if submit_edit_match:
                    # Get team races from profiles
                    team_a_race = next((team['team_race'] for team in st.session_state.team_profiles if team['team_name'] == team_a_name), '')
                    team_b_race = next((team['team_race'] for team in st.session_state.team_profiles if team['team_name'] == team_b_name), '')

                    updated_match = {
                        'match_date': match_date.strftime('%B %d, %Y'),
                        'team_a_name': team_a_name.strip(),
                        'team_a_race': team_a_race.strip(),
                        'team_b_name': team_b_name.strip(),
                        'team_b_race': team_b_race.strip(),
                        'final_score': final_score.strip(),
                        'key_events': key_events.strip()
                    }
                    st.session_state.matches[idx] = updated_match
                    save_data_to_file(st.session_state.matches, save_filename)
                    st.success(f"Match {idx + 1} updated.")
                    st.session_state.show_edit_match_form = False
                    st.rerun()

# --- Injury Reports ---
with tab5:
    st.header("Injury Reports")
    st.info(f"Data files are saved in: `{BASE_DATA_DIR}`")

    # Add New Injury Report
    with st.expander("Add New Injury Report", expanded=True):
        with st.form("injury_report_form"):
            player_names = [player['player_name'] for player in st.session_state.player_profiles]
            if player_names:
                injured_player_name = st.selectbox("Player Name", options=player_names, help="Select the name of the injured player.")
            else:
                st.warning("No players available. Please add a player first.")
                injured_player_name = ''
            team_name = next((player['team_name'] for player in st.session_state.player_profiles if player['player_name'] == injured_player_name), '')
            injury_type = st.text_input("Injury Type", help="Describe the type of injury.")
            injury_description = st.text_area("Injury Description", help="Provide details about the injury.")
            time_out = st.text_input("Time Out", help="E.g., '2 weeks', 'Rest of the season'")
            expected_return = st.text_input("Expected Return", help="E.g., 'Next match', 'Playoffs'")
            save_filename = st.text_input("Save As", value="injuries.json", help="Filename for saving injury reports.")
            submit_injury = st.form_submit_button("Add Injury Report")

            if submit_injury:
                errors = []
                if not injured_player_name.strip():
                    errors.append("Player Name is required.")
                if not injury_type.strip():
                    errors.append("Injury Type is required.")
                if errors:
                    for error in errors:
                        st.error(error)
                else:
                    injury = {
                        'player_name': injured_player_name.strip(),
                        'team_name': team_name.strip(),
                        'injury_type': injury_type.strip(),
                        'injury_description': injury_description.strip(),
                        'time_out': time_out.strip(),
                        'expected_return': expected_return.strip()
                    }
                    st.session_state.injuries.append(injury)
                    save_data_to_file(st.session_state.injuries, save_filename)
                    st.success(f"Injury report added and saved as `{save_filename}`.")
                    st.rerun()

    # Display existing injury reports
    if st.session_state.injuries:
        st.subheader("Existing Injury Reports")
        injuries_df = pd.DataFrame(st.session_state.injuries)
        st.dataframe(injuries_df)

        # Visualization of injury types
        if 'injury_type' in injuries_df.columns:
            fig = px.bar(injuries_df, x='player_name', y='injury_type', color='team_name', title='Injuries by Player')
            st.plotly_chart(fig)

        # Edit and Delete Options
        for idx, injury in enumerate(st.session_state.injuries):
            st.markdown(f"**Injury {idx + 1}:** {injury['player_name']} from {injury['team_name']}")
            st.write(f"Injury Type: {injury['injury_type']}")
            st.write(f"Description: {injury['injury_description']}")
            st.write(f"Time Out: {injury['time_out']}, Expected Return: {injury['expected_return']}")

            # Edit and Delete Buttons
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"Edit Injury {idx + 1}", key=f"edit_injury_{idx}"):
                    st.session_state.edit_injury_index = idx
                    st.session_state.show_edit_injury_form = True
                    st.rerun()
            with col2:
                if st.button(f"Delete Injury {idx + 1}", key=f"delete_injury_{idx}"):
                    confirm_delete = st.checkbox(f"Confirm delete Injury {idx + 1}", key=f"confirm_delete_injury_{idx}")
                    if confirm_delete:
                        st.session_state.injuries.pop(idx)
                        save_data_to_file(st.session_state.injuries, save_filename)
                        st.success(f"Injury {idx + 1} deleted.")
                        st.rerun()

        # Edit Injury Form
        if st.session_state.get('show_edit_injury_form', False):
            idx = st.session_state.edit_injury_index
            injury = st.session_state.injuries[idx]
            st.subheader(f"Edit Injury {idx + 1}")
            with st.form("edit_injury_form"):
                player_names = [player['player_name'] for player in st.session_state.player_profiles]
                injured_player_name = st.selectbox("Player Name", options=player_names, index=player_names.index(injury['player_name']))
                team_name = next((player['team_name'] for player in st.session_state.player_profiles if player['player_name'] == injured_player_name), '')
                injury_type = st.text_input("Injury Type", value=injury['injury_type'])
                injury_description = st.text_area("Injury Description", value=injury['injury_description'])
                time_out = st.text_input("Time Out", value=injury['time_out'])
                expected_return = st.text_input("Expected Return", value=injury['expected_return'])
                submit_edit_injury = st.form_submit_button("Update Injury Report")

                if submit_edit_injury:
                    updated_injury = {
                        'player_name': injured_player_name.strip(),
                        'team_name': team_name.strip(),
                        'injury_type': injury_type.strip(),
                        'injury_description': injury_description.strip(),
                        'time_out': time_out.strip(),
                        'expected_return': expected_return.strip()
                    }
                    st.session_state.injuries[idx] = updated_injury
                    save_data_to_file(st.session_state.injuries, save_filename)
                    st.success(f"Injury {idx + 1} updated.")
                    st.session_state.show_edit_injury_form = False
                    st.rerun()

# --- Narratives and Lore ---
with tab6:
    st.header("Narratives and Lore")
    st.info(f"Data files are saved in: `{BASE_DATA_DIR}`")

    # Add New Narrative
    with st.expander("Add New Narrative", expanded=True):
        with st.form("narrative_form"):
            storyline_title = st.text_input("Storyline Title", help="Enter the title of the narrative.")
            description = st.text_area("Description", help="Provide a description of the narrative.")
            teams_or_players_involved = st.text_input("Teams/Players Involved", help="List the teams or players involved.")
            recent_developments = st.text_area("Recent Developments", help="Describe any recent developments in the storyline.")
            save_filename = st.text_input("Save As", value="narratives.json", help="Filename for saving narratives.")
            submit_narrative = st.form_submit_button("Add Narrative")

            if submit_narrative:
                errors = []
                if not storyline_title.strip():
                    errors.append("Storyline Title is required.")
                if errors:
                    for error in errors:
                        st.error(error)
                else:
                    narrative = {
                        'storyline_title': storyline_title.strip(),
                        'description': description.strip(),
                        'teams_or_players_involved': teams_or_players_involved.strip(),
                        'recent_developments': recent_developments.strip()
                    }
                    st.session_state.narratives.append(narrative)
                    save_data_to_file(st.session_state.narratives, save_filename)
                    st.success(f"Narrative added and saved as `{save_filename}`.")
                    st.rerun()

    # Display existing narratives
    if st.session_state.narratives:
        st.subheader("Existing Narratives")
        narratives_df = pd.DataFrame(st.session_state.narratives)
        st.dataframe(narratives_df)

        # Visualization of narratives by teams/players
        if 'teams_or_players_involved' in narratives_df.columns:
            narratives_df['count'] = 1  # Add a count column for plotting
            fig = px.bar(narratives_df, x='teams_or_players_involved', y='count', title='Narratives by Teams/Players')
            st.plotly_chart(fig)

        # Edit and Delete Options
        for idx, narrative in enumerate(st.session_state.narratives):
            st.markdown(f"**Storyline {idx + 1}:** {narrative['storyline_title']}")
            st.write(f"Description: {narrative['description']}")
            st.write(f"Teams/Players Involved: {narrative['teams_or_players_involved']}")
            st.write(f"Recent Developments: {narrative['recent_developments']}")

            # Edit and Delete Buttons
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"Edit Narrative {idx + 1}", key=f"edit_narrative_{idx}"):
                    st.session_state.edit_narrative_index = idx
                    st.session_state.show_edit_narrative_form = True
                    st.rerun()
            with col2:
                if st.button(f"Delete Narrative {idx + 1}", key=f"delete_narrative_{idx}"):
                    confirm_delete = st.checkbox(f"Confirm delete Narrative {idx + 1}", key=f"confirm_delete_narrative_{idx}")
                    if confirm_delete:
                        st.session_state.narratives.pop(idx)
                        save_data_to_file(st.session_state.narratives, save_filename)
                        st.success(f"Narrative {idx + 1} deleted.")
                        st.rerun()

        # Edit Narrative Form
        if st.session_state.get('show_edit_narrative_form', False):
            idx = st.session_state.edit_narrative_index
            narrative = st.session_state.narratives[idx]
            st.subheader(f"Edit Narrative {idx + 1}")
            with st.form("edit_narrative_form"):
                storyline_title = st.text_input("Storyline Title", value=narrative['storyline_title'])
                description = st.text_area("Description", value=narrative['description'])
                teams_or_players_involved = st.text_input("Teams/Players Involved", value=narrative['teams_or_players_involved'])
                recent_developments = st.text_area("Recent Developments", value=narrative['recent_developments'])
                submit_edit_narrative = st.form_submit_button("Update Narrative")

                if submit_edit_narrative:
                    updated_narrative = {
                        'storyline_title': storyline_title.strip(),
                        'description': description.strip(),
                        'teams_or_players_involved': teams_or_players_involved.strip(),
                        'recent_developments': recent_developments.strip()
                    }
                    st.session_state.narratives[idx] = updated_narrative
                    save_data_to_file(st.session_state.narratives, save_filename)
                    st.success(f"Narrative {idx + 1} updated.")
                    st.session_state.show_edit_narrative_form = False
                    st.rerun()

# --- Generate GPT Prompt ---
with tab7:
    st.header("Generate GPT Prompt")

    # Generate Prompt Button
    with st.form("generate_prompt_form"):
        # Additional Details
        additional_details = st.text_area("Additional Details", height=150, key="additional_details", help="Include any specific quotes, interviews, or events to highlight.")

        generate_prompt = st.form_submit_button("Generate GPT Prompt")

        if generate_prompt:
            # Validate inputs
            required_fields = [reporter_name, reporter_description, tone_style, format_length]
            if all(required_fields):
                # Formatting Functions
                def format_league_info():
                    league_info = st.session_state.league_info
                    if league_info:
                        return f"**League Name:** {league_info.get('league_name')}\n\n**League Description:**\n{league_info.get('league_description')}"
                    else:
                        return "No league information provided."

                def format_team_profiles():
                    teams = st.session_state.team_profiles
                    if teams:
                        team_str = ""
                        for idx, team in enumerate(teams):
                            team_str += f"**Team {idx + 1}:** {team['team_name']} ({team['team_race']})\n"
                            team_str += f"- Coach: {team['coach_name']}\n"
                            team_str += f"- History: {team['team_history']}\n"
                            team_str += f"- Achievements: {team['achievements']}\n\n"
                        return team_str
                    else:
                        return "No team profiles available."

                def format_player_profiles():
                    players = st.session_state.player_profiles
                    if players:
                        player_str = ""
                        for idx, player in enumerate(players):
                            player_str += f"**Player {idx + 1}:** {player['player_name']} ({player['position']}) for {player['team_name']}\n"
                            player_str += f"- Bio: {player['bio']}\n"
                            player_str += f"- Career Highlights: {player['career_highlights']}\n"
                            player_str += f"- Statistics:\n"
                            player_str += f"  - Matches Played: {player['stats']['matches_played']}\n"
                            player_str += f"  - Touchdowns: {player['stats']['touchdowns']}\n"
                            player_str += f"  - Interceptions: {player['stats']['interceptions']}\n"
                            player_str += f"  - Injuries Caused: {player['stats']['injuries_caused']}\n"
                            player_str += f"  - MVP Awards: {player['stats']['mvp_awards']}\n\n"
                        return player_str
                    else:
                        return "No player profiles available."

                def format_matches():
                    matches = st.session_state.matches
                    if matches:
                        match_str = ""
                        for idx, match in enumerate(matches):
                            match_str += f"**Match {idx + 1}:** {match['team_a_name']} vs {match['team_b_name']} on {match['match_date']}\n"
                            match_str += f"- Final Score: {match['final_score']}\n"
                            match_str += f"- Key Events: {match['key_events']}\n\n"
                        return match_str
                    else:
                        return "No match reports available."

                def format_injuries():
                    injuries = st.session_state.injuries
                    if injuries:
                        injury_str = ""
                        for idx, injury in enumerate(injuries):
                            injury_str += f"**Injury {idx + 1}:** {injury['player_name']} from {injury['team_name']}\n"
                            injury_str += f"- Injury Type: {injury['injury_type']}\n"
                            injury_str += f"- Description: {injury['injury_description']}\n"
                            injury_str += f"- Time Out: {injury['time_out']}, Expected Return: {injury['expected_return']}\n\n"
                        return injury_str
                    else:
                        return "No injury reports available."

                def format_narratives():
                    narratives = st.session_state.narratives
                    if narratives:
                        narrative_str = ""
                        for idx, narrative in enumerate(narratives):
                            narrative_str += f"**Storyline {idx + 1}:** {narrative['storyline_title']}\n"
                            narrative_str += f"- Description: {narrative['description']}\n"
                            narrative_str += f"- Teams/Players Involved: {narrative['teams_or_players_involved']}\n"
                            narrative_str += f"- Recent Developments: {narrative['recent_developments']}\n\n"
                        return narrative_str
                    else:
                        return "No narratives provided."

                # Compile the GPT prompt
                prompt = f"""
You are a seasoned sports journalist in the fantastical and brutal world of Blood Bowl. Your task is to write a report for the **{st.session_state.league_info.get('league_name', 'Unknown League')}**. The report should be engaging and entertaining for both players in the league and fans of Blood Bowl in general. Assume the audience does not need an understanding of Blood Bowl mechanics to enjoy the content.

**Please use the following information to craft your report:**

1. **League Information:**

{format_league_info()}

2. **Team Profiles:**

{format_team_profiles()}

3. **Player Profiles:**

{format_player_profiles()}

4. **Match Reports:**

{format_matches()}

5. **Injury Reports:**

{format_injuries()}

6. **Narratives and Lore:**

{format_narratives()}

7. **Additional Narrative and Lore:**

{additional_details}

8. **Reporter Character:**
- **Character Name:** {reporter_name}
- **Character Description:** {reporter_description}

9. **Tone and Style:** {tone_style}

10. **Format and Length:** {format_length}

---

**Now, please write the report accordingly.**
"""
                st.subheader("Generated GPT Prompt")
                st.text_area("GPT Prompt", value=prompt.strip(), height=500)
                st.markdown("**Copy the prompt above and paste it into your GPT interface to generate the report.**")
            else:
                st.error("Please fill in all required fields in the sidebar.")

# --- Help Tab ---
with tab8:
    st.header("Help and Instructions")
    st.write("""
Welcome to the Blood Bowl GPT Prompt Generator! This app allows you to:

- Manage league information.
- Create and maintain team and player profiles with images and detailed stats.
- Record match reports and injury reports.
- Add narratives and lore to enrich your league's storytelling.
- Generate prompts for GPT to create engaging reports based on your data.

**Getting Started:**

1. **League Info**: Start by adding your league's name and description.
2. **Team Profiles**: Add teams participating in your league.
3. **Player Profiles**: Add players and associate them with teams.
4. **Match Reports**: Record match outcomes and key events.
5. **Injury Reports**: Document injuries to players.
6. **Narratives**: Add storylines and lore to enhance your league's narrative.
7. **Generate Prompt**: Use all the collected data to generate a prompt for GPT.

**Tips:**

- Use the **Sidebar** to set global settings like the reporter character and tone.
- Save your data regularly using the save options provided.
- Ensure filenames are valid to prevent errors.
- For best results, provide as much detailed information as possible.

If you need further assistance, feel free to reach out!

""")

# --- End of Code ---
