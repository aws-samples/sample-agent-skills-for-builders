# Agent Skill: Building a Strands Context Manager (Sliding Window with Summarization)

## Overview

This skill guides you through creating a production-ready conversation manager that combines sliding window and summarization strategies for the Strands Agent framework. You'll learn to avoid common pitfalls and implement a robust solution that prevents recursion, session pollution, and message leakage.

## Problem Statement

When building conversational AI agents, managing conversation history is critical. Long conversations can:
- Exceed model context windows
- Increase latency and costs
- Lose important historical context

A sliding window with summarization approach solves this by:
1. Keeping recent N messages (sliding window)
2. Summarizing older messages instead of discarding them
3. Maintaining context while controlling token usage

## Common Pitfalls and Solutions

### ❌ Pitfall 1: Inheriting from SummarizingConversationManager

**The Temptation:**
```python
from strands.agent.conversation_manager import SummarizingConversationManager

class MySlidingWindowSummarizingManager(SummarizingConversationManager):
    def __init__(self, window_size=40, summary_ratio=0.3, ...):
        super().__init__(summary_ratio=summary_ratio, ...)
        self.window_size = window_size
```

**Why This Fails:**

1. **Conflicting Semantics**:
   - Parent uses `summary_ratio` (percentage-based)
   - Child uses `window_size` (fixed count)
   - These don't align naturally

2. **Inappropriate Triggering**:
   - Parent's `apply_management()` is a no-op
   - Parent's `reduce_context()` uses ratio calculations
   - Results in unpredictable behavior

3. **Message Pollution**:
   - Parent's `_generate_summary()` adds "Please summarize" to messages
   - These internal messages pollute history

**Solution**: Inherit directly from `ConversationManager` base class:

```python
from strands.agent.conversation_manager import ConversationManager

class SlidingWindowWithSummarizationManager(ConversationManager):
    def __init__(self, window_size=40, ...):
        super().__init__()
        self.window_size = window_size
        # Implement from scratch with clear semantics
```

**Benefits**:
- ✅ Full control over implementation
- ✅ Clear window-based semantics
- ✅ No inherited quirks or conflicts

---

### ❌ Pitfall 2: Using the Original Agent for Summarization

**The Temptation:**
```python
def _generate_summary(self, messages, agent):
    # Reuse the main agent
    original_messages = agent.messages.copy()

    try:
        agent.messages = messages
        result = agent("Please summarize this conversation.")
        return result.message
    finally:
        agent.messages = original_messages
```

**Why This Fails:**

**Problem 1: Infinite Recursion**

```
Main Agent (with conversation_manager)
  ├─ User asks question
  ├─ Messages exceed window_size
  ├─ conversation_manager.reduce_context() called
  │   └─ _generate_summary() called
  │       └─ agent("Please summarize...")
  │           ├─ Event loop runs
  │           ├─ apply_management() called
  │           ├─ Still exceeds window_size!
  │           └─ reduce_context() called AGAIN
  │               └─ 💥 INFINITE RECURSION
```

**Problem 2: Session Pollution**

```
Main Agent (with session_manager via hooks)
  └─ session_manager registered hooks:
      └─ MessageAddedEvent → lambda: session_manager.append_message(...)

When summarizing:
  agent.messages = messages_to_summarize
  agent("Please summarize...")
    ├─ Adds "Please summarize..." message
    │   └─ Triggers MessageAddedEvent
    │       └─ lambda calls session_manager.append_message()
    │           └─ 💥 Internal message persisted to session!
    │
    └─ Adds "## Summary..." response
        └─ Triggers MessageAddedEvent
            └─ 💥 Summary persisted to session!

Next session load:
  └─ Restores polluted messages from storage
```

**Solution 1: Add Recursion Guard**

```python
class SlidingWindowWithSummarizationManager(ConversationManager):
    def __init__(self, ...):
        super().__init__()
        self._is_summarizing = False  # Recursion flag

    def apply_management(self, agent):
        if self._is_summarizing:  # Guard against recursion
            return
        # ... normal logic

    def reduce_context(self, agent, e=None):
        if self._is_summarizing:
            raise ContextWindowOverflowException("Cannot reduce during summarization")

        try:
            self._is_summarizing = True
            # ... summarization logic
        finally:
            self._is_summarizing = False
```

**Benefits**:
- ✅ Prevents infinite loops
- ✅ Clear error messages
- ✅ Defense-in-depth protection

---

### ❌ Pitfall 3: Attempting to Disable Session Manager at Runtime

