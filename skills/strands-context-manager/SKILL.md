---
name: strands-context-manager
description: Strands conversation/context manager patterns, including sliding window with summarization. Use when building agents with context management, preventing session pollution, or implementing conversation compaction.
license: MIT
metadata:
  author: sample-skills-for-builders
  version: "1.0.0"
---

# Strands Context Manager (Sliding Window with Summarization)

Strands Agents SDK conversation manager combining sliding window and summarization strategies.

## When to Apply

Reference this skill when:
- Building Strands agents with long conversations
- Implementing context window management
- Preventing session pollution in multi-turn dialogs
- Combining sliding window with summarization

## Critical Pitfalls

### 1. Inheritance Pitfall
**DON'T** inherit from `SummarizingConversationManager`.
**DO** inherit from base `ConversationManager`.

### 2. Infinite Recursion
Use `_is_summarizing` flag with try/finally to prevent recursion during summarization calls.

### 3. Hook Closure Problem (MOST CRITICAL)
Lambda closures capture session_manager references during initialization. Create summarization agent WITHOUT session_manager, hooks, or persistence.

## Implementation Pattern

```python
class SlidingWindowWithSummarizationManager(ConversationManager):
    def __init__(self, window_size=40, summarization_agent=None, summarization_system_prompt=None):
        self._is_summarizing = False
        self._summarization_agent = summarization_agent  # Lazy init when None

    def _get_summarization_agent(self):
        # Create clean agent without session_manager
        return Agent(
            # NO session_manager, NO hooks
        )
```

## Usage

```python
from conversation_manager import SlidingWindowWithSummarizationManager

manager = SlidingWindowWithSummarizationManager(
    window_size=20,
)
```

## Critical Test

```python
def test_no_session_pollution():
    # Verify internal messages don't persist
    # Verify no "Please summarize" in session
```

## References

- [Architecture](./references/architecture.md) - Detailed design and testing
