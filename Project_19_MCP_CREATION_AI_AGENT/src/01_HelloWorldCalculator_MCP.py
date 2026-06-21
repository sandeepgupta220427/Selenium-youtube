"""
MCP Server 1: Hello World Calculator
=====================================
The simplest possible MCP server.
Just 15 lines of actual code!

Run:   fastmcp dev 01_calculator.py
Test:  Opens MCP Inspector at http://127.0.0.1:6274

"""

from fastmcp import FastMCP

mcp = FastMCP("Calculator")

@mcp.tool()
def add(a: float, b:float) -> float:
    # Single 
    """ Multi comment """
    return a + b

@mcp.tool()
def subtract(a: float, b: float) -> float:
    """Subtract b from a."""
    return a - b


@mcp.tool()
def multiply(a: float, b: float) -> float:
    """Multiply two numbers."""
    return a * b


@mcp.tool()
def divide(a: float, b: float) -> float:
    """Divide a by b. Returns error if b is zero."""
    if b == 0:
        return float("inf")
    return a / b


mcp.add_tool(add)

if __name__ == "__main__":
    mcp.run()