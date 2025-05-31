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

from google.adk.tools.tool_context import ToolContext

def calculate_yield_metrics(
    total_units: int, defective_units: int, tool_context: ToolContext
) -> dict:
    """Calculates yield and defect rates from production data.

    Args:
        total_units: The total number of units produced.
        defective_units: The number of defective units.
        tool_context: The context for the tool.

    Returns:
        A dictionary containing the yield rate and defect rate.
        Returns an error message if total_units is zero.
    """
    if total_units <= 0:
        return {"error": "Total units must be a positive number."}
    if defective_units < 0:
        return {"error": "Defective units cannot be negative."}
    if defective_units > total_units:
        return {"error": "Defective units cannot exceed total units."}

    yield_rate = (total_units - defective_units) / total_units
    defect_rate = defective_units / total_units

    if 'calculations' not in tool_context.state:
        tool_context.state['calculations'] = []
    tool_context.state['calculations'].append({
        "total_units": total_units,
        "defective_units": defective_units,
        "yield_rate": yield_rate,
        "defect_rate": defect_rate
    })

    return {
        "yield_rate": yield_rate,
        "defect_rate": defect_rate,
    }

def identify_low_yield_stages(
    production_data_per_stage: list[dict], yield_threshold: float, tool_context: ToolContext
) -> dict:
    """Identifies production stages with yield below a given threshold.

    Args:
        production_data_per_stage: A list of dictionaries, where each dictionary
                                   represents a stage and contains 'stage_name',
                                   'input_units', and 'output_units'.
        yield_threshold: The minimum yield rate considered acceptable.
        tool_context: The context for the tool.

    Returns:
        A dictionary containing a list of low-yield stages.
        Each item in the list includes the stage name and its calculated yield.
        Returns an error message if input data is invalid.
    """
    low_yield_stages = []
    if not isinstance(production_data_per_stage, list):
        return {"error": "Production data per stage must be a list of dictionaries."}
    if not (0 < yield_threshold <= 1):
        return {"error": "Yield threshold must be between 0 (exclusive) and 1 (inclusive)."}

    for stage_data in production_data_per_stage:
        if not all(key in stage_data for key in ['stage_name', 'input_units', 'output_units']):
            return {"error": "Each stage must have 'stage_name', 'input_units', and 'output_units'."}
        if not isinstance(stage_data['input_units'], int) or not isinstance(stage_data['output_units'], int):
            return {"error": "Input and output units must be integers."}
        if stage_data['input_units'] <= 0:
            return {"error": f"Input units for stage {stage_data['stage_name']} must be positive."}
        if stage_data['output_units'] < 0:
            return {"error": f"Output units for stage {stage_data['stage_name']} cannot be negative."}
        if stage_data['output_units'] > stage_data['input_units']:
            return {"error": f"Output units cannot exceed input units for stage {stage_data['stage_name']}."}

        stage_yield = stage_data['output_units'] / stage_data['input_units']
        if stage_yield < yield_threshold:
            low_yield_stages.append({
                "stage_name": stage_data['stage_name'],
                "yield": stage_yield,
                "input_units": stage_data['input_units'],
                "output_units": stage_data['output_units'],
            })

    if 'low_yield_analysis' not in tool_context.state:
        tool_context.state['low_yield_analysis'] = []
    tool_context.state['low_yield_analysis'].append({
        "yield_threshold": yield_threshold,
        "identified_low_yield_stages": low_yield_stages
    })

    return {"low_yield_stages": low_yield_stages}

def suggest_improvement_actions(
    low_yield_stages: list[dict], common_defect_types: list[str], tool_context: ToolContext
) -> dict:
    """Suggests potential improvement actions based on low-yield stages and defect types.

    Args:
        low_yield_stages: A list of dictionaries representing low-yield stages,
                          including 'stage_name' and 'yield'.
        common_defect_types: A list of strings describing common defect types.
        tool_context: The context for the tool.

    Returns:
        A dictionary containing a list of suggested actions.
    """
    suggestions = []
    if not isinstance(low_yield_stages, list):
        return {"error": "Low yield stages must be a list."}
    if not isinstance(common_defect_types, list):
        return {"error": "Common defect types must be a list."}

    for stage in low_yield_stages:
        if not isinstance(stage, dict) or 'stage_name' not in stage:
            return {"error": "Each low yield stage must be a dictionary with a 'stage_name'."}
        suggestions.append(
            f"Investigate root causes for low yield at stage: {stage['stage_name']}."
        )

    for defect in common_defect_types:
        if not isinstance(defect, str):
            return {"error": "Each defect type must be a string."}
        suggestions.append(
            f"Implement corrective actions for defect type: {defect}."
        )

    if not low_yield_stages and not common_defect_types:
        suggestions.append(
            "No specific low-yield stages or defect types provided. "
            "Consider a general process review for potential improvements."
        )
    elif not low_yield_stages:
        suggestions.append(
            "No specific low-yield stages provided. "
            "Focus on addressing the listed common defect types."
        )
    elif not common_defect_types:
        suggestions.append(
            "No common defect types provided. "
            "Focus on investigating the identified low-yield stages."
        )

    if 'improvement_suggestions' not in tool_context.state:
        tool_context.state['improvement_suggestions'] = []
    tool_context.state['improvement_suggestions'].append({
        "low_yield_stages_input": low_yield_stages,
        "common_defect_types_input": common_defect_types,
        "suggestions_provided": suggestions
    })

    return {"suggested_actions": suggestions}
