# Strands Context Manager Skill (Sliding Window with Summarization)

A production-ready conversation management solution for Strands agents that prevents context window overflow while preserving important conversation context through intelligent summarization.

## Quick Start

### Installation

```bash
npx skills add https://github.com/aws-samples/sample-agent-skills-for-builders --skill strands-context-manager
```

### Basic Usage

```python
from conversation_manager import SlidingWindowWithSummarizationManager
from strands import Agent
from strands.agent.session_manager import FileSessionManager

# Create the conversation manager
manager = SlidingWindowWithSummarizationManager(window_size=20)

# Use it with your agent
agent = Agent(
    model="anthropic.claude-sonnet-3-5-v2:0",
    conversation_manager=manager,
    session_manager=FileSessionManager()
)

# Have a conversation—old messages are automatically summarized
for i in range(50):
    response = agent(f"Tell me about topic {i}")
    print(response.text)

# Only recent messages + summary remain in memory
# No context window overflow, no token waste
```

## What This Skill Does

When conversations grow long, they either:
- **Exceed model context limits** (errors, truncation)
- **Waste tokens** (more expensive API calls)
- **Lose historical context** (if simply discarded)

This skill solves all three problems by:

1. **Maintaining a sliding window** of recent messages (default: 20)
2. **Summarizing older messages** instead of deleting them
3. **Prepending the summary** to keep context while staying efficient
4. **Preserving tool use/result pairs** during summarization

## Key Features

### Zero Session Pollution
Internal summarization messages never get persisted to your session storage. Your conversation history stays clean.

### Infinite Recursion Prevention
Built-in guards prevent the summarization process from triggering itself recursively—a common pitfall in conversation managers.

### Tool-Safe Summarization
Automatically adjusts where to split messages to avoid breaking ToolUse/ToolResult pairs, which must stay together.

### Customizable Summarization Agent
Use a faster/cheaper model for summarization:

```python
from strands import Agent as StrandsAgent

# Haiku for summarization (cheaper)
summarization_agent = StrandsAgent(
    model="anthropic.claude-haiku-3-5:0",
    system_prompt="You are a conversation summarizer..."
)

manager = SlidingWindowWithSummarizationManager(
    window_size=20,
    summarization_agent=summarization_agent
)
```

## Configuration

### Parameters

```python
manager = SlidingWindowWithSummarizationManager(
    window_size=40,                              # Max recent messages to keep (default: 40)
    summarization_agent=None,                   # Optional custom agent for summarization
    summarization_system_prompt=None            # Optional custom system prompt
)
```

### Examples

**Long conversations with summary preservation:**
```python
manager = SlidingWindowWithSummarizationManager(window_size=10)
```

**Custom summarization prompt:**
```python
manager = SlidingWindowWithSummarizationManager(
    window_size=30,
    summarization_system_prompt="Summarize focusing on technical details and decisions..."
)
```

**User-provided agent:**
```python
custom_agent = Agent(model="anthropic.claude-haiku-3-5:0", ...)
manager = SlidingWindowWithSummarizationManager(
    summarization_agent=custom_agent
)
```

## File Structure

```
skills/strands-context-manager/
├── README.md                           # This file
├── SKILL.md                            # Skill definition & pitfall guide
├── scripts/
│   └── strands-context-manager.py      # Implementation
└── references/
    └── architecture.md                 # Deep dive: design patterns & testing
```

## Prerequisites

- **Python 3.10+**
- **Strands Agent SDK** (`from strands import Agent`)
- **Session manager** (FileSessionManager, S3SessionManager, etc.)

## Common Patterns

### Basic Multi-Turn Chat
```python
manager = SlidingWindowWithSummarizationManager(window_size=20)
agent = Agent(
    model="anthropic.claude-sonnet-3-5-v2:0",
    conversation_manager=manager,
    session_manager=FileSessionManager(session_id="my_chat")
)

# Chat naturally—summarization happens automatically
response1 = agent("What's Python?")
response2 = agent("Show me a decorator example")
response3 = agent("How does that work under the hood?")
# ... after window_size messages, old ones get summarized
```

