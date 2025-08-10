from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel

# -------- Structured output --------
class Weather(BaseModel):
    location: str
    temperature_c: float
    condition: str

class ActionPlan(BaseModel):
    title: str = Field(..., description="One-line summary")
    steps: List[str] = Field(..., description="Actionable steps")
    effort_hours: float = Field(..., ge=0, description="Estimated effort in hours")
    weather: Optional[Weather] = None

# -------- Dependencies --------
class Deps(BaseModel):
    default_city: str = "Bengaluru"

# -------- Agent (uses output_type) --------
agent: Agent[Deps, ActionPlan] = Agent(
    model=OpenAIModel("gpt-4o"),
    deps_type=Deps,
    output_type=ActionPlan,  # structured output contract
    system_prompt=(
        "You are a precise, delivery-focused assistant."
        "Use tools when helpful and ensure the final output strictly matches ActionPlan."
    ),
)

# -------- Tools (function calling) --------
@agent.tool
def get_weather(ctx: RunContext[Deps], city: Optional[str] = None) -> Weather:
    _city = city or ctx.deps.default_city
    return Weather(location=_city, temperature_c=24.5, condition="Partly Cloudy")

@agent.tool
def estimate_effort(ctx: RunContext[Deps], tasks: List[str]) -> float:
    return sum(1.0 if len(t) > 60 else 0.5 for t in tasks)

# -------- Orchestration --------
def run(user_prompt: str) -> ActionPlan:
    result = agent.run_sync(user_prompt, deps=Deps())  # <-- add deps
    return result.output

if __name__ == "__main__":
    plan = run("Plan a 3-step economic policy for India. Include weather and effort estimate.")
    print(plan.model_dump_json(indent=2))