**The Temptation:**
```python
def _generate_summary(self, messages, agent):
    # Try to disable session persistence
    original_session_manager = agent._session_manager
    agent._session_manager = None  # ❌ This doesn't work!

    try:
        agent.messages = messages
        result = agent("Please summarize...")
        return result.message
    finally:
        agent._session_manager = original_session_manager
```

**Why This Fails: The Closure Problem**

```python
# When Agent is initialized with session_manager:
class Agent:
    def __init__(self, session_manager=None, ...):
        self._session_manager = session_manager
        if self._session_manager:
            self.hooks.add_hook(self._session_manager)
            # ↑ This registers callbacks

# In SessionManager.register_hooks():
class SessionManager:
    def register_hooks(self, registry):
        # Lambda captures self (the session_manager object) via closure
        registry.add_callback(
            MessageAddedEvent,
            lambda event: self.append_message(event.message, event.agent)
            #             ^^^^ self = session_manager object (captured in closure)
        )

# Later, when you try to disable:
agent._session_manager = None  # ❌ Only changes the attribute

# But when messages are added:
agent.messages.append(new_message)
  → Triggers MessageAddedEvent
  → Invokes lambda: self.append_message(...)
                    ^^^^ self still points to original session_manager!
  → Message still persisted! 💥
```

**The Root Cause**: Lambda functions in hook callbacks captured the `session_manager` object via **closure** when `register_hooks()` was called during agent initialization. Changing `agent._session_manager` doesn't affect these already-registered callbacks.

**Why Setting Attributes Doesn't Work**:
1. Hooks callbacks are **already registered** in the registry
2. Lambda closures have **already captured** the session_manager reference
3. Modifying `agent._session_manager` only changes the **attribute**, not the closure
4. The **captured reference** in lambdas remains active

**Solution**: Create a Clean Agent from the Start

```python
def _get_or_create_summarization_agent(self, template_agent):
    """Create a clean agent without session persistence from initialization."""
    if self._internal_agent is None:
        from strands import Agent

        self._internal_agent = Agent(
            model=template_agent.model,
            system_prompt=DEFAULT_SUMMARIZATION_PROMPT,
            conversation_manager=NullConversationManager(),  # Prevent recursion
            session_manager=None,  # CRITICAL: No session manager
            hooks=[],              # CRITICAL: No hooks, no callbacks
            callback_handler=None,
        )

    return self._internal_agent
```

**Why This Works**:
- ✅ Agent created **without hooks** from the start
- ✅ No lambda closures capturing session_manager
- ✅ No runtime attribute modification needed
- ✅ Clean separation of concerns

---

## Best Practices: Complete Implementation

### 1. Architecture Overview

```
Main Agent (User-Facing)
  ├─ session_manager: AgentCoreMemory/S3/File
  ├─ conversation_manager: SlidingWindowWithSummarizationManager
  │   └─ _internal_summarization_agent (Created lazily)
  │       ├─ session_manager: None ✅
  │       ├─ hooks: [] ✅
  │       └─ conversation_manager: NullConversationManager ✅
  └─ hooks: [session_manager, other_hooks...]
```

### 2. Complete Implementation

