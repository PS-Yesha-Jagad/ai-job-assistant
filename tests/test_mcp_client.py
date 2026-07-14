import asyncio
from agent.mcp_client import MCPClientManager

async def main():
    manager = MCPClientManager()
    # We'll point this at real servers in Phase 3 & 4
    print("MCPClientManager initialized OK")
    await manager.close()

if __name__ == "__main__":
    asyncio.run(main())