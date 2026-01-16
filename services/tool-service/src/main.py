# Copyright 2024 Renai Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tool Service main application entry point."""

import ast
import operator
from typing import Any

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from shared import get_settings, get_logger
from shared.types import ServiceResponse, ToolDefinition, ToolCall, ToolResult

logger = get_logger(__name__)
settings = get_settings()

# In-memory tool registry (would be database in production)
tool_registry: dict[str, ToolDefinition] = {}

# Safe arithmetic operators
_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def _safe_eval_arithmetic(expr: str) -> float:
    """Safely evaluate arithmetic expressions using AST parsing."""
    try:
        tree = ast.parse(expr, mode="eval")
    except SyntaxError as e:
        raise ValueError(f"Invalid expression syntax: {e}") from e

    def _eval_node(node: ast.AST) -> float:
        if isinstance(node, ast.Expression):
            return _eval_node(node.body)
        elif isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return float(node.value)
            raise ValueError(f"Unsupported constant type: {type(node.value)}")
        elif isinstance(node, ast.BinOp):
            op = _OPERATORS.get(type(node.op))
            if op is None:
                raise ValueError(f"Unsupported operator: {type(node.op).__name__}")
            left = _eval_node(node.left)
            right = _eval_node(node.right)
            return op(left, right)
        elif isinstance(node, ast.UnaryOp):
            op = _OPERATORS.get(type(node.op))
            if op is None:
                raise ValueError(f"Unsupported operator: {type(node.op).__name__}")
            return op(_eval_node(node.operand))
        else:
            raise ValueError(f"Unsupported expression type: {type(node).__name__}")

    return _eval_node(tree)


class RegisterToolRequest(BaseModel):
    """Request to register a new tool."""

    name: str
    description: str
    parameters: dict[str, Any]
    required: list[str] = Field(default_factory=list)


class ExecuteToolRequest(BaseModel):
    """Request to execute a tool."""

    arguments: dict[str, Any]


app = FastAPI(
    title="Renai Tool Service",
    description="Tool registry service with MCP protocol support",
    version="0.1.0",
)


def register_builtin_tools():
    """Register built-in tools."""
    builtin_tools = [
        ToolDefinition(
            name="calculator",
            description="Perform basic arithmetic calculations",
            parameters={
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Mathematical expression to evaluate",
                    },
                },
            },
            required=["expression"],
        ),
        ToolDefinition(
            name="web_search",
            description="Search the web for information",
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query",
                    },
                    "num_results": {
                        "type": "integer",
                        "description": "Number of results to return",
                        "default": 5,
                    },
                },
            },
            required=["query"],
        ),
        ToolDefinition(
            name="get_weather",
            description="Get current weather for a location",
            parameters={
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City name or coordinates",
                    },
                },
            },
            required=["location"],
        ),
    ]

    for tool in builtin_tools:
        tool_registry[tool.name] = tool


# Register built-in tools on startup
register_builtin_tools()


@app.get("/health")
async def health_check() -> ServiceResponse[dict[str, str]]:
    """Health check endpoint."""
    return ServiceResponse(data={"status": "healthy", "service": "tool-service"})


@app.get("/api/v1/tools")
async def list_tools() -> ServiceResponse[list[ToolDefinition]]:
    """List all registered tools."""
    return ServiceResponse(data=list(tool_registry.values()))


@app.get("/api/v1/tools/{name}")
async def get_tool(name: str) -> ServiceResponse[ToolDefinition]:
    """Get tool details by name."""
    if name not in tool_registry:
        raise HTTPException(status_code=404, detail=f"Tool '{name}' not found")
    return ServiceResponse(data=tool_registry[name])