```python
from typing import TYPE_CHECKING, Any, cast

from strands.agent.conversation_manager import ConversationManager, NullConversationManager
from strands.tools._tool_helpers import noop_tool
from strands.tools.registry import ToolRegistry
from strands.types.content import Message
from strands.types.exceptions import ContextWindowOverflowException
from strands.types.tools import AgentTool

if TYPE_CHECKING:
    from strands.agent.agent import Agent

DEFAULT_SUMMARIZATION_PROMPT = """You are a conversation summarizer..."""


class SlidingWindowWithSummarizationManager(ConversationManager):
    """Sliding window with summarization conversation manager.

    Key Design Decisions:
    1. Uses clean internal agent for summarization (no session_manager, no hooks)
    2. Implements recursion guard with _is_summarizing flag
    3. Inherits directly from ConversationManager (not SummarizingConversationManager)
    4. Lazy initialization of internal agent
    """

    def __init__(
        self,
        window_size: int = 40,
        summarization_agent: "Agent | None" = None,
        summarization_system_prompt: str | None = None,
    ):
        """Initialize the manager.

        Args:
            window_size: Maximum number of messages in sliding window.
            summarization_agent: Optional user-provided clean agent.
            summarization_system_prompt: Optional custom prompt.
        """
        super().__init__()

        if summarization_agent is not None and summarization_system_prompt is not None:
            raise ValueError("Cannot provide both agent and prompt")

        self.window_size = window_size
        self._user_provided_agent = summarization_agent
        self._summarization_system_prompt = summarization_system_prompt
        self._summary_message: Message | None = None
        self._is_summarizing = False  # Recursion guard

        # Internal agent (created lazily when needed)
        self._internal_summarization_agent: "Agent | None" = None

    def apply_management(self, agent: "Agent") -> None:
        """Apply sliding window management."""
        # Guard against recursion
        if self._is_summarizing:
            return

        # Count messages (excluding summary if present)
        message_count = len(agent.messages)
        if self._summary_message and agent.messages and agent.messages[0] == self._summary_message:
            message_count = len(agent.messages) - 1

        if message_count <= self.window_size:
            return

        # Trigger summarization
        self.reduce_context(agent)

    def reduce_context(self, agent: "Agent", e: Exception | None = None) -> None:
        """Reduce context by summarizing overflow messages."""
        # Guard against recursion
        if self._is_summarizing:
            raise ContextWindowOverflowException("Cannot reduce during summarization")

        try:
            self._is_summarizing = True

            # Calculate split point (keep last window_size messages)
            summary_exists = (
                self._summary_message
                and agent.messages
                and agent.messages[0] == self._summary_message
            )

            if summary_exists:
                total_non_summary = len(agent.messages) - 1
                if total_non_summary <= self.window_size:
                    raise ContextWindowOverflowException("At or below window size")

                messages_to_summarize_count = total_non_summary - self.window_size
                split_point = 1 + messages_to_summarize_count
            else:
                total = len(agent.messages)
                if total <= self.window_size:
                    raise ContextWindowOverflowException("At or below window size")

                messages_to_summarize_count = total - self.window_size
                split_point = messages_to_summarize_count

            # Adjust for tool pairs
            split_point = self._adjust_split_point_for_tool_pairs(agent.messages, split_point)

            # Extract messages
            messages_to_summarize = agent.messages[:split_point]
            remaining_messages = agent.messages[split_point:]

            # Track removed count
            if summary_exists:
                self.removed_message_count += len(messages_to_summarize) - 1
            else:
                self.removed_message_count += len(messages_to_summarize)

            # Generate new summary
            self._summary_message = self._generate_summary(messages_to_summarize, agent)

            # Replace with summary + remaining
            agent.messages[:] = [self._summary_message] + remaining_messages

        except Exception as error:
            raise error from e
        finally:
            self._is_summarizing = False

    def _get_or_create_summarization_agent(self, template_agent: "Agent") -> "Agent":
        """Get or create clean agent for summarization.

        Critical: This agent must NOT have session_manager or hooks.
        """
        # Use user-provided agent if available
        if self._user_provided_agent is not None:
            return self._user_provided_agent

        # Create internal agent (lazy initialization)
        if self._internal_summarization_agent is None:
            from strands import Agent

            system_prompt = (
                self._summarization_system_prompt
                if self._summarization_system_prompt is not None
                else DEFAULT_SUMMARIZATION_PROMPT
            )

            # Create clean agent WITHOUT session_manager and hooks
            self._internal_summarization_agent = Agent(
                model=template_agent.model,
                system_prompt=system_prompt,
                conversation_manager=NullConversationManager(),  # Prevent recursion
                session_manager=None,  # CRITICAL: No persistence
                hooks=[],              # CRITICAL: No callbacks
                callback_handler=None,
            )

        return self._internal_summarization_agent

    def _generate_summary(self, messages: list[Message], agent: "Agent") -> Message:
        """Generate summary using clean agent."""
        # Get clean agent (no session_manager, no hooks)
        summarization_agent = self._get_or_create_summarization_agent(agent)

        # Only need to manage messages
        original_messages = summarization_agent.messages.copy()

        try:
            summarization_agent.messages = messages
            result = summarization_agent("Please summarize this conversation.")
            return cast(Message, {**result.message, "role": "user"})
        finally:
            summarization_agent.messages = original_messages

    def _adjust_split_point_for_tool_pairs(
        self, messages: list[Message], split_point: int
    ) -> int:
        """Adjust split point to avoid breaking ToolUse/ToolResult pairs."""
        if split_point >= len(messages):
            return split_point

        # Advance split point until valid boundary
        while split_point < len(messages):
            current = messages[split_point]

            # Can't start with toolResult
            if any("toolResult" in c for c in current["content"]):
                split_point += 1
                continue

            # Can't split toolUse from its result
            if any("toolUse" in c for c in current["content"]):
                if (split_point + 1 < len(messages) and
                    not any("toolResult" in c for c in messages[split_point + 1]["content"])):
                    split_point += 1
                    continue

            break

        if split_point >= len(messages):
            raise ContextWindowOverflowException("Unable to find valid split point")

        return split_point

    # Implement session persistence methods
    def restore_from_session(self, state: dict[str, Any]) -> list[Message] | None:
        """Restore from session."""
        super().restore_from_session(state)
        self._summary_message = state.get("summary_message")
        return [self._summary_message] if self._summary_message else None

    def get_state(self) -> dict[str, Any]:
        """Get state for persistence."""
        return {"summary_message": self._summary_message, **super().get_state()}
```

