"""
MCP server exposing LinkedIn scraper tools to Claude Desktop.
"""

import asyncio
import json
import os
import sys
from pathlib import Path

from apify_client import ApifyClient
from dotenv import load_dotenv
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types

load_dotenv(Path(__file__).parent / ".env")

ACTOR_PROFILE_POSTS = "harvestapi~linkedin-profile-posts"
ACTOR_COMPANY_POSTS = "harvestapi~linkedin-company-posts"
ACTOR_PROFILE_REACTIONS = "harvestapi~linkedin-profile-reactions"

app = Server("linkedin-scraper")


def _apify_client() -> ApifyClient:
    token = os.getenv("APIFY_API_TOKEN")
    if not token:
        raise RuntimeError("APIFY_API_TOKEN not set in .env")
    return ApifyClient(token)


def _run_actor(actor_id: str, actor_input: dict) -> list[dict]:
    client = _apify_client()
    run = client.actor(actor_id).call(run_input=actor_input)
    dataset_id = run.default_dataset_id if hasattr(run, "default_dataset_id") else run["defaultDatasetId"]
    return list(client.dataset(dataset_id).iterate_items())


@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="scrape_linkedin_posts",
            description="Pobiera posty z profilu LinkedIn danej osoby.",
            inputSchema={
                "type": "object",
                "properties": {
                    "profile_url": {
                        "type": "string",
                        "description": "URL profilu LinkedIn, np. https://www.linkedin.com/in/jankowalski/",
                    },
                    "max_posts": {
                        "type": "integer",
                        "description": "Maksymalna liczba postów do pobrania (domyślnie: wszystkie)",
                        "default": 50,
                    },
                },
                "required": ["profile_url"],
            },
        ),
        types.Tool(
            name="scrape_linkedin_company_posts",
            description="Pobiera posty z profilu firmy na LinkedIn.",
            inputSchema={
                "type": "object",
                "properties": {
                    "company_url": {
                        "type": "string",
                        "description": "URL profilu firmy na LinkedIn, np. https://www.linkedin.com/company/microsoft/",
                    },
                    "max_posts": {
                        "type": "integer",
                        "description": "Maksymalna liczba postów do pobrania (domyślnie: wszystkie)",
                        "default": 50,
                    },
                },
                "required": ["company_url"],
            },
        ),
        types.Tool(
            name="scrape_linkedin_profile_reactions",
            description="Pobiera posty, które dana osoba polajkowała / zareagowała na LinkedIn.",
            inputSchema={
                "type": "object",
                "properties": {
                    "profile_url": {
                        "type": "string",
                        "description": "URL profilu LinkedIn, np. https://www.linkedin.com/in/jankowalski/",
                    },
                    "max_items": {
                        "type": "integer",
                        "description": "Maksymalna liczba reakcji do pobrania (domyślnie: wszystkie)",
                        "default": 50,
                    },
                },
                "required": ["profile_url"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    if name == "scrape_linkedin_posts":
        profile_url = arguments["profile_url"]
        max_posts = arguments.get("max_posts", 50)
        actor_input = {"profileUrls": [profile_url]}
        items = await asyncio.get_event_loop().run_in_executor(
            None, _run_actor, ACTOR_PROFILE_POSTS, actor_input
        )
        if max_posts:
            items = items[:max_posts]
        return [types.TextContent(type="text", text=json.dumps(items, ensure_ascii=False, indent=2))]

    if name == "scrape_linkedin_company_posts":
        company_url = arguments["company_url"]
        max_posts = arguments.get("max_posts", 50)
        actor_input = {"companyUrls": [company_url]}
        items = await asyncio.get_event_loop().run_in_executor(
            None, _run_actor, ACTOR_COMPANY_POSTS, actor_input
        )
        if max_posts:
            items = items[:max_posts]
        return [types.TextContent(type="text", text=json.dumps(items, ensure_ascii=False, indent=2))]

    if name == "scrape_linkedin_profile_reactions":
        profile_url = arguments["profile_url"]
        max_items = arguments.get("max_items", 50)
        actor_input = {"profileUrls": [profile_url]}
        items = await asyncio.get_event_loop().run_in_executor(
            None, _run_actor, ACTOR_PROFILE_REACTIONS, actor_input
        )
        if max_items:
            items = items[:max_items]
        return [types.TextContent(type="text", text=json.dumps(items, ensure_ascii=False, indent=2))]

    raise ValueError(f"Unknown tool: {name}")


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