### Expensive Operations with Budget Control
```python
# Use cheaper Haiku for summarization
summarization_agent = Agent(
    model="anthropic.claude-haiku-3-5:0",
    system_prompt="Concise summary format..."
)

manager = SlidingWindowWithSummarizationManager(
    window_size=15,  # More aggressive window
    summarization_agent=summarization_agent
)

main_agent = Agent(
    model="anthropic.claude-sonnet-3-5-v2:0",  # Expensive model
    conversation_manager=manager
)
```

### Resume Long Sessions
```python
# First session
manager = SlidingWindowWithSummarizationManager(window_size=20)
session_mgr = FileSessionManager(session_id="research_project")
agent = Agent(
    model="anthropic.claude-sonnet-3-5-v2:0",
    conversation_manager=manager,
    session_manager=session_mgr
)
# ... have conversation, triggers summarization ...

# Later: resume same session
agent2 = Agent(
    model="anthropic.claude-sonnet-3-5-v2:0",
    conversation_manager=manager,
    session_manager=session_mgr  # Same session ID
)
# Automatically restores with summary + recent messages
response = agent2("Continue from where we left off")
```

## How to Test

### Verify No Session Pollution
```python
import tempfile
from pathlib import Path

# Create a temporary session directory
with tempfile.TemporaryDirectory() as tmpdir:
    session_mgr = FileSessionManager(session_id="test", base_path=tmpdir)
    manager = SlidingWindowWithSummarizationManager(window_size=3)
    
    agent = Agent(
        model="anthropic.claude-sonnet-3-5-v2:0",
        conversation_manager=manager,
        session_manager=session_mgr
    )
    
    # Generate many messages to trigger summarization
    for i in range(10):
        agent(f"Message {i}")
    
    # Verify session doesn't contain internal prompts
    session_file = Path(tmpdir) / "test.json"
    session_content = session_file.read_text()
    
    assert "Please summarize" not in session_content
    assert "internal" not in session_content.lower()
    print("✓ No session pollution detected")
```

### Check Summarization Happens
```python
manager = SlidingWindowWithSummarizationManager(window_size=3)
agent = Agent(model="anthropic.claude-sonnet-3-5-v2:0", conversation_manager=manager)

# Add 5 messages (exceeds window_size=3)
for i in range(5):
    agent(f"Message {i}")

# Should have summary + 3 recent messages = 4 total
assert len(agent.messages) <= 4
assert any("summary" in str(msg).lower() for msg in agent.messages)
print(f"✓ Summarization working: {len(agent.messages)} messages")
```

## Troubleshooting

### "Cannot reduce context during active summarization"
**Cause:** Recursion detection triggered (shouldn't happen in normal use)  
**Solution:** Check if you're using the same agent for summarization without proper isolation

### Session loads unexpected messages
**Cause:** Likely using a parent class's session manager  
**Solution:** Ensure your summarization agent has `session_manager=None` and `hooks=[]`

### Tool use/result pairs get split incorrectly
**Cause:** Window size too small for typical tool interactions  
**Solution:** Increase `window_size` (default 40 is usually safe)

## Architecture

For implementation details and common pitfalls, see:
- **[SKILL.md](./SKILL.md)** - What to watch out for when building similar features
- **[architecture.md](./references/architecture.md)** - Complete design documentation, testing strategies, and DynamoDB type safety

## Performance Tips

1. **Use a cheaper model for summarization:**
   ```python
   summarization_agent = Agent(model="anthropic.claude-haiku-3-5:0", ...)
   ```

2. **Tune window size to your use case:**
   - Small window (10-15): Aggressive summarization, cheaper
   - Large window (40-100): Less summarization, more context

3. **Enable lazy initialization** (default):
   - Summarization agent only created when first needed
   - Avoids overhead if summarization never triggers

## References

- [Strands Agent SDK](https://strands.dev/docs)
- [Conversation Manager Pattern](https://strands.dev/docs/conversation-managers)
- [Claude Agent Skills Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)

## License

MIT

---

**Version:** 1.0.0  
**Last Updated:** 2025-04-24  
**Status:** Production Ready
