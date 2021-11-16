from utils.db_handler import DB


async def get_rooms(
    org_id, query: dict = None
):  # add member_id after figuing query process
    """Get the rooms a user is in
    Args:
        member_id (str): The user id
    Returns:
        [List]: [description]
    """
    DB.organization_id = org_id
    options = {"sort": {"created_at": -1}}
    response = await DB.read("rooms", query, options)
    if response and "status_code" not in response:
        return response
    return []


async def sidebar_emitter(
    org_id, member_id, category: str, group_name: str
):  # group_room_name = None or a String of Names
    """Get sidebar info of rooms a registered member belongs to.
    Args:
        org_id (str): The organization's id,
        member_id (str): The member's id,
        category (str): category of the plugin (direct message or channel)
        group_name: name of plugin
        room_name: title of the room if any
    Returns:
        {dict}: {dict containing user info}
    """

    rooms = []
    starred_rooms = []
    user_rooms = await get_rooms(
        org_id=org_id
    )  # add member_id after adding it to function
    if user_rooms is not None:
        for room in user_rooms:
            room_profile = {}
            if len(room["room_members"]) == 2:
                room_profile["room_id"] = room["_id"]
                room_profile["room_url"] = f"/dm/{room['_id']}"
                user_id_set = set(room["room_members"]).difference({member_id})
                partner_id = list(user_id_set)[0]

                profile = await DB.get_member(partner_id)

                if "user_name" in profile and profile["user_name"] != "":
                    if profile["user_name"]:
                        room_profile["room_name"] = profile["user_name"]
                    else:
                        room_profile["room_name"] = "no user name"
                    if profile["image_url"]:
                        room_profile["room_image"] = profile["image_url"]
                    else:
                        room_profile["room_image"] = (
                            "https://cdn.iconscout.com/icon/free/png-256/"
                            "account-avatar-profile-human-man-user-30448.png"
                        )

                else:
                    room_profile["room_name"] = "no user name"
                    room_profile["room_image"] = (
                        "https://cdn.iconscout.com/icon/free/png-256/"
                        "account-avatar-profile-human-man-user-30448.png"
                    )
            else:
                room_profile["room_name"] = room["room_name"]
                room_profile["room_id"] = room["_id"]
                room_profile["room_url"] = f"/dm/{room['_id']}"

            rooms.append(room_profile)

    #       if room["room_members"][member_id]["starred"] is True:
    #           starred_rooms.append(room_profile)

    sidebar = {
        "data": {
            "name": "Messaging",
            "description": "Sends messages between users in a dm or channel",
            "plugin_id": "messaging.zuri.chat",
            "organisation_id": f"{org_id}",
            "user_id": f"{member_id}",
            "group_name": f"{group_name}",
            "category": f"{category}",
            "show_group": False,
            "button_url": f"/{category}",
            "public_rooms": [],
            "starred_rooms": starred_rooms,
            "joined_rooms": rooms,
        }  # List of rooms/channels created whenever a user starts a DM chat with another user
        # This is what will be displayed by Zuri Main
    }
    return sidebar