"""
Command-line interface for MCP Client testing.
"""

import asyncio
import json
import sys
from client.core import MCPClient, MCPServerConfig
from client.health.monitor import HealthMonitor
from client.german_llm.cli import handle_german_command


class MCPClientCLI:
    """Simple CLI for interacting with MCP Client."""
    
    def __init__(self):
        self.client = MCPClient()
        self.health_monitor = HealthMonitor(self.client)
    
    async def status(self):
        """Show client status."""
        servers = self.client.get_connected_servers()
        print(f"Connected servers: {len(servers)}")
        if servers:
            for server in servers:
                print(f"  - {server}")
        else:
            print("  (no servers connected)")
    
    async def health(self):
        """Show health status."""
        health = await self.health_monitor.health_check()
        print(json.dumps(health, indent=2))
    
    async def ping(self, server_name: str):
        """Ping a specific server."""
        result = await self.health_monitor.ping_server(server_name)
        print(json.dumps(result, indent=2))
    
    async def tools(self, server_name: str = None):
        """List available tools."""
        tools = await self.client.list_tools(server_name)
        if tools:
            for server, tool_list in tools.items():
                print(f"\n{server} tools:")
                for tool in tool_list:
                    print(f"  - {tool.name}: {tool.description or 'No description'}")
        else:
            print("No tools available (no servers connected)")
    
    def help(self):
        """Show help message."""
        print("""
MCP Client CLI Commands:
  status  - Show connection status
  health  - Show health check results
  ping    - Ping all servers (or specify server name)
  tools   - List available tools
  german  - German language learning commands
  help    - Show this help message
  exit    - Exit the CLI

German Language Learning Commands:
  german init [config]          - Initialize analyzer (configs: default, fast, comprehensive, beginner)
  german check 'text'           - Quick grammar check
  german analyze 'text'         - Comprehensive analysis
  german explain 'topic'        - Explain grammar topic
  german correct 'text'         - Correct with explanations
  german session topic1,topic2  - Create learning session
  german status                 - Show analyzer status
  german cleanup                - Clean up resources
        """)


async def interactive_mode():
    """Run interactive CLI mode."""
    cli = MCPClientCLI()
    
    print("🚀 MCP Client CLI")
    print("Type 'help' for commands, 'exit' to quit")
    
    while True:
        try:
            command = input("\nmcp> ").strip().lower()
            
            if command == "exit":
                break
            elif command == "status":
                await cli.status()
            elif command == "health":
                await cli.health()
            elif command.startswith("ping"):
                parts = command.split()
                server_name = parts[1] if len(parts) > 1 else None
                if server_name:
                    await cli.ping(server_name)
                else:
                    print("Usage: ping <server_name>")
            elif command == "tools":
                await cli.tools()
            elif command == "help":
                cli.help()
            elif command.startswith("german"):
                # Handle German language learning commands
                parts = command.split()
                german_args = parts[1:] if len(parts) > 1 else []
                await handle_german_command(german_args)
            else:
                print("Unknown command. Type 'help' for available commands.")
                
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")


async def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        # Command line mode
        cli = MCPClientCLI()
        command = sys.argv[1].lower()
        
        if command == "status":
            await cli.status()
        elif command == "health":
            await cli.health()
        elif command == "tools":
            await cli.tools()
        else:
            print(f"Unknown command: {command}")
            cli.help()
    else:
        # Interactive mode
        await interactive_mode()


if __name__ == "__main__":
    asyncio.run(main())