### 3. Key Implementation Points

#### ✅ DO: Use Clean Agent Pattern

```python
# Good: Clean agent created from initialization
self._internal_agent = Agent(
    model=template_agent.model,
    session_manager=None,  # No persistence
    hooks=[],              # No callbacks
)
```

#### ❌ DON'T: Modify Existing Agent

```python
# Bad: Trying to disable at runtime
agent._session_manager = None  # Doesn't work due to closures
agent.hooks.clear()             # May break other functionality
```

#### ✅ DO: Implement Recursion Guards

```python
self._is_summarizing = False

def apply_management(self, agent):
    if self._is_summarizing:  # Early return
        return
    # ...

def reduce_context(self, agent, e=None):
    if self._is_summarizing:  # Raise exception
        raise ContextWindowOverflowException("...")

    try:
        self._is_summarizing = True
        # ...
    finally:
        self._is_summarizing = False  # Always restore
```

#### ✅ DO: Lazy Initialization

```python
# Create agent only when first needed
if self._internal_agent is None:
    self._internal_agent = Agent(...)
return self._internal_agent
```

**Benefits**:
- Defers model loading until necessary
- Avoids initialization costs if never triggered
- Allows using template_agent for model selection

---

## Testing Strategy

### 1. Unit Tests

```python
def test_no_session_pollution():
    """Verify internal messages are not persisted."""
    session_manager = FileSessionManager(session_id="test")
    manager = SlidingWindowWithSummarizationManager(window_size=5)

    agent = Agent(
        model="...",
        session_manager=session_manager,
        conversation_manager=manager,
    )

    # Generate many messages to trigger summarization
    for i in range(10):
        agent(f"Message {i}")

    # Check messages don't contain internal summarization prompts
    for msg in agent.messages:
        content_str = str(msg.get("content", []))
        assert "Please summarize" not in content_str

    # Reload from session
    new_agent = Agent(
        model="...",
        session_manager=session_manager,
        conversation_manager=manager,
    )

    # Verify no pollution
    for msg in new_agent.messages:
        content_str = str(msg.get("content", []))
        assert "Please summarize" not in content_str

def test_no_recursion():
    """Verify recursion is prevented."""
    manager = SlidingWindowWithSummarizationManager(window_size=3)

    # Set recursion flag
    manager._is_summarizing = True

    mock_agent = MagicMock()
    mock_agent.messages = [create_message(f"Msg {i}") for i in range(10)]

    # Should skip without error
    manager.apply_management(mock_agent)

    # Messages unchanged
    assert len(mock_agent.messages) == 10
```

### 2. Integration Tests

```python
def test_with_real_agent():
    """Test with real Strands agent."""
    manager = SlidingWindowWithSummarizationManager(window_size=10)

    agent = Agent(
        model="anthropic.claude-sonnet-3-5-v2:0",
        conversation_manager=manager,
        session_manager=FileSessionManager(session_id="integration-test"),
    )

    # Long conversation
    for i in range(20):
        response = agent(f"Tell me a fact about number {i}")
        assert response.text

    # Should have: summary + 10 recent messages
    assert len(agent.messages) == 11

    # First message should be summary
    first_msg = agent.messages[0]
    assert "summary" in str(first_msg.get("content", [])).lower()
```

---

## Common Mistakes and Solutions

### Mistake 1: Using Parent Agent's Hooks

```python
# ❌ Bad
def _generate_summary(self, messages, agent):
    # This agent has hooks that will persist messages
    result = agent("Please summarize...")
```

**Solution**: Use dedicated clean agent

```python
# ✅ Good
def _generate_summary(self, messages, agent):
    clean_agent = self._get_or_create_summarization_agent(agent)
    # This agent has no hooks, no persistence
    result = clean_agent("Please summarize...")
```

