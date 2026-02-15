import json
from typing import List, TypedDict

from .agents.planner import planner_agent
from .agents.researcher import researcher_agent
from .utils.output_parser import get_structured_output_parser


class UserProfile(TypedDict):
    name: str
    background: str
    goals: str
    preferences: str


class OnboardingProfile(TypedDict):
    user_profile: UserProfile
    questionaire_responses: List[dict[str, str]]


def create_onboarding_agent():
    print("Creating onboarding agent...")
    result = planner_agent.invoke(
        {"messages": [{"role": "user", "content": "What is langgraph?"}]}
    )
    data = get_structured_output_parser(result)
    todo_list_json = [data]  # wrap in a 1‑element list to match your prompt format

    for item in todo_list_json:
        print(f"- Description: {item['description']}, Agent: {item['agent']}")
        if item["agent"] not in ["internet_search_agent", "search_youtube_videos"]:
            print("  [Warning] Unknown agent specified!")
        else:
            query = json.dumps(todo_list_json, indent=2)
            research_result = researcher_agent.invoke(
                {"messages": [{"role": "user", "content": query}]}
            )

            data = get_structured_output_parser(research_result)

            print("Research Result:\n", json.dumps(data, indent=2))


if __name__ == "__main__":
    create_onboarding_agent()
