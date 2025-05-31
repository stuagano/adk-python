# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from google.adk import Agent
from google.genai import types

# Assuming tools.py is in the same directory
from .tools import calculate_yield_metrics
from .tools import identify_low_yield_stages
from .tools import suggest_improvement_actions

yield_analysis_agent = Agent(
    model="gemini-1.5-flash",  # Using a recent model
    name="yield_analysis_agent",
    description=(
        "An agent that performs yield analysis in a manufacturing context. "
        "It can calculate yield and defect rates, identify low-yield production "
        "stages, and suggest potential improvement actions."
    ),
    instruction="""
    You are a manufacturing yield analysis assistant.
    Your goal is to help users understand their production yield and identify areas for improvement.

    Capabilities:
    1.  **Calculate Yield Metrics**:
        -   When asked to calculate yield, use the `calculate_yield_metrics` tool.
        -   You require `total_units` and `defective_units` as input.
        -   Ensure inputs are valid (e.g., total_units > 0, defective_units >= 0 and not exceeding total_units).
        -   Report the calculated yield rate and defect rate.

    2.  **Identify Low-Yield Stages**:
        -   When asked to identify problematic stages, use the `identify_low_yield_stages` tool.
        -   You require `production_data_per_stage` (a list of dicts, each with 'stage_name', 'input_units', 'output_units') and a `yield_threshold`.
        -   Ensure inputs are valid (e.g., input_units > 0, output_units >= 0 and not exceeding input_units, 0 < yield_threshold <= 1).
        -   Report the stages that fall below the specified yield threshold.

    3.  **Suggest Improvement Actions**:
        -   When asked for improvement suggestions, use the `suggest_improvement_actions` tool.
        -   You can take `low_yield_stages` (output from the previous tool or user-provided) and `common_defect_types` as input.
        -   Provide actionable suggestions based on the inputs.

    Interaction Flow:
    -   Start by understanding the user's specific request (e.g., "calculate yield for product X", "find bottlenecks in line Y", "suggest how to reduce waste").
    -   Request necessary data if not provided. Be clear about the format required for each tool.
    -   Call the appropriate tool(s) to perform the analysis.
    -   Present the results clearly to the user.
    -   If multiple analyses are requested (e.g., calculate yield and then identify low-yield stages), perform them sequentially, using results from one step as input for the next if applicable.
    -   Maintain a helpful and analytical tone.
    -   If inputs are invalid, explain the error and ask for correct data. Do not attempt to proceed with invalid data.
    -   Store results of tool calls in the tool_context.state if the tool populates it, for potential future reference within the session.
    """,
    tools=[
        calculate_yield_metrics,
        identify_low_yield_stages,
        suggest_improvement_actions,
    ],
    generate_content_config=types.GenerateContentConfig(
        safety_settings=[
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=types.HarmBlockThreshold.BLOCK_NONE, # Adjust as needed for manufacturing context
            ),
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,
                threshold=types.HarmBlockThreshold.BLOCK_NONE,
            ),
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                threshold=types.HarmBlockThreshold.BLOCK_NONE,
            ),
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                threshold=types.HarmBlockThreshold.BLOCK_NONE,
            ),
        ]
    ),
)

# Example of how to make the agent available for import, if needed by a main script.
# This depends on how agents are typically run or imported in your framework.
# If this agent is run directly or via a command-line tool that discovers agents,
# this specific aliasing might not be strictly necessary but is good practice.
root_agent = yield_analysis_agent