### Mistake 2: Forgetting Recursion Guard

```python
# ❌ Bad
def apply_management(self, agent):
    if len(agent.messages) > self.window_size:
        self.reduce_context(agent)  # Can recurse!
```

**Solution**: Add flag check

```python
# ✅ Good
def apply_management(self, agent):
    if self._is_summarizing:
        return  # Prevent recursion
    if len(agent.messages) > self.window_size:
        self.reduce_context(agent)
```

### Mistake 3: Not Handling Tool Pairs

```python
# ❌ Bad
split_point = len(agent.messages) - self.window_size
messages_to_summarize = agent.messages[:split_point]
```

**Solution**: Adjust for tool pairs

```python
# ✅ Good
split_point = len(agent.messages) - self.window_size
split_point = self._adjust_split_point_for_tool_pairs(agent.messages, split_point)
messages_to_summarize = agent.messages[:split_point]
```

---

## Performance Considerations

### 1. Model Selection

```python
# Use cheaper model for summarization
summarization_agent = Agent(
    model="anthropic.claude-haiku-3-5:0",  # Cheaper, faster
    # ...
)

main_agent = Agent(
    model="anthropic.claude-sonnet-4-5-v2:0",  # More capable
    conversation_manager=manager,
)
```

### 2. Lazy Initialization

```python
# Don't create summarization agent until needed
if self._internal_agent is None:
    self._internal_agent = Agent(...)
```

### 3. Summary Prompt Optimization

```python
# Keep summaries concise
DEFAULT_SUMMARIZATION_PROMPT = """Provide a concise summary (max 500 words).
Focus on key decisions, actions, and unresolved questions."""
```

---

## Configuration Loading and Data Type Safety

### YAML vs DynamoDB Number Type Handling

**Critical Issue: DynamoDB Uses Decimal for Numbers**

When loading agent configuration from DynamoDB (after initial YAML load), numeric values are stored as `Decimal` type, not Python's native `int` or `float`.

#### The Problem

```python
# Initial load from YAML to DynamoDB
config = {
    "conversation_manager": {
        "type": "sliding_window",
        "window_size": 40  # Python int
    }
}

# After persisting to DynamoDB and reading back
config = {
    "conversation_manager": {
        "type": "sliding_window",
        "window_size": Decimal('40')  # boto3 returns Decimal!
    }
}

# Later in code - RUNTIME ERROR
split_point = window_size - 10  # Decimal('30')
messages[split_point]  # TypeError: list indices must be integers or slices, not Decimal
```

#### Real-World Error Example

```python
# File: conversation_managers/strands_context_manager.py, line 373
def _adjust_split_point_for_tool_pairs(self, messages, split_point):
    while split_point < len(messages):
        # ❌ CRASH: If split_point is Decimal from config
        if any("toolResult" in content for content in messages[split_point]["content"]):
            split_point += 1
            continue
        # ...
```

**Error Message:**
```
TypeError: list indices must be integers or slices, not decimal.Decimal
```

#### The Solution: Explicit Type Conversion

**In Agent Loader:**

```python
# File: agent_loader.py
def _create_conversation_manager(self, config: dict | None) -> ConversationManager | None:
    if not config:
        return None

    manager_type = config.get("type", "").lower()

    # ✅ CRITICAL: Convert to int to handle Decimal from DynamoDB
    window_size = int(config.get("window_size", 40))

    if manager_type == "sliding_window":
        return SlidingWindowConversationManager(window_size=window_size)
    elif manager_type == "sliding_window_summarizing":
        return SlidingWindowWithSummarizationManager(window_size=window_size)
    # ...
```

**In Conversation Manager (Defense in Depth):**

```python
class SlidingWindowWithSummarizationManager(ConversationManager):
    def __init__(self, window_size: int = 40):
        super().__init__()

        # ✅ Additional safety: Ensure int type
        self.window_size = int(window_size)
        # ...
```

#### Type-Safe Helper Function

For robust production code:

```python
from decimal import Decimal
from typing import Union

def safe_int(value: Union[int, float, Decimal, str, None], default: int = 0) -> int:
    """
    Safely convert various numeric types to int.

    Handles:
    - Python native int/float
    - DynamoDB Decimal
    - String representations
    - None values

    Args:
        value: Value to convert
        default: Default value if conversion fails

    Returns:
        Integer value

    Examples:
        >>> safe_int(Decimal('40'))
        40
        >>> safe_int(40.5)
        40
        >>> safe_int("30")
        30
        >>> safe_int(None, default=100)
        100
    """
    if value is None:
        return default

    try:
        return int(value)
    except (ValueError, TypeError):
        return default

# Usage in agent loader
window_size = safe_int(config.get("window_size"), default=40)
```

