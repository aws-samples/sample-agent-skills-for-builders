"""Sliding window with summarization conversation history management.

This module provides a hybrid approach that combines the benefits of sliding window
and summarization strategies for managing conversation history. It solves the
recursive call issues by temporarily disabling the conversation manager during
summarization.
"""

from typing import TYPE_CHECKING, Any, cast

from strands.agent.conversation_manager import ConversationManager, NullConversationManager
from strands.tools._tool_helpers import noop_tool
from strands.tools.registry import ToolRegistry
from strands.types.content import Message
from strands.types.exceptions import ContextWindowOverflowException
from strands.types.tools import AgentTool

if TYPE_CHECKING:
    from strands.agent.agent import Agent

from log import getLogger

logger = getLogger()

DEFAULT_SUMMARIZATION_PROMPT = """You are a conversation summarizer. Provide a concise summary of the conversation \
history.

Format Requirements:
- You MUST create a structured and concise summary in bullet-point format.
- You MUST NOT respond conversationally.
- You MUST NOT address the user directly.
- You MUST NOT comment on tool availability.

Assumptions:
- You MUST NOT assume tool executions failed unless otherwise stated.

Task:
Your task is to create a structured summary document:
- It MUST contain bullet points with key topics and questions covered
- It MUST contain bullet points for all significant tools executed and their results
- It MUST contain bullet points for any code or technical information shared
- It MUST contain a section of key insights gained
- It MUST format the summary in the third person

Example format:

## Conversation Summary
* Topic 1: Key information
* Topic 2: Key information

## Tools Executed
* Tool X: Result Y

!IMPORTANT: do not use any tools to summarize the conversation!
"""


