from typing import Any, Dict, List, Optional, Type

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI


class PydancticLLMChain:
    def __init__(
        self,
        pydantic_model: Type,
        prompt_template: str,
        input_variables: List[Dict[str, Any]],
        model_name: str = "gpt-4o-mini",
        temperature: float = 0.7,
        api_key: Optional[str] = None,
        partial_variables: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.parser = JsonOutputParser(
            pydantic_object=pydantic_model,
        )
        self.prompt = PromptTemplate(
            template=prompt_template,
            input_variables=[var["name"] for var in input_variables],
            partial_variables=partial_variables
            or {"format_instructions": self.parser.get_format_instructions()},
        )
        self.model = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            api_key=api_key,
            max_retries=3,
        )
        self.chain = self.prompt | self.model | self.parser

    def run(self, variables: Dict[str, Any]) -> Any:
        return self.chain.invoke(variables)

    async def arun(self, variables: Dict[str, Any]) -> Any:
        return await self.chain.ainvoke(variables)
