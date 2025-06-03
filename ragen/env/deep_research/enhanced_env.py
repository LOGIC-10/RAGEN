"""
Enhanced Deep Research Environment that loads instruction mapping 
from criticsearch package instead of local files.
"""

from __future__ import annotations
import json
import uuid
from pathlib import Path
from typing import Dict, Any, Tuple
import logging

from jinja2 import Template
from ragen.env.base import BaseLanguageBasedEnv
from ragen.env.deep_research.config import DeepResearchEnvConfig
from ragen.utils.instruction_loader import load_instruction_mapping, get_instruction_for_file

from criticsearch.base_agent import BaseAgent
from criticsearch.tools.tool_registry import ToolRegistry
from criticsearch.tools.note_manager import set_session, taking_notes, retrieve_notes
from criticsearch.utils import extract_tag_content
from criticsearch.reportbench.instruction_generator import InstructionGenerator
from criticsearch.reportbench.verifier import ReportVerifier


class EnhancedDeepResearchEnv(BaseLanguageBasedEnv):
    """
    Enhanced Deep Research Environment that demonstrates how to load
    instruction mapping from criticsearch package resources.
    """
    metadata = {"render.modes": ["human"]}

    def __init__(self, config: DeepResearchEnvConfig = None):
        super().__init__()
        self.cfg = config or DeepResearchEnvConfig()
        self.config = self.cfg
        self.episode_id: str | None = None
        self.current_observation_for_action: str | None = None

        # Setup logging
        self.save_path = Path("log")
        self.save_path.mkdir(parents=True, exist_ok=True)
        
        logger_name = f"{__name__}.{self.__class__.__name__}.{str(uuid.uuid4())[:8]}"
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(logging.INFO)
        
        if not self.logger.handlers:
            log_file_path = self.save_path / "enhanced_env.log"
            file_handler = logging.FileHandler(log_file_path, mode='a', encoding='utf-8')
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
            self.logger.propagate = False

        # Load instruction mapping from criticsearch package
        self._load_instruction_mapping()

        # Initialize CriticSearch components
        self.agent = BaseAgent()
        self.registry = ToolRegistry()
        self.history: list[Dict[str, str]] = []
        self._step_count: int = 0

        self.instruction_generator = InstructionGenerator()
        self.section_level_samples: list[dict] = (
            self.instruction_generator.get_all_section_level_instructions()
        )
        
        # Use instruction mapping to enhance samples if available
        self._enhance_samples_with_mapping()
        
        from itertools import cycle
        self._sample_iter = cycle(self.section_level_samples)
        self.current_facts: list[dict] | None = None  
        self.render_cache = None

    def _load_instruction_mapping(self):
        """Load instruction mapping from criticsearch package."""
        self._log_info("Loading instruction mapping from criticsearch package...")
        
        # Try different possible package locations
        possible_packages = [
            "criticsearch.data",
            "criticsearch.resources", 
            "criticsearch.reportbench.data",
            "criticsearch"
        ]
        
        self.instruction_mapping = {}
        for pkg in possible_packages:
            try:
                mapping = load_instruction_mapping(pkg)
                if mapping:
                    self.instruction_mapping = mapping
                    self._log_info(f"Successfully loaded {len(mapping)} instructions from {pkg}")
                    break
            except Exception as e:
                self._log_info(f"Failed to load from {pkg}: {e}")
        
        if not self.instruction_mapping:
            self._log_warning("Could not load instruction mapping from any package location")

    def _enhance_samples_with_mapping(self):
        """Enhance section level samples with instruction mapping if available."""
        if not self.instruction_mapping:
            return
            
        # This is an example of how you might enhance the samples
        # The actual implementation would depend on how you want to use the mapping
        enhanced_samples = []
        for sample in self.section_level_samples:
            enhanced_sample = sample.copy()
            
            # Example: Try to find a matching instruction for this sample
            # You could match based on keywords, themes, etc.
            sample_prompt = sample.get("section_full_prompt", "").lower()
            
            # Simple keyword matching example
            for filename, instruction in self.instruction_mapping.items():
                if any(keyword in filename.lower() for keyword in ["election", "political", "news"]):
                    if any(keyword in sample_prompt for keyword in ["election", "political", "news"]):
                        enhanced_sample["enhanced_instruction"] = instruction
                        enhanced_sample["source_file"] = filename
                        break
            
            enhanced_samples.append(enhanced_sample)
        
        self.section_level_samples = enhanced_samples
        self._log_info(f"Enhanced {len(enhanced_samples)} samples with instruction mapping")

    def get_instruction_for_topic(self, topic: str) -> str:
        """
        Get instruction for a specific topic from the loaded mapping.
        
        Args:
            topic: Topic to search for in the instruction mapping
            
        Returns:
            Matching instruction or empty string if not found
        """
        if not self.instruction_mapping:
            return ""
            
        # Simple search - you could make this more sophisticated
        topic_lower = topic.lower()
        for filename, instruction in self.instruction_mapping.items():
            if topic_lower in filename.lower():
                return instruction
                
        return ""

    def _log_info(self, message: str):
        self.logger.info(f"[Epi: {self.episode_id} | Step: {self._step_count}] {message}")

    def _log_warning(self, message: str):
        self.logger.warning(f"[Epi: {self.episode_id} | Step: {self._step_count}] {message}")

    def _log_error(self, message: str):
        self.logger.error(f"[Epi: {self.episode_id} | Step: {self._step_count}] {message}")

    def reset(self, seed=None, **kw) -> str:
        """Reset the environment with enhanced instruction loading."""
        self.episode_id = str(uuid.uuid4())
        self._step_count = 0
        self.history = []

        set_session(str(uuid.uuid4()))
        sample = next(self._sample_iter)
        
        # Use enhanced instruction if available
        if "enhanced_instruction" in sample:
            user_prompt = f"Enhanced Query: {sample['enhanced_instruction']}"
            self._log_info(f"Using enhanced instruction from {sample.get('source_file', 'unknown')}")
        else:
            user_prompt = "User Query: " + sample["section_full_prompt"]
        
        self.current_facts = sample["extracted_facts"]

        # Setup tool schemas
        schemas = []
        for fn in [
            self.agent.search_aggregator.search,
            self.agent.content_scraper.scrape,
            taking_notes,
            retrieve_notes,
        ]:
            schemas.extend(self.registry.get_or_create_tool_schema(fn))

        tpl = Path(self.agent.prompts_dir) / "tool_use_short.txt"
        system_prompt_content = Template(tpl.read_text(encoding="utf-8")).render(
            AVAILABLE_TOOLS=json.dumps(schemas, ensure_ascii=False),
        )

        self.history.append({"role": "system", "content": system_prompt_content})
        self.history.append({"role": "user", "content": user_prompt})
        
        full_prompt = f"{system_prompt_content}\n\n{user_prompt}"
        self.current_observation_for_action = full_prompt

        self._log_info("--- Enhanced Environment Reset ---")
        self._log_info(f"User Prompt: {user_prompt}")
        
        # Log instruction mapping status
        if self.instruction_mapping:
            self._log_info(f"Instruction mapping loaded: {len(self.instruction_mapping)} entries")
        else:
            self._log_warning("No instruction mapping available")

        self.render_cache = full_prompt
        return full_prompt

    def step(self, action: str) -> Tuple[str, float, bool, Dict]:
        """Step function - same as original but with enhanced logging."""
        # The step function would be the same as the original DeepResearchEnv
        # This is just to show the concept - in practice you'd copy the full implementation
        self._step_count += 1
        self._log_info(f"--- Enhanced Model Action (a_{self._step_count-1}) ---")
        self._log_info(action)
        
        # ... rest of step implementation would go here ...
        # For brevity, returning a simple placeholder
        return "Enhanced step result", 0.0, False, {}

    def render(self, mode="human") -> str:
        """Render the environment state."""
        return self.render_cache or "Enhanced Deep Research Environment"


# Example usage
if __name__ == "__main__":
    # Demonstrate the enhanced environment
    env = EnhancedDeepResearchEnv()
    obs = env.reset()
    print("Enhanced environment initialized successfully!")
    
    # Show instruction mapping capabilities
    if env.instruction_mapping:
        print(f"Loaded {len(env.instruction_mapping)} instructions from criticsearch package")
        
        # Example: Get instruction for a political topic
        political_instruction = env.get_instruction_for_topic("election")
        if political_instruction:
            print(f"Found political instruction: {political_instruction[:100]}...")
    else:
        print("No instruction mapping loaded - falling back to default behavior") 