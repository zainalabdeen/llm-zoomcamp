from fastmcp import Client
import asyncio

async def main():
    async with Client("weather_fastmcp_server.py") as mcp_client:
        result = await mcp_client.list_tools()
        print(result)

if __name__ == "__main__":
    test = asyncio.run(main())