class SlidingWindowWithSummarizationManager(ConversationManager):
    """Implements a hybrid sliding window with summarization strategy.

    This manager maintains a sliding window of recent messages. When the window size
    is exceeded, instead of simply discarding old messages, it summarizes them and
    prepends the summary to the conversation history. This preserves important context
    while keeping the conversation manageable.

    Key features:
    - Maintains a fixed window size of recent messages
    - Summarizes overflow messages instead of discarding them
    - Preserves tool use/result pairs during summarization
    - Supports custom summarization agents and prompts
    - Prevents recursive calls by temporarily disabling conversation manager during summarization

    Key improvements over previous implementations:
    1. Prevents infinite recursion by temporarily replacing conversation_manager with NullConversationManager during summarization
    2. Prevents session pollution by temporarily disabling session_manager during summarization
    3. Proper window-based triggering (not ratio-based like parent SummarizingConversationManager)
    4. Does not pollute message history with "Please summarize" prompts
    5. Uses Strands framework's built-in NullConversationManager for consistency
    """

    def __init__(
        self,
        window_size: int = 40,
        summarization_agent: "Agent | None" = None,
        summarization_system_prompt: str | None = None,
    ):
        """Initialize the sliding window summarizing conversation manager.

        Args:
            window_size: Maximum number of messages to keep in the sliding window.
                Messages beyond this count will be summarized. Defaults to 40.
            summarization_agent: Optional dedicated agent to use for summarization.
                If provided, it will be used as-is. IMPORTANT: It should NOT have
                a session_manager or conversation_manager to avoid issues.
            summarization_system_prompt: Optional system prompt override for summarization.
                If None, uses the default summarization prompt. Cannot be used together
                with summarization_agent (agents come with their own system prompt).
                If neither is provided, a clean internal agent will be created.

        Raises:
            ValueError: If both summarization_agent and summarization_system_prompt are provided.
        """
        super().__init__()

        if summarization_agent is not None and summarization_system_prompt is not None:
            raise ValueError(
                "Cannot provide both summarization_agent and summarization_system_prompt. "
                "Agents come with their own system prompt."
            )

        self.window_size = window_size
        self._user_provided_agent = summarization_agent  # User-provided agent (if any)
        self._summarization_system_prompt = summarization_system_prompt
        self._summary_message: Message | None = None
        self._is_summarizing = False  # Flag to prevent recursive summarization

        # Internal clean agent for summarization (created lazily when needed)
        self._internal_summarization_agent: "Agent | None" = None

    def restore_from_session(self, state: dict[str, Any]) -> list[Message] | None:
        """Restores the conversation manager from its previous state in a session.

        Args:
            state: The previous state of the conversation manager.

        Returns:
            Optionally returns the previous conversation summary if it exists.
        """
        super().restore_from_session(state)
        self._summary_message = state.get("summary_message")
        return [self._summary_message] if self._summary_message else None

    def get_state(self) -> dict[str, Any]:
        """Returns a dictionary representation of the state for the conversation manager.

        Returns:
            Dictionary containing the summary message and parent state.
        """
        return {"summary_message": self._summary_message, **super().get_state()}

    def apply_management(self, agent: "Agent", **kwargs: Any) -> None:
        """Apply the sliding window management to the agent's conversation history.

        This method is called after every event loop cycle. When the message count
        exceeds the window size, it triggers summarization of overflow messages.

        Args:
            agent: The agent whose conversation history will be managed.
                The agent's messages list is modified in-place.
            **kwargs: Additional keyword arguments for future extensibility.
        """
        # Prevent recursive calls during summarization
        if self._is_summarizing:
            logger.debug("Currently summarizing, skipping apply_management")
            return

        # Count actual messages (excluding summary message if it exists)
        message_count = len(agent.messages)
        if self._summary_message and agent.messages and agent.messages[0] == self._summary_message:
            # If first message is our summary, count from second message onwards
            message_count = len(agent.messages) - 1

        if message_count <= self.window_size:
            logger.debug(
                "message_count=<%s>, window_size=<%s> | skipping context reduction",
                message_count,
                self.window_size,
            )
            return

        logger.info(
            "message_count=<%s>, window_size=<%s> | triggering summarization",
            message_count,
            self.window_size,
        )
        self.reduce_context(agent)

    def reduce_context(self, agent: "Agent", e: Exception | None = None) -> None:
        """Reduce context by summarizing overflow messages.

        When the conversation exceeds the window size, this method summarizes the
        overflow messages and replaces them with a summary message. The most recent
        messages (up to window_size) are preserved.

        Args:
            agent: The agent whose conversation history will be reduced.
                The agent's messages list is modified in-place.
            e: The exception that triggered the context reduction, if any.
            **kwargs: Additional keyword arguments for future extensibility.

        Raises:
            ContextWindowOverflowException: If the context cannot be reduced.
        """
        # Prevent recursive calls
        if self._is_summarizing:
            logger.warning("Recursive summarization detected, skipping")
            raise ContextWindowOverflowException("Cannot reduce context during active summarization")

        try:
            self._is_summarizing = True

            # Determine the split point
            summary_exists = self._summary_message and agent.messages and agent.messages[0] == self._summary_message

            if summary_exists:
                # If we have a summary, calculate overflow from position 1 onwards
                total_non_summary_messages = len(agent.messages) - 1
                if total_non_summary_messages <= self.window_size:
                    raise ContextWindowOverflowException("Cannot reduce: conversation is at or below window size")

                # Calculate how many messages to include in new summary
                # We want to keep the most recent window_size messages
                messages_to_summarize_count = total_non_summary_messages - self.window_size

                if messages_to_summarize_count <= 0:
                    raise ContextWindowOverflowException("Cannot reduce: insufficient overflow messages")

                # Split point is after the summary message
                # We'll summarize from index 1 to (1 + messages_to_summarize_count)
                split_point = 1 + messages_to_summarize_count
            else:
                # No existing summary
                total_messages = len(agent.messages)
                if total_messages <= self.window_size:
                    raise ContextWindowOverflowException("Cannot reduce: conversation is at or below window size")

                messages_to_summarize_count = total_messages - self.window_size
                split_point = messages_to_summarize_count

            # Adjust split point to avoid breaking ToolUse/ToolResult pairs
            split_point = self._adjust_split_point_for_tool_pairs(agent.messages, split_point)

            if summary_exists:
                if split_point <= 1:
                    raise ContextWindowOverflowException("Cannot reduce: split point too close to summary")
            else:
                if split_point <= 0:
                    raise ContextWindowOverflowException("Cannot reduce: invalid split point")

            # Extract messages to summarize
            # If summary exists, it will be included at index 0 (split_point accounts for this)
            messages_to_summarize = agent.messages[:split_point]
            remaining_messages = agent.messages[split_point:]

            # Track removed messages
            if summary_exists:
                # Don't count the summary message itself
                self.removed_message_count += len(messages_to_summarize) - 1
            else:
                self.removed_message_count += len(messages_to_summarize)

            # Generate new summary
            self._summary_message = self._generate_summary(messages_to_summarize, agent)

            # Replace with new summary + remaining messages
            agent.messages[:] = [self._summary_message] + remaining_messages

            logger.info(
                "Summarized %s messages, %s messages remaining (plus summary)",
                len(messages_to_summarize),
                len(remaining_messages),
            )

        except Exception as summarization_error:
            logger.error("Summarization failed: %s", summarization_error)
            raise summarization_error from e
        finally:
            self._is_summarizing = False

    def _get_or_create_summarization_agent(self, template_agent: "Agent") -> "Agent":
        """Get or create a clean agent for summarization.

        Args:
            template_agent: The main agent to use as template for model selection.

        Returns:
            A clean agent configured for summarization without session persistence.
        """
        # If user provided an agent, use it directly
        if self._user_provided_agent is not None:
            return self._user_provided_agent

        # Create internal agent if not already created
        if self._internal_summarization_agent is None:
            from strands import Agent as StrandsAgent

            # Determine system prompt
            system_prompt = (
                self._summarization_system_prompt
                if self._summarization_system_prompt is not None
                else DEFAULT_SUMMARIZATION_PROMPT
            )

            self._internal_summarization_agent = StrandsAgent(
                model=template_agent.model,
                system_prompt=system_prompt,
                conversation_manager=NullConversationManager(),  # Prevent recursion
                session_manager=None,  # CRITICAL: No persistence
                hooks=[],              # CRITICAL: No callbacks
                callback_handler=None,
            )

            logger.debug("Created clean internal summarization agent")

        return self._internal_summarization_agent

    def _generate_summary(self, messages: list[Message], agent: "Agent") -> Message:
        """Generate a summary of the provided messages.

        Uses a clean dedicated agent (either user-provided or internally created)
        to prevent session pollution and recursive calls.

        Args:
            messages: The messages to summarize.
            agent: The main agent instance (used as template for model selection).

        Returns:
            A message containing the conversation summary.

        Raises:
            Exception: If summary generation fails.
        """
        # Get or create a clean summarization agent
        summarization_agent = self._get_or_create_summarization_agent(agent)

        # Save original messages to restore later
        original_messages = summarization_agent.messages.copy()

        try:
            # Set messages to summarize
            summarization_agent.messages = messages

            logger.debug("Generating summary for %s messages", len(messages))

            # Generate summary
            result = summarization_agent("Please summarize this conversation.")

            logger.debug("Summary generated successfully")

            # Return summary as a user message
            return cast(Message, {**result.message, "role": "user"})

        finally:
            # Restore original messages
            summarization_agent.messages = original_messages

    def _adjust_split_point_for_tool_pairs(self, messages: list[Message], split_point: int) -> int:
        """Adjust the split point to avoid breaking ToolUse/ToolResult pairs.

        This ensures that the conversation remains valid by not splitting in the middle
        of a tool interaction sequence.

        Args:
            messages: The full list of messages.
            split_point: The initially calculated split point.

        Returns:
            The adjusted split point that doesn't break ToolUse/ToolResult pairs.

        Raises:
            ContextWindowOverflowException: If no valid split point can be found.
        """
        if split_point > len(messages):
            raise ContextWindowOverflowException("Split point exceeds message array length")

        if split_point == len(messages):
            return split_point

        # Find the next valid split_point
        while split_point < len(messages):
            if (
                # Oldest message cannot be a toolResult because it needs a toolUse preceding it
                any("toolResult" in content for content in messages[split_point]["content"])
                or (
                    # Oldest message can be a toolUse only if a toolResult immediately follows it.
                    any("toolUse" in content for content in messages[split_point]["content"])
                    and split_point + 1 < len(messages)
                    and not any("toolResult" in content for content in messages[split_point + 1]["content"])
                )
            ):
                split_point += 1
            else:
                break
        else:
            # If we didn't find a valid split_point, then we throw
            raise ContextWindowOverflowException("Unable to find valid split point!")

        return split_point
