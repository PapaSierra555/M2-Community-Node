#!/usr/bin/env python3
"""
m2-event-space.py — Create or tear down an encrypted Matrix Space for M2 events.

Usage:
  python3 m2-event-space.py create --event "CCC26" --bot-token TOKEN
  python3 m2-event-space.py destroy --bot-token TOKEN

The script saves room IDs to /tmp/m2-event-space-state.json after creation
so destroy can clean up the right rooms.

Rooms created per event:
  #<event>-general    General coordination
  #<event>-ops        Ops/logistics
  #<event>-field      Field team comms
  #<event>-sar        SAR / emergency channel
  #<event>-atak       ATAK/TAK coordination

All rooms: private, invite-only, E2E encrypted at creation.
"""

import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.error

MATRIX_URL = os.environ.get("M2_MATRIX_URL", "https://m2-matrix.yourdomain.com")
STATE_FILE = "/tmp/m2-event-space-state.json"

EVENT_ROOMS = [
    {
        "suffix": "general",
        "name_template": "{event} — General",
        "topic": "General coordination and announcements",
    },
    {
        "suffix": "ops",
        "name_template": "{event} — Ops",
        "topic": "Logistics, setup, and operations staff",
    },
    {
        "suffix": "field",
        "name_template": "{event} — Field",
        "topic": "Field team comms",
    },
    {
        "suffix": "sar",
        "name_template": "{event} — SAR",
        "topic": "Search and rescue / emergency channel",
    },
    {
        "suffix": "atak",
        "name_template": "{event} — ATAK",
        "topic": "ATAK / TAK coordination",
    },
]


def api(method, path, token, body=None):
    url = f"{MATRIX_URL}{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        err = json.loads(e.read())
        print(f"  HTTP {e.code} on {method} {path}: {err.get('error', err)}")
        return None


def create_encrypted_room(token, name, alias, topic):
    # room_version "10" required — Conduit 0.10.x has a bug in room v11/v12 auth
    # where the creator's implicit PL 100 is not recognized for power_level updates.
    # v10 correctly writes the creator to the power_levels state at creation.
    body = {
        "name": name,
        "room_alias_name": alias,
        "room_version": "10",
        "preset": "private_chat",
        "topic": topic,
        "initial_state": [
            {
                "type": "m.room.encryption",
                "state_key": "",
                "content": {"algorithm": "m.megolm.v1.aes-sha2"},
            }
        ],
    }
    result = api("POST", "/_matrix/client/v3/createRoom", token, body)
    return result.get("room_id") if result else None


def add_room_to_space(token, space_id, room_id):
    # Set m.space.child on the space pointing at the room
    body = {"via": ["m2.yourdomain.com"], "suggested": True}
    api("PUT",
        f"/_matrix/client/v3/rooms/{space_id}/state/m.space.child/{room_id}",
        token, body)
    # Set m.space.parent on the room pointing back at the space
    body2 = {"via": ["m2.yourdomain.com"], "canonical": True}
    api("PUT",
        f"/_matrix/client/v3/rooms/{room_id}/state/m.space.parent/{space_id}",
        token, body2)


def invite_user(token, room_id, user_id):
    api("POST", f"/_matrix/client/v3/rooms/{room_id}/invite",
        token, {"user_id": user_id})


def set_power_level(token, room_id, user_id, level):
    # Fetch current power levels first
    result = api("GET",
        f"/_matrix/client/v3/rooms/{room_id}/state/m.room.power_levels/",
        token)
    if not result:
        return
    result.setdefault("users", {})[user_id] = level
    api("PUT",
        f"/_matrix/client/v3/rooms/{room_id}/state/m.room.power_levels/",
        token, result)


def leave_room(token, room_id):
    api("POST", f"/_matrix/client/v3/rooms/{room_id}/leave", token, {})


