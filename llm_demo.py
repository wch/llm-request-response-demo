#!/usr/bin/env python3
"""
LLM Message Format Demonstration Script
Sends requests to OpenAI or Anthropic APIs and streams responses.
"""

import argparse
import json
import os
import sys
from typing import Dict, Any

try:
    import requests
except ImportError:
    print("Error: 'requests' library not found. Install with: pip install requests")
    sys.exit(1)

try:
    from dotenv import load_dotenv
except ImportError:
    print(
        "Error: 'python-dotenv' library not found. Install with: pip install python-dotenv"
    )
    sys.exit(1)


OPENAI_MODEL = "gpt-4o"
ANTHROPIC_MODEL = "claude-sonnet-4-5-20250929"


# ANSI color codes for terminal output
class Colors:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"


def load_api_keys():
    """Load API keys from .env file or environment variables."""
    load_dotenv()

    openai_key = os.getenv("OPENAI_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")

    return openai_key, anthropic_key


def check_api_key(provider: str, api_key: str):
    """Check if API key is present and provide helpful error message if not."""
    if not api_key:
        key_name = "OPENAI_API_KEY" if provider == "openai" else "ANTHROPIC_API_KEY"
        print(f"{Colors.RED}Error: Missing {key_name}!{Colors.ENDC}\n")
        print("You can provide it by either:")
        print(
            f"  1. Creating a .env file with: {Colors.CYAN}{key_name}=your-key-here{Colors.ENDC}"
        )
        print(
            f"  2. Setting environment variable: {Colors.CYAN}export {key_name}=your-key-here{Colors.ENDC}"
        )
        sys.exit(1)


