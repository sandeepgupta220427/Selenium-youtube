import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def run():
    server_params = StdioServerParameters(
        command="fastmcp",
        args=["run", "/Users/promode/Documents/AITesterBlueprint/Project_19_MCP_CREATION_AI_AGENT/src/01_HelloWorldCalculator_MCP.py"],
    )
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool("add", arguments={"a": 37, "b": 47})
            print(result)

asyncio.run(run())
