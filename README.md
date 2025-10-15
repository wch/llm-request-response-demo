# LLM Request Demo

A demonstration script for exploring OpenAI and Anthropic API message formats. This tool helps you understand the structure of requests and streaming responses from multiple providers, which is useful for building LLM proxies and integrations.

## What It Does

This script sends requests to OpenAI (Chat Completions API), OpenAI (Responses API), or Anthropic APIs and displays:
1. **Request Payload** - The exact JSON being sent to the API (always pretty-printed)
2. **Streaming Response** - Each streaming event (raw format by default, or pretty-printed with `--pretty`)
3. **Accumulated Text** - The complete text response extracted from the stream

It demonstrates various message types including:
- Simple text conversations
- Image inputs
- Tool/function calling
- Tool responses
- Images in tool results

## Requirements

**Important**: The script requires two image files in the project root directory:
- `tires.jpeg` - Used for the `image_input` scenario
- `plot.png` - Used for the `image_in_tool` scenario

These images are loaded and sent as base64-encoded data to demonstrate how to handle image inputs and outputs. Make sure these files exist before running the image-related scenarios.

## Setup

### 1. Install Dependencies

```bash
uv pip install -r requirements.txt
```

Or using pip:
```bash
pip install -r requirements.txt
```

### 2. Configure API Keys

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Then edit `.env` and add your API keys:

```
OPENAI_API_KEY=sk-your-openai-api-key-here
ANTHROPIC_API_KEY=sk-ant-your-anthropic-api-key-here
```

Alternatively, you can set environment variables directly:

```bash
export OPENAI_API_KEY=sk-...
export ANTHROPIC_API_KEY=sk-ant-...
```

## Usage

```bash
./llm_demo.py --provider <openai-api|openai-responses|anthropic> --scenario <scenario_name> [--pretty]
```

### Providers

- **`openai-api`** - OpenAI Chat Completions API (traditional format)
- **`openai-responses`** - OpenAI Responses API (newer format with `input` parameter)
- **`anthropic`** - Anthropic Claude API

### Output Formats

**Default (raw)**: Streaming responses are shown exactly as received from the API, preserving the original format. This is useful for debugging and seeing the exact wire format.

**With `--pretty`**: Streaming responses are parsed and re-formatted with indentation for easier reading.

```bash
# Raw format (default) - compact, exact API format
./llm_demo.py --provider openai-api --scenario simple_chat

# Pretty format - indented JSON for readability
./llm_demo.py --provider openai-api --scenario simple_chat --pretty
```

### Available Scenarios

#### 1. `simple_chat`
Basic text conversation with system prompt and user message.

```bash
./llm_demo.py --provider openai-api --scenario simple_chat
./llm_demo.py --provider openai-responses --scenario simple_chat
./llm_demo.py --provider anthropic --scenario simple_chat
```

#### 2. `image_input`
Send an image as part of the user message.

```bash
./llm_demo.py --provider openai-api --scenario image_input
./llm_demo.py --provider openai-responses --scenario image_input
./llm_demo.py --provider anthropic --scenario image_input
```

#### 3. `tool_call`
Trigger a tool/function call (weather API example).

```bash
./llm_demo.py --provider openai-api --scenario tool_call
./llm_demo.py --provider openai-responses --scenario tool_call
./llm_demo.py --provider anthropic --scenario tool_call
```

#### 4. `tool_response`
Multi-turn conversation including a tool call and its result.

```bash
./llm_demo.py --provider openai-api --scenario tool_response
./llm_demo.py --provider openai-responses --scenario tool_response
./llm_demo.py --provider anthropic --scenario tool_response
```

#### 5. `image_in_tool`
Tool result that contains an image.

```bash
./llm_demo.py --provider openai-api --scenario image_in_tool
./llm_demo.py --provider openai-responses --scenario image_in_tool
./llm_demo.py --provider anthropic --scenario image_in_tool
```

## Example Output

When run without `--pretty`, the streaming response shows the raw API format:

