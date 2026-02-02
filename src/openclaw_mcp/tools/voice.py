"""clawd_voice: OpenClaw TTS (text-to-speech) via Gateway tools/invoke."""

import logging
from typing import Literal

from fastmcp import Context

from openclaw_mcp.gateway_client import GatewayClient
from openclaw_mcp.config import Settings
from openclaw_mcp.mcp_instance import mcp

logger = logging.getLogger(__name__)


@mcp.tool()
async def clawd_voice(
    ctx: Context,
    operation: Literal["tts"] = "tts",
    text: str = "",
) -> dict:
    """
    OpenClaw voice: TTS (text-to-speech) via Gateway tts tool.

    **Operations:**
    - `tts`: Convert text to speech. Uses OpenClaw TTS (ElevenLabs, OpenAI, or Edge TTS).
      Returns Gateway result; typically includes MEDIA path to generated audio.
      Configure TTS in OpenClaw: messages.tts in ~/.openclaw/openclaw.json.
      See https://docs.clawd.bot/tts

    **Dialogic returns**: Natural language message plus structured data (e.g. media path).

    Requires OpenClaw Gateway at OPENCLAW_GATEWAY_URL with TTS enabled and a provider configured.
    """
    if operation != "tts":
        return {"success": False, "message": "Only operation 'tts' is supported.", "error": "unsupported_operation"}
    if not (text or "").strip():
        return {"success": False, "message": "Text is required for TTS.", "error": "missing_text"}

    settings = Settings()
    client = GatewayClient(settings)
    try:
        result = await client.tools_invoke(
            tool="tts",
            args={"text": text.strip()},
            session_key="main",
        )
        if result.get("success"):
            return {
                "success": True,
                "message": "TTS completed. Check data for MEDIA path or audio URL.",
                "data": result.get("data"),
            }
        return {
            "success": False,
            "message": result.get("message", "TTS failed."),
            "error": result.get("error"),
        }
    finally:
        await client.close()