def cmd_create(args):
    event = args.event
    token = args.bot_token
    slug = event.lower().replace(" ", "-")
    invitees = args.invite or []

    print(f"Creating M2 event space for: {event}")

    # 1. Create the Space
    print("  Creating space...")
    space_body = {
        "name": f"M2 — {event}",
        "room_alias_name": f"m2-{slug}",
        "room_version": "10",
        "preset": "private_chat",
        "topic": f"M2 Community Node — {event} event space",
        "creation_content": {"type": "m.space"},
        "initial_state": [
            {
                "type": "m.room.encryption",
                "state_key": "",
                "content": {"algorithm": "m.megolm.v1.aes-sha2"},
            }
        ],
    }
    space_result = api("POST", "/_matrix/client/v3/createRoom", token, space_body)
    if not space_result:
        print("Failed to create space. Aborting.")
        sys.exit(1)
    space_id = space_result["room_id"]
    print(f"  Space: {space_id}")

    # 2. Create each event room and add to space
    state = {"event": event, "space_id": space_id, "rooms": {}}
    for room_def in EVENT_ROOMS:
        suffix = room_def["suffix"]
        name = room_def["name_template"].format(event=event)
        alias = f"m2-{slug}-{suffix}"
        topic = room_def["topic"]
        print(f"  Creating #{alias}...")
        room_id = create_encrypted_room(token, name, alias, topic)
        if room_id:
            state["rooms"][suffix] = room_id
            add_room_to_space(token, space_id, room_id)
            print(f"    {room_id}")
        else:
            print(f"    FAILED — continuing")
        time.sleep(0.5)

    # 3. Invite users to space and all rooms
    if invitees:
        all_ids = [space_id] + list(state["rooms"].values())
        for user_id in invitees:
            print(f"  Inviting {user_id}...")
            for rid in all_ids:
                invite_user(token, rid, user_id)
                time.sleep(0.2)
            # Set PL 100 in all rooms after they accept (can't set before join)
            # Run --promote after they accept invites

    # 4. Save state
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)
    print(f"\nState saved to {STATE_FILE}")
    print(f"\nSpace alias: #m2-{slug}:m2.yourdomain.com")
    print("Room aliases:")
    for suffix in state["rooms"]:
        print(f"  #m2-{slug}-{suffix}:m2.yourdomain.com")
    print("\nNext: accept invites in Element, then run --promote to set admin power levels.")


def cmd_promote(args):
    """After invitees accept, set their power level to 100 in all rooms."""
    token = args.bot_token
    invitees = args.invite or []
    if not invitees:
        print("No --invite users specified.")
        sys.exit(1)
    try:
        with open(STATE_FILE) as f:
            state = json.load(f)
    except FileNotFoundError:
        print(f"State file not found: {STATE_FILE}")
        sys.exit(1)

    all_ids = [state["space_id"]] + list(state["rooms"].values())
    for user_id in invitees:
        print(f"Setting PL 100 for {user_id}...")
        for rid in all_ids:
            set_power_level(token, rid, user_id, 100)
            time.sleep(0.2)
    print("Done.")


def cmd_destroy(args):
    token = args.bot_token
    try:
        with open(STATE_FILE) as f:
            state = json.load(f)
    except FileNotFoundError:
        print(f"State file not found: {STATE_FILE}")
        sys.exit(1)

    event = state.get("event", "unknown")
    print(f"Destroying event space for: {event}")

    # Tombstone and leave all rooms
    all_ids = list(state["rooms"].values()) + [state["space_id"]]
    for rid in all_ids:
        print(f"  Tombstoning {rid}...")
        api("PUT", f"/_matrix/client/v3/rooms/{rid}/state/m.room.tombstone/",
            token,
            {"body": f"Event {event} concluded. This room is archived.", "replacement_room": ""})
        time.sleep(0.3)
        leave_room(token, rid)
        time.sleep(0.3)

    import os
    os.remove(STATE_FILE)
    print("Done. All event rooms tombstoned and left.")
    print("Note: room data persists in Conduit DB — kick remaining members to fully vacate.")


def main():
    parser = argparse.ArgumentParser(description="M2 Event Space manager")
    parser.add_argument("--bot-token", required=True, help="m2bot access token")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_create = sub.add_parser("create", help="Create event space and rooms")
    p_create.add_argument("--event", required=True, help="Event name, e.g. CCC26")
    p_create.add_argument("--invite", nargs="*", metavar="@user:server",
                          help="Matrix user IDs to invite to all rooms")

    p_promote = sub.add_parser("promote", help="Set PL 100 after invitees accept")
    p_promote.add_argument("--invite", nargs="*", metavar="@user:server", required=True)

    sub.add_parser("destroy", help="Tombstone and leave all event rooms")

    args = parser.parse_args()
    if args.cmd == "create":
        cmd_create(args)
    elif args.cmd == "promote":
        cmd_promote(args)
    elif args.cmd == "destroy":
        cmd_destroy(args)


if __name__ == "__main__":
    main()
