import os

from study_guide_agent.orchestrators.foundry import FoundryOrchestrator
from study_guide_agent.orchestrators.foundry_client import (
    create_foundry_client_from_env,
)
from study_guide_agent.orchestrators.gemini import GeminiOrchestrator
from study_guide_agent.orchestrators.protocol import AgentOrchestrator


def create_orchestrator(provider: str) -> AgentOrchestrator:
    normalized = provider.strip().lower()
    if normalized == "foundry":
        mcp_endpoint = os.getenv("MCP_SERVER_URL")
        client = create_foundry_client_from_env()
        return FoundryOrchestrator(client=client, mcp_endpoint=mcp_endpoint)
    if normalized == "gemini":
        return GeminiOrchestrator()
    raise ValueError(f"Unknown agent provider: {provider}")


__all__ = [
    "AgentOrchestrator",
    "FoundryOrchestrator",
    "GeminiOrchestrator",
    "create_foundry_client_from_env",
    "create_orchestrator",
]