@app.post("/api/v1/tools")
async def register_tool(request: RegisterToolRequest) -> ServiceResponse[ToolDefinition]:
    """Register a new tool."""
    if request.name in tool_registry:
        raise HTTPException(
            status_code=409, detail=f"Tool '{request.name}' already exists"
        )

    tool = ToolDefinition(
        name=request.name,
        description=request.description,
        parameters=request.parameters,
        required=request.required,
    )
    tool_registry[request.name] = tool

    logger.info("Tool registered", extra={"tool": request.name})
    return ServiceResponse(data=tool, message=f"Tool '{request.name}' registered")


@app.delete("/api/v1/tools/{name}")
async def unregister_tool(name: str) -> ServiceResponse[dict[str, str]]:
    """Unregister a tool."""
    if name not in tool_registry:
        raise HTTPException(status_code=404, detail=f"Tool '{name}' not found")

    del tool_registry[name]
    logger.info("Tool unregistered", extra={"tool": name})
    return ServiceResponse(data={"status": "deleted"}, message=f"Tool '{name}' removed")


@app.post("/api/v1/tools/{name}/execute")
async def execute_tool(name: str, request: ExecuteToolRequest) -> ServiceResponse[ToolResult]:
    """Execute a tool with given arguments."""
    if name not in tool_registry:
        raise HTTPException(status_code=404, detail=f"Tool '{name}' not found")

    tool = tool_registry[name]

    # Validate required parameters
    for param in tool.required:
        if param not in request.arguments:
            raise HTTPException(
                status_code=400, detail=f"Missing required parameter: {param}"
            )

    try:
        # Execute tool based on name
        result = await _execute_tool_impl(name, request.arguments)
        return ServiceResponse(
            data=ToolResult(tool_name=name, success=True, result=result)
        )
    except Exception as e:
        logger.error("Tool execution failed", extra={"tool": name, "error": str(e)})
        return ServiceResponse(
            data=ToolResult(tool_name=name, success=False, error=str(e))
        )


async def _execute_tool_impl(name: str, arguments: dict[str, Any]) -> Any:
    """Execute tool implementation."""
    if name == "calculator":
        # Safe expression evaluation using a simple parser
        expr = arguments["expression"]
        # Only allow safe arithmetic characters
        allowed_chars = set("0123456789+-*/.(). ")
        if not all(c in allowed_chars for c in expr):
            raise ValueError("Invalid characters in expression")
        # Use a safe arithmetic evaluator
        result = _safe_eval_arithmetic(expr)
        return {"result": result}

    elif name == "web_search":
        # Mock web search (would call actual search API in production)
        query = arguments["query"]
        return {
            "results": [
                {"title": f"Result for: {query}", "url": "https://example.com"},
            ]
        }

    elif name == "get_weather":
        # Mock weather (would call weather API in production)
        location = arguments["location"]
        return {
            "location": location,
            "temperature": "20°C",
            "conditions": "Partly cloudy",
        }

    else:
        raise ValueError(f"No implementation for tool: {name}")


# MCP Protocol endpoints
@app.get("/mcp/tools")
async def mcp_list_tools() -> dict[str, Any]:
    """MCP protocol - list available tools."""
    tools = []
    for tool in tool_registry.values():
        tools.append(
            {
                "name": tool.name,
                "description": tool.description,
                "inputSchema": tool.parameters,
            }
        )
    return {"tools": tools}


@app.post("/mcp/tools/call")
async def mcp_call_tool(call: ToolCall) -> dict[str, Any]:
    """MCP protocol - call a tool."""
    if call.tool_name not in tool_registry:
        return {
            "content": [{"type": "text", "text": f"Tool '{call.tool_name}' not found"}],
            "isError": True,
        }

    try:
        result = await _execute_tool_impl(call.tool_name, call.arguments)
        return {
            "content": [{"type": "text", "text": str(result)}],
            "isError": False,
        }
    except Exception as e:
        return {
            "content": [{"type": "text", "text": str(e)}],
            "isError": True,
        }


if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host=settings.service_host,
        port=8005,
        reload=settings.debug,
    )
