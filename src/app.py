"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import os
from pathlib import Path
import re

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# In-memory activity database
activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Soccer Team": {
        "description": "Join the school soccer team and compete in matches",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 22,
        "participants": ["liam@mergington.edu", "noah@mergington.edu"]
    },
    "Basketball Team": {
        "description": "Practice and play basketball with the school team",
        "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["ava@mergington.edu", "mia@mergington.edu"]
    },
    "Art Club": {
        "description": "Explore your creativity through painting and drawing",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["amelia@mergington.edu", "harper@mergington.edu"]
    },
    "Drama Club": {
        "description": "Act, direct, and produce plays and performances",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 20,
        "participants": ["ella@mergington.edu", "scarlett@mergington.edu"]
    },
    "Math Club": {
        "description": "Solve challenging problems and participate in math competitions",
        "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
        "max_participants": 10,
        "participants": ["james@mergington.edu", "benjamin@mergington.edu"]
    },
    "Debate Team": {
        "description": "Develop public speaking and argumentation skills",
        "schedule": "Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 12,
        "participants": ["charlotte@mergington.edu", "henry@mergington.edu"]
    }
}


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is not already signed up
    if email in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student is already signed up"
        )

    # Add student
    activity["participants"].append(email)
    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is signed up
    if email not in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student is not signed up for this activity"
        )

    # Remove student
    activity["participants"].remove(email)
    return {"message": f"Unregistered {email} from {activity_name}"}


# Chatbot models
class ChatMessage(BaseModel):
    message: str


@app.post("/chat")
def chat(chat_message: ChatMessage):
    """Handle chatbot messages and provide responses about activities"""
    user_message = chat_message.message.lower().strip()
    
    # Check for greeting
    if any(greeting in user_message for greeting in ['hello', 'hi', 'hey', 'greetings']):
        return {
            "response": "Hello! I'm the Mergington High School Activities Assistant. I can help you find information about our extracurricular activities, schedules, and available spots. What would you like to know?"
        }
    
    # Check for help request
    if 'help' in user_message:
        return {
            "response": "I can help you with:\n• View all activities\n• Check activity schedules\n• See available spots\n• Get information about specific activities\n\nJust ask me questions like 'What activities are available?' or 'When is Chess Club?'"
        }
    
    # List all activities
    if any(keyword in user_message for keyword in ['list', 'show', 'what activities', 'all activities']):
        activity_list = "\n".join([f"• {name}" for name in activities.keys()])
        return {
            "response": f"Here are all our extracurricular activities:\n\n{activity_list}\n\nWould you like to know more about any specific activity?"
        }
    
    # Check for specific activity queries
    for activity_name, details in activities.items():
        if activity_name.lower() in user_message:
            spots_left = details['max_participants'] - len(details['participants'])
            participant_info = f"\nCurrent participants: {len(details['participants'])}/{details['max_participants']}"
            
            if 'schedule' in user_message or 'when' in user_message:
                return {
                    "response": f"{activity_name} meets {details['schedule']}."
                }
            elif 'spots' in user_message or 'available' in user_message or 'space' in user_message:
                return {
                    "response": f"{activity_name} has {spots_left} spots available out of {details['max_participants']} total."
                }
            else:
                return {
                    "response": f"**{activity_name}**\n\n{details['description']}\n\n**Schedule:** {details['schedule']}\n**Availability:** {spots_left} spots left{participant_info}"
                }
    
    # Schedule-related queries
    if 'schedule' in user_message or 'when' in user_message:
        schedule_info = "\n".join([f"• {name}: {details['schedule']}" for name, details in activities.items()])
        return {
            "response": f"Here are the schedules for all activities:\n\n{schedule_info}"
        }
    
    # Availability queries
    if 'spots' in user_message or 'available' in user_message or 'space' in user_message:
        availability = []
        for name, details in activities.items():
            spots_left = details['max_participants'] - len(details['participants'])
            availability.append(f"• {name}: {spots_left} spots")
        
        return {
            "response": f"Here's the availability for all activities:\n\n" + "\n".join(availability)
        }
    
    # Sign up instructions
    if 'sign up' in user_message or 'join' in user_message or 'register' in user_message:
        return {
            "response": "To sign up for an activity, please use the sign-up form on this page. Enter your email address and select the activity you'd like to join!"
        }
    
    # Default response
    return {
        "response": "I'm not sure I understood that. Try asking me about:\n• Available activities\n• Activity schedules\n• Available spots\n• Specific activities by name\n\nOr just say 'help' for more information!"
    }