def print_payload(payload: Dict[str, Any], title: str = "Request Payload"):
    """Pretty-print JSON payload with colors."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{title}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.ENDC}")
    print(json.dumps(payload, indent=2))
    print()


def print_stream_start():
    """Print streaming response header."""
    print(f"{Colors.BOLD}{Colors.GREEN}{'=' * 60}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.GREEN}Streaming Response{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.GREEN}{'=' * 60}{Colors.ENDC}")


def send_to_openai(payload: Dict[str, Any], api_key: str):
    """Send request to OpenAI and stream the response."""
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    print_payload(payload, "OpenAI Request Payload")
    print_stream_start()

    try:
        response = requests.post(url, headers=headers, json=payload, stream=True)

        if not response.ok:
            error_body = response.text
            print(
                f"{Colors.RED}Error {response.status_code}: {error_body}{Colors.ENDC}"
            )
            sys.exit(1)

        # Parse SSE stream
        for line in response.iter_lines():
            if line:
                line = line.decode("utf-8")
                if line.startswith("data: "):
                    data_str = line[6:]  # Remove 'data: ' prefix
                    if data_str == "[DONE]":
                        print(f"{Colors.CYAN}data: [DONE]{Colors.ENDC}")
                        break
                    try:
                        data = json.loads(data_str)
                        # Print the entire JSON payload
                        print(f"{Colors.CYAN}{json.dumps(data, indent=2)}{Colors.ENDC}")
                    except json.JSONDecodeError:
                        pass

        print()  # Final newline
        print(f"{Colors.GREEN}Stream complete.{Colors.ENDC}\n")

    except requests.exceptions.RequestException as e:
        print(f"{Colors.RED}Error: {e}{Colors.ENDC}")
        sys.exit(1)


def send_to_anthropic(payload: Dict[str, Any], api_key: str):
    """Send request to Anthropic and stream the response."""
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }

    print_payload(payload, "Anthropic Request Payload")
    print_stream_start()

    try:
        response = requests.post(url, headers=headers, json=payload, stream=True)

        if not response.ok:
            error_body = response.text
            print(
                f"{Colors.RED}Error {response.status_code}: {error_body}{Colors.ENDC}"
            )
            sys.exit(1)

        # Parse SSE stream
        for line in response.iter_lines():
            if line:
                line = line.decode("utf-8")
                if line.startswith("data: "):
                    data_str = line[6:]  # Remove 'data: ' prefix
                    try:
                        data = json.loads(data_str)
                        # Print the entire JSON payload
                        print(f"{Colors.CYAN}{json.dumps(data, indent=2)}{Colors.ENDC}")
                    except json.JSONDecodeError:
                        pass

        print()  # Final newline
        print(f"{Colors.GREEN}Stream complete.{Colors.ENDC}\n")

    except requests.exceptions.RequestException as e:
        print(f"{Colors.RED}Error: {e}{Colors.ENDC}")
        sys.exit(1)


# ============================================================================
# SCENARIO DEFINITIONS
# ============================================================================

SCENARIOS_OPENAI = {
    "simple_chat": {
        "model": OPENAI_MODEL,
        "messages": [
            {
                "role": "developer",
                "content": "You are a helpful assistant that provides concise answers.",
            },
            {"role": "user", "content": "Tell me a haiku."},
        ],
        "stream": True,
    },
    "image_input": {
        "model": OPENAI_MODEL,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "What do you see in this image?"},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg"
                        },
                    },
                ],
            }
        ],
        "max_tokens": 300,
        "stream": True,
    },
    "tool_call": {
        "model": OPENAI_MODEL,
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant with access to weather information.",
            },
            {"role": "user", "content": "What's the weather like in San Francisco?"},
        ],
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "Get the current weather in a given location",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "The city and state, e.g. San Francisco, CA",
                            },
                            "unit": {
                                "type": "string",
                                "enum": ["celsius", "fahrenheit"],
                                "description": "The temperature unit",
                            },
                        },
                        "required": ["location"],
                    },
                },
            }
        ],
        "tool_choice": "auto",
        "stream": True,
    },
    "tool_response": {
        "model": OPENAI_MODEL,
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant with access to weather information.",
            },
            {"role": "user", "content": "What's the weather like in San Francisco?"},
            {
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {
                        "id": "call_abc123",
                        "type": "function",
                        "function": {
                            "name": "get_weather",
                            "arguments": '{"location": "San Francisco, CA", "unit": "fahrenheit"}',
                        },
                    }
                ],
            },
            {
                "role": "tool",
                "tool_call_id": "call_abc123",
                "content": '{"temperature": 72, "condition": "sunny", "humidity": 65}',
            },
        ],
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "Get the current weather in a given location",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {"type": "string"},
                            "unit": {
                                "type": "string",
                                "enum": ["celsius", "fahrenheit"],
                            },
                        },
                        "required": ["location"],
                    },
                },
            }
        ],
        "stream": True,
    },
    "image_in_tool": {
        "model": OPENAI_MODEL,
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant that can generate and analyze charts.",
            },
            {"role": "user", "content": "Create a bar chart showing sales data."},
            {
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {
                        "id": "call_chart123",
                        "type": "function",
                        "function": {
                            "name": "generate_chart",
                            "arguments": '{"chart_type": "bar", "data": [10, 20, 30, 40]}',
                        },
                    }
                ],
            },
            {
                "role": "tool",
                "tool_call_id": "call_chart123",
                "content": json.dumps(
                    {
                        "chart_url": "https://quickchart.io/chart?c={type:'bar',data:{labels:['Q1','Q2','Q3','Q4'],datasets:[{label:'Sales',data:[10,20,30,40]}]}}"
                    }
                ),
            },
        ],
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "generate_chart",
                    "description": "Generate a chart and return the image URL",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "chart_type": {"type": "string"},
                            "data": {"type": "array", "items": {"type": "number"}},
                        },
                        "required": ["chart_type", "data"],
                    },
                },
            }
        ],
        "stream": True,
    },
}


SCENARIOS_ANTHROPIC = {
    "simple_chat": {
        "model": ANTHROPIC_MODEL,
        "max_tokens": 1024,
        "system": "You are a helpful assistant that provides answers.",
        "messages": [{"role": "user", "content": "Tell me a haiku."}],
        "stream": True,
    },
    "image_input": {
        "model": "claude-3-5-sonnet-20241022",
        "max_tokens": 1024,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "What do you see in this image?"},
                    {
                        "type": "image",
                        "source": {
                            "type": "url",
                            "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg",
                        },
                    },
                ],
            }
        ],
        "stream": True,
    },
    "tool_call": {
        "model": ANTHROPIC_MODEL,
        "max_tokens": 1024,
        "system": "You are a helpful assistant with access to weather information.",
        "messages": [
            {"role": "user", "content": "What's the weather like in San Francisco?"}
        ],
        "tools": [
            {
                "name": "get_weather",
                "description": "Get the current weather in a given location",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city and state, e.g. San Francisco, CA",
                        },
                        "unit": {
                            "type": "string",
                            "enum": ["celsius", "fahrenheit"],
                            "description": "The temperature unit",
                        },
                    },
                    "required": ["location"],
                },
            }
        ],
        "stream": True,
    },
    "tool_response": {
        "model": ANTHROPIC_MODEL,
        "max_tokens": 1024,
        "system": "You are a helpful assistant with access to weather information.",
        "messages": [
            {"role": "user", "content": "What's the weather like in San Francisco?"},
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "tool_use",
                        "id": "toolu_01A09q90qw90lq917835lq9",
                        "name": "get_weather",
                        "input": {
                            "location": "San Francisco, CA",
                            "unit": "fahrenheit",
                        },
                    }
                ],
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": "toolu_01A09q90qw90lq917835lq9",
                        "content": '{"temperature": 72, "condition": "sunny", "humidity": 65}',
                    }
                ],
            },
        ],
        "tools": [
            {
                "name": "get_weather",
                "description": "Get the current weather in a given location",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "location": {"type": "string"},
                        "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                    },
                    "required": ["location"],
                },
            }
        ],
        "stream": True,
    },
    "image_in_tool": {
        "model": ANTHROPIC_MODEL,
        "max_tokens": 1024,
        "system": "You are a helpful assistant that can generate and analyze charts.",
        "messages": [
            {"role": "user", "content": "Create a bar chart showing sales data."},
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "tool_use",
                        "id": "toolu_01chart123",
                        "name": "generate_chart",
                        "input": {"chart_type": "bar", "data": [10, 20, 30, 40]},
                    }
                ],
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": "toolu_01chart123",
                        "content": [
                            {"type": "text", "text": "Chart generated successfully:"},
                            {
                                "type": "image",
                                "source": {
                                    "type": "url",
                                    "url": "https://quickchart.io/chart?c={type:'bar',data:{labels:['Q1','Q2','Q3','Q4'],datasets:[{label:'Sales',data:[10,20,30,40]}]}}",
                                },
                            },
                        ],
                    }
                ],
            },
        ],
        "tools": [
            {
                "name": "generate_chart",
                "description": "Generate a chart and return the image",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "chart_type": {"type": "string"},
                        "data": {"type": "array", "items": {"type": "number"}},
                    },
                    "required": ["chart_type", "data"],
                },
            }
        ],
        "stream": True,
    },
}


def main():
    parser = argparse.ArgumentParser(
        description="LLM Message Format Demo - Send requests to OpenAI or Anthropic"
    )
    parser.add_argument(
        "--provider",
        choices=["openai", "anthropic"],
        required=True,
        help="LLM provider to use",
    )
    parser.add_argument(
        "--scenario",
        choices=[
            "simple_chat",
            "image_input",
            "tool_call",
            "tool_response",
            "image_in_tool",
        ],
        required=True,
        help="Scenario to demonstrate",
    )

    args = parser.parse_args()

    # Load API keys
    openai_key, anthropic_key = load_api_keys()

    # Select provider and check API key
    if args.provider == "openai":
        check_api_key("openai", openai_key)
        payload = SCENARIOS_OPENAI[args.scenario]
        send_to_openai(payload, openai_key)
    else:  # anthropic
        check_api_key("anthropic", anthropic_key)
        payload = SCENARIOS_ANTHROPIC[args.scenario]
        send_to_anthropic(payload, anthropic_key)


if __name__ == "__main__":
    main()
