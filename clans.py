import json
import os
import time
from datetime import datetime, timedelta

import scratchattach as scratch3
from fuzzywuzzy import fuzz

# Your username and session setup
session = scratch3.Session(os.environ["SESSION_ID"], username="crashbandicootsthe1")
conn = session.connect_cloud("903941586")
client = scratch3.CloudRequests(conn)

# Define a constant for the similarity threshold
SIMILARITY_THRESHOLD = 55

# Function to load user data from a JSON file
def load_user_data():
    try:
        if os.path.exists("user_data.json"):
            with open("user_data.json", "r") as data_file:
                return json.load(data_file)
        else:
            return {}
    except Exception as e:
        print(f"Error loading user data: {e}")
        return {}

# Function to save user data to a JSON file
def save_user_data(user_data):
    try:
        with open("user_data.json", "w") as data_file:
            json.dump(user_data, data_file, indent=4)
    except Exception as e:
        print(f"Error saving user data: {e}")

# Function to load team data from a JSON file
def load_team_data():
    try:
        if os.path.exists("team_data.json"):
            with open("team_data.json", "r") as data_file:
                return json.load(data_file)
        else:
            return {}
    except Exception as e:
        print(f"Error loading team data: {e}")
        return {}

# Function to save team data to a JSON file
def save_team_data(team_data):
    try:
        with open("team_data.json", "w") as data_file:
            json.dump(team_data, data_file, indent=4)
    except Exception as e:
        print(f"Error saving team data: {e}")

# Initialize the team data
team_data = load_team_data()

# Function to retrieve team data by ID
def get_team_by_id(team_id):
    return team_data.get(str(team_id), {})

@client.request
def ping():
    return "pong"

@client.request
def create_team(team_name, owner_name):
    # Generate a new team ID
    team_id = len(team_data) + 1

    # Create a new team entry with team_id
    team_data[team_id] = {
        "team_id": team_id,
        "team_name": team_name,
        "owner_name": owner_name,
        "members": [],
        "boosts": 0  # Initialize the number of boosts
    }
    save_team_data(team_data)
    return {"success": "Team created successfully."}

import json


# Load team data from team_data.json
def load_team_data_from_file():
    try:
        with open("team_data.json", "r") as data_file:
            return json.load(data_file)
    except Exception as e:
        print(f"Error loading team data: {e}")
        return {}

# Load user data from user_data.json
def load_user_data_from_file():
    try:
        with open("user_data.json", "r") as data_file:
            return json.load(data_file)
    except Exception as e:
        print(f"Error loading user data: {e}")
        return {}


# Function to find the newest team ID from team_data.json
@client.request
def newest_team():
    try:
        with open("team_data.json", "r") as data_file:
            team_data = json.load(data_file)
            if not team_data:
                return None  # No teams exist
            # Find the maximum team ID
            max_team_id = max(map(int, team_data.keys()))
            return max_team_id
    except Exception as e:
        print(f"Error finding newest team ID: {e}")
        return None

@client.request
def search_teams(keyword):
    matching_teams = []

    for team_id, team_info in team_data.items():
        team_name = team_info.get("team_name", "")
        similarity = fuzz.partial_ratio(keyword, team_name)

        if similarity >= SIMILARITY_THRESHOLD:
            matching_teams.append([team_id, team_info])

    return matching_teams

@client.request
def join_team(team_id, member_name):
    team = get_team_by_id(team_id)
    if not team:
        return {"error": "Team does not exist."}

    # Add the member to the team
    team["members"].append(member_name)
    save_team_data(team_data)
    return {"success": "Joined team successfully."}

@client.request
def get_team(team_id):
    team_info = team_data.get(str(team_id))

    if team_info is None:
        return {"error": "Team does not exist."}

    return format_team_info(team_info)

def format_team_info(team_info):
    team_id = team_info.get("team_id")  # Corrected here to get the team_id
    team_name = team_info.get("team_name")
    owner_name = team_info.get("owner_name")
    team_members = team_info.get("members", [])
    team_boosts = team_info.get("boosts", 0)
    member_amount = len(team_members)
    boost_level = calculate_boost_level(team_boosts)

    return [
        "team_id",  # Team ID is now included in the response
        team_id,
        "team name",
        team_name,
        "owner",
        owner_name,
        "members",
        team_members,
        "boosts",
        team_boosts,
        "level",
        boost_level,
        "member_amount",
        member_amount,
    ]


def calculate_boost_level(boosts):
    if boosts < 3:
        return 0
    elif boosts < 10:
        return 1
    elif boosts < 20:
        return 2
    elif boosts < 25:
        return 3
    else:
        return 4

@client.request
def get_leaderboard():
    # Sort the teams by the number of boosts in descending order
    sorted_teams = sorted(team_data.items(), key=lambda x: x[1].get("boosts", 0), reverse=True)

    # Extract the top 5 teams
    top_teams = sorted_teams[:5]

    leaderboard = []
    for _team_id, team_info in top_teams:
        leaderboard.append(format_team_info(team_info))

    return leaderboard

# Function to award 1 gemstone to every user
def award_gemstones_to_users(user_data):
    for _user_id, user_info in user_data.items():
        user_info["gemstones"] += 1


# Calculate the time remaining until the next hour with both minute and second as 0
def time_until_next_hour():
    now = datetime.utcnow()
    next_hour = now.replace(minute=0, second=0) + timedelta(hours=1)
    time_remaining = next_hour - now
    return time_remaining.total_seconds()
  
@client.event
def on_request(request):
    print("Received request", request.name, request.requester, request.arguments, request.timestamp, request.id)

if __name__ == "__main__":
    client.run()
    while True:
        time_remaining = time_until_next_hour()
        if time_remaining > 0:
          time.sleep(time_remaining)
        
          user_data = load_user_data()
          award_gemstones_to_users(user_data)
          save_user_data(user_data)