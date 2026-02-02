"""clawd_moltbook: Moltbook social network operations for AI agents."""

import logging
from typing import Literal

from fastmcp import Context

from openclaw_mcp.mcp_instance import mcp

from openclaw_mcp.config import Settings
from openclaw_mcp.moltbook_client import MoltbookClient

logger = logging.getLogger(__name__)


@mcp.tool()
async def clawd_moltbook(
    ctx: Context,
    operation: Literal[
        "feed",
        "search",
        "post",
        "comment",
        "upvote",
        "heartbeat_run",
        "heartbeat_dm",
        "status",
    ],
    post_id: str | None = None,
    content: str | None = None,
    query: str | None = None,
) -> dict:
    """
    Moltbook social network operations for AI agents.

    **Operations:**
    - `feed`: Get personalized or global feed.
    - `search`: Semantic search across posts/comments.
    - `post`: Create a post (rate limit: 1 per 30 min).
    - `comment`: Add comment to post (rate limit: 1 per 20 sec).
    - `upvote`: Upvote a post.
    - `heartbeat_run`: Execute full heartbeat flow (check DMs, feed, consider posting).
    - `heartbeat_dm`: Check DMs only (pending requests, unread).
    - `status`: Check Moltbook API connectivity and key presence.

    **Dialogic returns**: Natural language message plus structured data.

    Requires MOLTBOOK_API_KEY (or OPENCLAW_MOLTBOOK_API_KEY). API base: www.moltbook.com.
    Rate limits: 100 req/min, 1 post/30min, 1 comment/20sec.
    """
    settings = Settings()
    client = MoltbookClient(settings)
    logger.info(
        "clawd_moltbook invoked",
        extra={"tool": "clawd_moltbook", "operation": operation},
    )

    try:
        if operation == "status":
            if not settings.moltbook_api_key:
                return {
                    "success": False,
                    "message": "MOLTBOOK_API_KEY not configured. Set OPENCLAW_MOLTBOOK_API_KEY or MOLTBOOK_API_KEY.",
                }
            result = await client.get("/feed", params={"limit": "1"})
            if result.get("success"):
                return {
                    "success": True,
                    "message": "Moltbook API reachable. Key configured.",
                    "data": {"api": settings.moltbook_url},
                }
            return result

        if operation == "feed":
            result = await client.get("/feed", params={"limit": "20"})
            if result.get("success"):
                result["message"] = "Feed retrieved."
            return result

        if operation == "search":
            if not query:
                return {"success": False, "message": "query required for search"}
            result = await client.get("/search", params={"q": query})
            if result.get("success"):
                result["message"] = f"Search results for: {query}"
            return result

        if operation == "post":
            if not content:
                return {"success": False, "message": "content required for post"}
            result = await client.post("/posts", json={"content": content})
            if result.get("success"):
                result["message"] = "Post created."
            return result

        if operation == "comment":
            if not post_id or not content:
                return {"success": False, "message": "post_id and content required for comment"}
            result = await client.post(
                f"/posts/{post_id}/comments",
                json={"content": content},
            )
            if result.get("success"):
                result["message"] = "Comment added."
            return result

        if operation == "upvote":
            if not post_id:
                return {"success": False, "message": "post_id required for upvote"}
            result = await client.post(f"/posts/{post_id}/upvote")
            if result.get("success"):
                result["message"] = "Upvoted."
            return result

        if operation == "heartbeat_dm":
            result = await client.get("/agents/dm/inbox")
            if result.get("success"):
                result["message"] = "DM inbox checked."
            return result

        if operation == "heartbeat_run":
            dm_result = await client.get("/agents/dm/inbox")
            feed_result = await client.get("/feed", params={"limit": "10"})
            heartbeat_md = "https://www.moltbook.com/heartbeat.md"
            return {
                "success": True,
                "message": "Heartbeat run complete. Check DMs and feed.",
                "data": {
                    "dm_status": "ok" if dm_result.get("success") else "error",
                    "feed_status": "ok" if feed_result.get("success") else "error",
                    "heartbeat_md": heartbeat_md,
                },
            }

        return {"success": False, "message": f"Unknown operation: {operation}"}
    except Exception as e:
        logger.error(
            "clawd_moltbook failed: %s",
            e,
            extra={"tool": "clawd_moltbook", "operation": operation, "error_type": type(e).__name__},
            exc_info=True,
        )
        return {
            "success": False,
            "message": f"Moltbook operation failed: {e!s}",
            "error": str(e),
        }
    finally:
        await client.close()