```
============================================================
OpenAI Request Payload
============================================================
{
  "model": "gpt-5",
  "messages": [
    {
      "role": "developer",
      "content": "You are a helpful assistant that provides concise answers."
    },
    {
      "role": "user",
      "content": "Tell me a haiku."
    }
  ],
  "stream": true,
  "stream_options": {
    "include_usage": true
  }
}

============================================================
Streaming Response
============================================================
data: {"id":"chatcmpl-...","object":"chat.completion.chunk","created":1234567890,"model":"gpt-5","choices":[{"index":0,"delta":{"role":"assistant","content":"Silent"},"finish_reason":null}]}
data: {"id":"chatcmpl-...","object":"chat.completion.chunk","created":1234567890,"model":"gpt-5","choices":[{"index":0,"delta":{"content":" moonlight"},"finish_reason":null}]}
...

============================================================
Accumulated Text Response
============================================================
Silent moonlight falls
On the quiet garden pond
Ripples fade to peace
============================================================
```

With `--pretty`, streaming chunks are formatted with indentation for easier inspection.

## Key Differences Between Providers

### OpenAI Chat Completions vs Responses API

**Chat Completions API** (`openai-api`):
- Uses `messages` array with role-based structure
- Roles: `developer`, `user`, `assistant`, `tool`
- System instructions via `developer` role message

**Responses API** (`openai-responses`):
- Uses `input` parameter (can be string or array)
- System instructions via separate `instructions` parameter
- Flatter structure for tool calls and responses
- Content types: `input_text`, `input_image`, `output_text`, `function_call`, `function_call_output`
- **Important**: Always includes `store: false` to prevent OpenAI from storing requests

### Message Roles
- **OpenAI Chat Completions**: `developer`, `user`, `assistant`, `tool`
- **OpenAI Responses**: `user`, `assistant` (plus `instructions` parameter)
- **Anthropic**: `user`, `assistant` (system is a separate parameter)

### Content Structure
- **OpenAI Chat Completions**: Content can be string or array of `{type: "text"}` or `{type: "image_url"}` objects
- **OpenAI Responses**: Uses `input_text` and `input_image` types in content arrays
- **Anthropic**: Content is array of blocks: `{type: "text"}`, `{type: "image"}`, `{type: "tool_use"}`, `{type: "tool_result"}`

### Tool Calling
- **OpenAI Chat Completions**: Uses `tools` array with `function` objects, returns `tool_calls` array
- **OpenAI Responses**: Uses `tools` array, `function_call` and `function_call_output` items in `input` array
- **Anthropic**: Uses `tools` array with `input_schema`, returns `tool_use` content blocks

### Images
- **OpenAI Chat Completions**:
  - URL: `{"type": "image_url", "image_url": {"url": "https://..."}}`
  - Base64: `{"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,..."}}`
- **OpenAI Responses**:
  - URL: `{"type": "input_image", "image_url": "https://..."}`
  - Base64: `{"type": "input_image", "image_url": "data:image/jpeg;base64,..."}`
- **Anthropic**:
  - URL: `{"type": "image", "source": {"type": "url", "url": "https://..."}}`
  - Base64: `{"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": "..."}}`

**Note**: This script uses base64-encoded images from local files (`tires.jpeg` and `plot.png`) to demonstrate image handling.

## Use Cases

This tool is helpful for:
- **Building LLM Proxies** - Understanding the exact format for routing between providers
- **Learning API Structures** - Seeing real request/response formats side-by-side
- **Debugging Integrations** - Comparing expected vs actual message structures
- **Protocol Translation** - Understanding how to convert between provider formats
- **Comparing OpenAI APIs** - Seeing differences between Chat Completions and Responses API formats

## Configuration

Model names are configurable at the top of `llm_demo.py`:

```python
OPENAI_MODEL = "gpt-5"
ANTHROPIC_MODEL = "claude-sonnet-4-5-20250929"
```

## License

MIT