#### Where Type Conversion is Required

Apply `int()` conversion when:

1. **Reading from DynamoDB**: All numeric config values
2. **Using as list/array indices**: `messages[index]`
3. **Range operations**: `range(window_size)`
4. **Arithmetic with integers**: `split_point = total - window_size`
5. **Comparison with integers**: `if message_count > window_size`

#### Testing Data Type Safety

```python
def test_decimal_window_size():
    """Test that Decimal window_size from DynamoDB works correctly."""
    from decimal import Decimal

    # Simulate DynamoDB data
    config = {
        "type": "sliding_window",
        "window_size": Decimal('30')  # DynamoDB returns Decimal
    }

    manager = _create_conversation_manager(config)
    assert isinstance(manager.window_size, int)
    assert manager.window_size == 30

    # Test actual usage
    agent = Agent(
        model="anthropic.claude-sonnet-4-5-v2:0",
        conversation_manager=manager
    )

    for i in range(50):
        agent(f"Message {i}")

    # Should not crash with Decimal index error
    assert len(agent.messages) <= 31  # 30 + summary
```

#### DynamoDB Number Type Reference

**What boto3 Returns:**

| YAML Type | DynamoDB Storage | boto3 Read Type |
|-----------|------------------|-----------------|
| `int: 40` | N (Number) | `Decimal('40')` |
| `float: 0.5` | N (Number) | `Decimal('0.5')` |
| `str: "hello"` | S (String) | `str` |
| `bool: true` | BOOL | `bool` |
| `list: [1,2]` | L (List) | `list` with Decimal items |
| `dict: {a:1}` | M (Map) | `dict` with Decimal values |

**Why boto3 Uses Decimal:**

- Preserves exact precision for financial calculations
- Avoids floating-point rounding errors
- Standard practice for DynamoDB numeric types

**Best Practice:**

```python
# Always convert numeric config on read
def load_agent_config(agent_id: str) -> dict:
    """Load agent config from DynamoDB with type normalization."""
    response = dynamodb.get_item(Key={'id': agent_id})
    config = response['Item']

    # Normalize conversation_manager config if present
    if 'conversation_manager' in config:
        cm = config['conversation_manager']
        if 'window_size' in cm:
            cm['window_size'] = int(cm['window_size'])  # ✅ Convert Decimal to int

    return config
```

## Deployment Checklist

- [ ] Implemented recursion guard with `_is_summarizing` flag
- [ ] Created clean agent without `session_manager` or `hooks`
- [ ] Used lazy initialization for internal agent
- [ ] Added tool pair preservation logic
- [ ] Implemented `restore_from_session()` and `get_state()`
- [ ] Added comprehensive logging
- [ ] Wrote unit tests for recursion prevention
- [ ] Wrote integration tests for session persistence
- [ ] Tested with real LLM and session manager
- [ ] Documented configuration options
- [ ] Added monitoring for summarization frequency
- [ ] **Added type conversion for DynamoDB Decimal values in config loading**
- [ ] **Tested with DynamoDB-loaded config (not just YAML)**

---

## References

- [Strands Agent SDK Documentation](https://strands.dev/docs)
- [Strands Conversation Managers](https://strands.dev/docs/conversation-managers)
- [Claude Agent Skills Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
- [Implementation Example](../scripts/strands-context-manager.py)
- [Session Pollution Analysis](./SESSION_POLLUTION_FIX.md)

---

## Summary

Building a robust sliding window with summarization conversation manager requires:

1. **Direct Inheritance**: Inherit from `ConversationManager`, not `SummarizingConversationManager`
2. **Clean Agent Pattern**: Create a dedicated agent without session_manager or hooks
3. **Recursion Protection**: Use flag guards in both `apply_management` and `reduce_context`
4. **Lazy Initialization**: Create internal agent only when first needed
5. **Simple State Management**: Only manage `messages`, no complex save/restore

**Key Insight**: The hook closure problem cannot be solved by modifying agent attributes at runtime. The only reliable solution is to use a clean agent from initialization.

This approach ensures:
- ✅ No infinite recursion
- ✅ No session pollution
- ✅ Clean conversation history
- ✅ Production-ready reliability

---

**Version**: 1.0.0
**Date**: 2025-01-27
**Author**: Claude Code
**Status**: Production Ready
