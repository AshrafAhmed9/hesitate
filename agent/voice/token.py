"""
LiveKit room-token issuance for the browser client.

PLAN.md section 3: "Keep credentials server-side; issue short-lived
room-scoped tokens." This is that boundary -- the API secret never
leaves the server process; only a signed, room-scoped, time-limited JWT
is handed to the browser.
"""
from __future__ import annotations

import datetime
import os

from livekit import api

DEFAULT_TOKEN_TTL_SECONDS = 30 * 60  # 30 minutes -- short-lived per section 3


def issue_room_token(room_name: str, identity: str, ttl_seconds: int = DEFAULT_TOKEN_TTL_SECONDS) -> str:
    """Returns a signed JWT scoped to exactly one room, for exactly one
    identity, expiring after ttl_seconds. Never returns or logs the API
    secret itself."""
    api_key = os.environ["LIVEKIT_API_KEY"]
    api_secret = os.environ["LIVEKIT_API_SECRET"]
    token = (
        api.AccessToken(api_key, api_secret)
        .with_identity(identity)
        .with_ttl(datetime.timedelta(seconds=ttl_seconds))
        .with_grants(api.VideoGrants(room_join=True, room=room_name))
        .to_jwt()
    )
    return token
