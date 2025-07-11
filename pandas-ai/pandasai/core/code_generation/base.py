import traceback
from typing import Any
from pandasai.agent.state import AgentState
from pandasai.core.prompts.base import BasePrompt

from .code_cleaning import CodeCleaner
from .code_validation import CodeRequirementValidator


class CodeGenerator:
    def __init__(self, context: AgentState):
        self._context = context
        self._code_cleaner = CodeCleaner(self._context)
        self._code_validator = CodeRequirementValidator(self._context)

    async def generate_code(self, prompt: BasePrompt) -> str:
        """
        Generates code using a given LLM and performs validation and cleaning steps.

        Args:
            context (PipelineContext): The pipeline context containing dataframes and logger.
            prompt (BasePrompt): The prompt to guide code generation.

        Returns:
            str: The final cleaned and validated code.

        Raises:
            Exception: If any step fails during the process.
        """
        code=None
        try:
            self._context.logger.log(f"Using Prompt: {prompt}")

            # Generate the code
            if self._context.code_fixing:
                code = self._context.config.correct_llm.generate_code(prompt, self._context)
            else:
                code = self._context.config.llm.generate_code(prompt, self._context)
            self._context.last_code_generated = code
            self._context.logger.log(f"Code Generated:\n{code}")
        except Exception as e:
            error_message = f"An error occurred during code generation: {e}"
            stack_trace = traceback.format_exc()

            self._context.logger.log(error_message)
            self._context.logger.log(f"Stack Trace:\n{stack_trace}")

            code=None
        return code

    def validate_and_clean_code(self, code: str) -> str:
        # Validate code requirements
        self._context.logger.log("Validating code requirements...")
        if not self._code_validator.validate(code):
            raise ValueError("Code validation failed due to unmet requirements.")
        self._context.logger.log("Code validation successful.")

        # Clean the code
        self._context.logger.log("Cleaning the generated code...")
        return self._code_cleaner.clean_code(code)
    
    def validate_and_clean_code_with_retries(self, code: str) -> str:
        """Execute the code with retry logic."""
        max_retries = 3
        attempts = 0

        while attempts <= max_retries:
            try:
                result = self.validate_and_clean_code(code)
                return result
            except Exception as e:
                attempts += 1
                if attempts > max_retries:
                    self._context.logger.log(f"Max retries reached. Error: {e}")
                    raise
                self._context.logger.log(
                    f"Retrying execution ({attempts}/{max_retries})..."
                )
                code = self._regenerate_code_after_error(code, e)    
