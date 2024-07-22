from typing import Optional, Tuple, List

from vocode.streaming.agent.abstract_factory import AbstractAgentFactory
from vocode.streaming.agent.base_agent import BaseAgent, RespondAgent
from vocode.streaming.agent.chat_gpt_agent import ChatGPTAgent
from vocode.streaming.models.agent import AgentConfig, AgentType, ChatGPTAgentConfig



class SpellerAgentConfig(AgentConfig, type="agent_speller"):
    """Configuration for SpellerAgent. Inherits from AgentConfig."""
    pass


class SpellerAgent(RespondAgent[SpellerAgentConfig]):
    """SpellerAgent class. Inherits from RespondAgent.

    This agent takes human input and returns it with spaces between each character.
    """

    def __init__(self, agent_config: SpellerAgentConfig):
        """Initializes SpellerAgent with the given configuration.

        Args:
            agent_config (SpellerAgentConfig): The configuration for this agent.
        """
        super().__init__(agent_config=agent_config)
        self.conversation: List[str] = []

    def record_conversation(self, speaker: str, text: str):
        """Records the conversation in memory.

        Args:
            speaker (str): The speaker ('Human' or 'Agent').
            text (str): The text to record.
        """
        self.conversation.append(f"{speaker}: {text}")

    async def respond(
        self,
        human_input: str,
        conversation_id: str,
        is_interrupt: bool = False,
    ) -> Tuple[Optional[str], bool]:
        """Generates a response from the SpellerAgent.

        The response is generated by joining each character in the human input with a space.
        The second element of the tuple indicates whether the agent should stop (False means it should not stop).

        Args:
            human_input (str): The input from the human user.
            conversation_id (str): The ID of the conversation.
            is_interrupt (bool): A flag indicating whether the agent was interrupted.

        Returns:
            Tuple[Optional[str], bool]: The generated response and a flag indicating whether to stop.
        """
        self.record_conversation("Human", human_input)
        response = "".join(c + " " for c in human_input)
        self.record_conversation("Agent", response)
        return response, False


class SpellerAgentFactory(AbstractAgentFactory):
    """Factory class for creating agents based on the provided agent configuration."""

    def create_agent(self, agent_config: AgentConfig) -> BaseAgent:
        """Creates an agent based on the provided agent configuration.
        Args:
            agent_config (AgentConfig): The configuration for the agent to be created.

        Returns:
            BaseAgent: The created agent.

        Raises:
            Exception: If the agent configuration type is not recognized.
        """
        # If the agent configuration type is CHAT_GPT, create a ChatGPTAgent.
        if isinstance(agent_config, ChatGPTAgentConfig):
            return ChatGPTAgent(agent_config=agent_config)
        # If the agent configuration type is agent_speller, create a SpellerAgent.
        elif isinstance(agent_config, SpellerAgentConfig):
            return SpellerAgent(agent_config=agent_config)
        # If the agent configuration type is not recognized, raise an exception.
        raise Exception("Invalid agent config")
    
