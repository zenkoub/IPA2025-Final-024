#######################################################################################
# Yourname: Koobun Kritnetithat
# Your student ID: 66070024
# Your GitHub Repo: https://github.com/zenkoub/IPA2025-Final-024

#######################################################################################
# 1. Import libraries for API requests, JSON formatting, time, os, (restconf_final or netconf_final), netmiko_final, and ansible_final.
import os
import time
import json
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder
import restconf_final as rc
import netconf_final as nc
import netmiko_final as nm
import ansible_final as ac

#######################################################################################
# Define IPA2025 router IP addresses
router_ip_list = [
    "10.0.15.61",
    "10.0.15.62",
    "10.0.15.63",
    "10.0.15.64",
    "10.0.15.65",
]

#######################################################################################
# 2. Assign the Webex access token to the variable ACCESS_TOKEN using environment variables.

ACCESS_TOKEN = os.environ.get("WEBEX_TOKEN")

room_response = requests.get(  # Get the list of rooms
    "https://webexapis.com/v1/rooms",
    headers={"Authorization": f"Bearer {ACCESS_TOKEN}"}
)

rooms = room_response.json()["items"] # sort the list of rooms in .json

# find room named IPA2025 (if present)
roomId = None
for room in rooms:
    if room.get("title") == "IPA2025":
        roomId = room.get("id")
        print("Using room:", room.get("title"))
        break

#######################################################################################
# 3. Prepare parameters get the latest message for messages API.

# Defines a variable that will hold the roomId. Prefer explicit env var, fall back to discovered roomId
roomIdToGetMessages = os.environ.get("WEBEX_ROOM_ID") or roomId

current_method = None

while True:
    # always add 1 second of delay to the loop to not go over a rate limit of API calls
    time.sleep(1)

    # the Webex Teams GET parameters
    #  "roomId" is the ID of the selected room
    #  "max": 1  limits to get only the very last message in the room
    getParameters = {"roomId": roomIdToGetMessages, "max": 1}

    # the Webex Teams HTTP header, including the Authoriztion
    getHTTPHeader = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

# 4. Provide the URL to the Webex Teams messages API, and extract location from the received message.
    
    # Send a GET request to the Webex Teams messages API.
    # - Use the GetParameters to get only the latest message.
    # - Store the message in the "r" variable.
    r = requests.get(
        "https://webexapis.com/v1/messages",
        params=getParameters,
        headers=getHTTPHeader,
    )
    # verify if the retuned HTTP status code is 200/OK
    if not r.status_code == 200:
        raise Exception(
            "Incorrect reply from Webex Teams API. Status code: {}".format(r.status_code)
        )

    # get the JSON formatted returned data
    json_data = r.json()

    # check if there are any messages in the "items" array
    if len(json_data["items"]) == 0:
        raise Exception("There are no messages in the room.")

    # store the array of messages
    messages = json_data["items"]
    
    # store the text of the first message in the array
    message = messages[0]["text"].strip()

    # check if the text of the message starts with the magic character "/" followed by your studentID and a space and followed by a command name
    #  e.g.  "/66070024 create"
    # Only process messages that start with the student ID; skip others
    if not message.startswith("/66070024"):
        continue
    print("Received message: " + message)
    try:
        parts = message.split()
        studentID = parts[0][1:]
    except IndexError:
        continue

    router_ip = None
    responseMessage = None

    # First, check if the user is selecting the method
    if len(parts) == 2:
        command = parts[1].strip().lower()
        if command in ["restconf", "netconf"]:
            current_method = command
            responseMessage = f"Ok: {current_method}"
        else:
            responseMessage = "Error: No command or unknown command"

    # Commands with router IP
    elif len(parts) >= 3:
        router_ip = parts[1]
        command = parts[2].lower()

        if router_ip not in router_ip_list:
            responseMessage = f"Error: Invalid IP, no {router_ip} in IPA2025"

        elif command in ["create", "delete", "enable", "disable", "status"]:
            if not current_method:
                responseMessage = "Error: No method specified"
            else:
                if current_method == "restconf":
                    responseMessage = getattr(rc, command)(studentID, router_ip)
                elif current_method == "netconf":
                    responseMessage = getattr(nc, command)(studentID, router_ip)

        elif command == "gigabit_status":
            responseMessage = nm.gigabit_status(router_ip)

        elif command == "showrun":
            responseMessage = ac.showrun(studentID, router_ip)
        
        elif command == "motd":
            if len(parts) >= 3:
                motd_text = " ".join(parts[3:])
                responseMessage = ac.configure_motd(studentID, router_ip, motd_text)
            else:
                responseMessage = nm.read_motd(router_ip)

        else:
            responseMessage = "Error: Unknown command"

# 6. Complete the code to post the message to the Webex Teams room.

    # The Webex Teams POST JSON data for command showrun
    # - "roomId" is is ID of the selected room
    # - "text": is always "show running config"
    # - "files": is a tuple of filename, fileobject, and filetype.

    # the Webex Teams HTTP headers, including the Authoriztion and Content-Type
        
    # Prepare postData and HTTPHeaders for command showrun
    # Need to attach file if responseMessage is 'ok'; 
    # Read Send a Message with Attachments Local File Attachments
    # https://developer.webex.com/docs/basics for more detail

    if command == "showrun" and responseMessage != "Error: Ansible":
        filename = responseMessage
        fileobject = open(filename, "rb")
        filetype = "text/plain"
            
        postData = {
            "roomId": roomIdToGetMessages,
            "text": "show running config",
            "files": (filename, fileobject, filetype),
        }
 
        postData = MultipartEncoder(postData)
        HTTPHeaders = {
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "Content-Type": postData.content_type,
        }
    # other commands only send text, or no attached file.
    else:
        print("Response:", responseMessage)

        postData = {"roomId": roomIdToGetMessages, "text": responseMessage}
        postData = json.dumps(postData)

        # the Webex Teams HTTP headers, including the Authoriztion and Content-Type
        HTTPHeaders = {
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "Content-Type": "application/json",
        }   

    # Post the call to the Webex Teams message API.
    r = requests.post(
        "https://webexapis.com/v1/messages",
        data=postData,
        headers=HTTPHeaders,
    )
        
    print("Webex POST response:", r.status_code, r.text)
        
    if not r.status_code in [200, 201]:
        raise Exception(
            "Incorrect reply from Webex Teams API. Status code: {}".format(r.status_code)
        )
