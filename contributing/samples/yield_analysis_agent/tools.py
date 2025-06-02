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
import pandas as pd
import io
import numpy as np
import uuid # Add this import for generating unique IDs
import json # For knowledge base
from collections import defaultdict # For failure patterns

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

    if tool_context and 'calculations' not in tool_context.state:
        tool_context.state['calculations'] = []
    if tool_context:
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

    if tool_context and 'low_yield_analysis' not in tool_context.state:
        tool_context.state['low_yield_analysis'] = []
    if tool_context:
        tool_context.state['low_yield_analysis'].append({
            "yield_threshold": yield_threshold,
            "identified_low_yield_stages": low_yield_stages
        })

    return {"low_yield_stages": low_yield_stages}

def suggest_improvement_actions(
    low_yield_stages: list[dict] = None,
    common_defect_types: list[str] = None,
    spc_out_of_control_points: list[dict] = None, # New: e.g., [{"index": 5, "value": 15.0, "metric_name": "defect_count"}]
    rca_summary: str = None, # New: e.g., "Root cause identified: Machine calibration drift for component X."
    tool_context: ToolContext = None
) -> dict:
    """Suggests potential improvement actions based on various analyses.

    Args:
        low_yield_stages: List of dictionaries representing low-yield stages.
        common_defect_types: List of strings describing common defect types.
        spc_out_of_control_points: List of out-of-control points from SPC analysis.
        rca_summary: A summary string from a Root Cause Analysis.
        tool_context: The context for the tool.

    Returns:
        A dictionary containing a list of suggested actions.
    """
    suggestions = []
    if low_yield_stages is None: low_yield_stages = []
    if common_defect_types is None: common_defect_types = []
    if spc_out_of_control_points is None: spc_out_of_control_points = []


    if not isinstance(low_yield_stages, list):
        return {"error": "Low yield stages must be a list if provided."}
    if not isinstance(common_defect_types, list):
        return {"error": "Common defect types must be a list if provided."}
    if not isinstance(spc_out_of_control_points, list):
        return {"error": "SPC out-of-control points must be a list if provided."}
    if rca_summary is not None and not isinstance(rca_summary, str):
        return {"error": "RCA summary must be a string if provided."}

    # Existing logic for low_yield_stages and common_defect_types
    for stage in low_yield_stages:
        if not isinstance(stage, dict) or 'stage_name' not in stage:
            # Allow for flexibility if other keys like 'yield' are also expected
            return {"error": "Each low yield stage must be a dictionary with at least a 'stage_name'."}
        stage_info = stage['stage_name']
        if 'yield' in stage:
            stage_info += f" (Yield: {stage['yield']:.2%})"
        suggestions.append(
            f"Investigate root causes and implement corrective actions for low yield at stage: {stage_info}."
        )

    for defect in common_defect_types:
        if not isinstance(defect, str):
            return {"error": "Each defect type must be a string."}
        suggestions.append(
            f"Address common defect type: Implement specific countermeasures for '{defect}'."
        )

    # New logic for SPC OOC points
    if spc_out_of_control_points:
        suggestions.append(
            "Address SPC out-of-control signals: Investigate the causes for the following out-of-control points:"
        )
        for point in spc_out_of_control_points:
            point_desc = f"- Index {point.get('index', 'N/A')}, Value {point.get('value', 'N/A')}"
            if 'metric_name' in point: # Optional: if metric name is passed
                 point_desc += f" for metric '{point['metric_name']}'"
            suggestions.append(point_desc)
        suggestions.append("Implement corrective actions to bring the process back into statistical control.")


    # New logic for RCA summary
    if rca_summary and rca_summary.strip():
        suggestions.append(
            f"Based on Root Cause Analysis: Address the findings summarized as: '{rca_summary}'. Develop and implement targeted solutions."
        )

    if not suggestions:
        suggestions.append(
            "No specific issues (low yield, defects, OOC points, or RCA summary) provided. "
            "Consider a general process review or provide more data for targeted suggestions."
        )

    if tool_context:
        if 'improvement_suggestions' not in tool_context.state:
            tool_context.state['improvement_suggestions'] = []
        # Log more comprehensive input that led to these suggestions
        current_inputs = {
            "low_yield_stages_input": low_yield_stages,
            "common_defect_types_input": common_defect_types,
            "spc_ooc_points_input": spc_out_of_control_points,
            "rca_summary_input": rca_summary,
            "suggestions_provided": suggestions
        }
        tool_context.state['improvement_suggestions'].append(current_inputs)

    return {"suggested_actions": suggestions}

def read_csv_data(
    file_path: str,
    total_units_col: str = None,
    defective_units_col: str = None,
    input_units_col: str = None,
    output_units_col: str = None,
    stage_name_col: str = None,
    tool_context: ToolContext = None
) -> dict:
    """Reads production data from a CSV file.

    The CSV can be used for overall yield (total_units_col, defective_units_col)
    or for stage-wise yield (stage_name_col, input_units_col, output_units_col).

    Args:
        file_path: Path to the CSV file accessible by the agent.
        total_units_col: Name of the column for total units (for overall yield).
        defective_units_col: Name of the column for defective units (for overall yield).
        input_units_col: Name of the column for input units (for stage-wise yield).
        output_units_col: Name of the column for output units (for stage-wise yield).
        stage_name_col: Name of the column for stage names (for stage-wise yield).
        tool_context: The context for the tool.

    Returns:
        A dictionary containing the extracted data or an error message.
        For overall yield, it returns: {"total_units": X, "defective_units": Y}
        For stage-wise yield, it returns: {"production_data_per_stage": [{"stage_name": S, "input_units": I, "output_units": O}, ...]}
    """
    try:
        df = pd.read_csv(file_path)

        if tool_context and 'file_reads' not in tool_context.state:
            tool_context.state['file_reads'] = []
        if tool_context:
            tool_context.state['file_reads'].append({"file_path": file_path, "type": "csv"})

        result = {}
        if total_units_col and defective_units_col:
            if total_units_col not in df.columns or defective_units_col not in df.columns:
                return {"error": f"One or both columns ('{total_units_col}', '{defective_units_col}') not found in CSV."}
            # Assuming one row of summary data or summing up if multiple rows
            result["total_units"] = int(df[total_units_col].sum())
            result["defective_units"] = int(df[defective_units_col].sum())
        elif input_units_col and output_units_col and stage_name_col:
            if not all(col in df.columns for col in [input_units_col, output_units_col, stage_name_col]):
                return {"error": f"One or more columns ('{input_units_col}', '{output_units_col}', '{stage_name_col}') not found."}

            production_data = []
            for _, row in df.iterrows():
                production_data.append({
                    "stage_name": str(row[stage_name_col]),
                    "input_units": int(row[input_units_col]),
                    "output_units": int(row[output_units_col])
                })
            result["production_data_per_stage"] = production_data
        else:
            return {"error": "Please specify columns for either overall yield or stage-wise yield."

        return result

    except FileNotFoundError:
        return {"error": f"CSV file not found at path: {file_path}"}
    except pd.errors.EmptyDataError:
        return {"error": "CSV file is empty."}
    except Exception as e:
        return {"error": f"Error reading CSV: {str(e)}"}

def read_excel_data(
    file_path: str,
    sheet_name: str | int = 0,
    total_units_col: str = None,
    defective_units_col: str = None,
    input_units_col: str = None,
    output_units_col: str = None,
    stage_name_col: str = None,
    tool_context: ToolContext = None
) -> dict:
    """Reads production data from an Excel file.

    The Excel sheet can be used for overall yield (total_units_col, defective_units_col)
    or for stage-wise yield (stage_name_col, input_units_col, output_units_col).

    Args:
        file_path: Path to the Excel file accessible by the agent.
        sheet_name: Name or index of the sheet to read (default is the first sheet).
        total_units_col: Name of the column for total units.
        defective_units_col: Name of the column for defective units.
        input_units_col: Name of the column for input units.
        output_units_col: Name of the column for output units.
        stage_name_col: Name of the column for stage names.
        tool_context: The context for the tool.

    Returns:
        A dictionary containing the extracted data or an error message.
    """
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name)

        if tool_context and 'file_reads' not in tool_context.state:
            tool_context.state['file_reads'] = []
        if tool_context:
            tool_context.state['file_reads'].append({"file_path": file_path, "type": "excel", "sheet": sheet_name})

        result = {}
        if total_units_col and defective_units_col:
            if total_units_col not in df.columns or defective_units_col not in df.columns:
                return {"error": f"One or both columns ('{total_units_col}', '{defective_units_col}') not found in Excel sheet."}
            result["total_units"] = int(df[total_units_col].sum())
            result["defective_units"] = int(df[defective_units_col].sum())
        elif input_units_col and output_units_col and stage_name_col:
            if not all(col in df.columns for col in [input_units_col, output_units_col, stage_name_col]):
                return {"error": f"One or more columns ('{input_units_col}', '{output_units_col}', '{stage_name_col}') not found."}

            production_data = []
            for _, row in df.iterrows():
                production_data.append({
                    "stage_name": str(row[stage_name_col]),
                    "input_units": int(row[input_units_col]),
                    "output_units": int(row[output_units_col])
                })
            result["production_data_per_stage"] = production_data
        else:
            return {"error": "Please specify columns for either overall yield or stage-wise yield."

        return result

    except FileNotFoundError:
        return {"error": f"Excel file not found at path: {file_path}"}
    except pd.errors.EmptyDataError:
        return {"error": "Excel sheet is empty."}
    except Exception as e: # Could be bad sheet name, etc.
        return {"error": f"Error reading Excel: {str(e)}"}

def calculate_spc_metrics_and_limits(
    data_points: list[float | int],
    control_limit_sigma: float = 3.0,
    tool_context: ToolContext = None
) -> dict:
    """Calculates SPC metrics (mean, std dev) and control limits for a given dataset.

    Args:
        data_points: A list of numerical data points (e.g., defect counts, measurements).
        control_limit_sigma: The number of standard deviations to use for control limits (default is 3.0).
        tool_context: The context for the tool.

    Returns:
        A dictionary containing:
        - mean: The average of the data points.
        - std_dev: The standard deviation of the data points.
        - upper_control_limit (UCL): Mean + (control_limit_sigma * std_dev).
        - lower_control_limit (LCL): Mean - (control_limit_sigma * std_dev), cannot be less than 0 for count data.
        - control_limit_sigma: The sigma value used.
        Or an error message if data is insufficient.
    """
    if not isinstance(data_points, list) or len(data_points) < 2:
        return {"error": "Insufficient data points. At least 2 data points are required."}
    if not all(isinstance(x, (int, float)) for x in data_points):
        return {"error": "All data points must be numerical (int or float)."}
    if control_limit_sigma <= 0:
        return {"error": "Control limit sigma must be a positive value."}

    np_data = np.array(data_points)
    mean = np.mean(np_data)
    std_dev = np.std(np_data)

    # Ensure LCL is not negative if data points suggest counts or positive measurements
    # A more sophisticated check might involve parameterizing this behavior.
    # For now, if all data points are >=0, LCL won't go below 0.
    is_non_negative_data = all(x >= 0 for x in data_points)

    ucl = mean + (control_limit_sigma * std_dev)
    lcl = mean - (control_limit_sigma * std_dev)

    if is_non_negative_data and lcl < 0:
        lcl = 0.0

    results = {
        "mean": float(mean),
        "std_dev": float(std_dev),
        "upper_control_limit": float(ucl),
        "lower_control_limit": float(lcl),
        "control_limit_sigma": control_limit_sigma,
        "data_points_analyzed": len(data_points)
    }

    if tool_context:
        if 'spc_analysis' not in tool_context.state:
            tool_context.state['spc_analysis'] = []
        tool_context.state['spc_analysis'].append(results)

    return results

def identify_out_of_control_points(
    data_points: list[float | int],
    upper_control_limit: float,
    lower_control_limit: float,
    tool_context: ToolContext = None
) -> dict:
    """Identifies data points that fall outside the given control limits.

    Args:
        data_points: A list of numerical data points.
        upper_control_limit: The upper control limit (UCL).
        lower_control_limit: The lower control limit (LCL).
        tool_context: The context for the tool.

    Returns:
        A dictionary containing:
        - out_of_control_points: A list of dicts, each with 'index' and 'value' of the OOC point.
        - ucl_used: The UCL value used for the check.
        - lcl_used: The LCL value used for the check.
        Or an error message if inputs are invalid.
    """
    if not isinstance(data_points, list) or not data_points:
        return {"error": "Data points list cannot be empty."}
    if not all(isinstance(x, (int, float)) for x in data_points):
        return {"error": "All data points must be numerical (int or float)."}
    if not isinstance(upper_control_limit, (int, float)) or not isinstance(lower_control_limit, (int, float)):
        return {"error": "Upper and Lower control limits must be numerical."}
    if lower_control_limit > upper_control_limit:
        return {"error": "Lower control limit cannot be greater than Upper control limit."}

    ooc_points = []
    for i, value in enumerate(data_points):
        if value > upper_control_limit or value < lower_control_limit:
            ooc_points.append({"index": i, "value": float(value)})

    results = {
        "out_of_control_points": ooc_points,
        "ucl_used": upper_control_limit,
        "lcl_used": lower_control_limit,
        "data_points_checked": len(data_points)
    }

    if tool_context:
        if 'spc_ooc_checks' not in tool_context.state:
            tool_context.state['spc_ooc_checks'] = []
        tool_context.state['spc_ooc_checks'].append(results)

    return results

def guide_root_cause_analysis_5whys(
    problem_statement: str,
    previous_whys: list[dict] = None, # Each dict: {"why_question": "...", "user_answer": "..."}
    tool_context: ToolContext = None
) -> dict:
    """Guides the user through a 5 Whys root cause analysis.

    This tool helps structure the 5 Whys process. The agent uses this tool
    to ask the next 'Why?' question or suggest conclusion.

    Args:
        problem_statement: The initial problem to analyze.
        previous_whys: A list of previous 'why' questions and user answers.
        tool_context: The context for the tool.

    Returns:
        A dictionary containing:
        - next_prompt_for_user: The next question to ask the user (e.g., "Why did '{last_answer}' occur?").
        - current_depth: The current number of 'Whys' asked.
        - analysis_summary: A summary of the
        Or, if depth is 5 or user indicates root cause found (logic to be handled by agent):
        - conclusion_prompt: A suggestion to conclude or summarize.
    """
    if not isinstance(problem_statement, str) or not problem_statement.strip():
        return {"error": "Problem statement cannot be empty."}

    current_depth = len(previous_whys) if previous_whys else 0
    analysis_path = [f"Initial Problem: {problem_statement}"]

    if previous_whys:
        for i, item in enumerate(previous_whys):
            analysis_path.append(f"{i+1}. Q: {item['why_question']} A: {item['user_answer']}")

    if tool_context:
        if 'rca_sessions' not in tool_context.state:
            tool_context.state['rca_sessions'] = []
        # Log current state of this RCA
        rca_log_entry = {
            "problem": problem_statement,
            "path": analysis_path,
            "depth": current_depth
        }
        # Avoid appending duplicates if called multiple times for the same RCA state
        # This simplistic check might need refinement for more robust state tracking
        if not any(s == rca_log_entry for s in tool_context.state['rca_sessions']):
             tool_context.state['rca_sessions'].append(rca_log_entry)


    if current_depth >= 5:
        return {
            "conclusion_prompt": "We have reached 5 'Whys'. Do you feel we have identified a potential root cause, or would you like to delve deeper?",
            "current_depth": current_depth,
            "analysis_summary": "\n".join(analysis_path)
        }

    last_answer = problem_statement
    if previous_whys:
        last_answer = previous_whys[-1]["user_answer"]
        if not isinstance(last_answer, str) or not last_answer.strip():
            return {"error": f"The answer to 'Why #{current_depth}' was empty. Please provide a valid answer."}


    next_question = f"Why did '{last_answer}' occur?"
    if current_depth == 0 and problem_statement:
        next_question = f"Why is '{problem_statement}' happening?"


    return {
        "next_prompt_for_user": next_question,
        "current_depth": current_depth + 1, # Next depth will be current_depth + 1
        "analysis_summary": "\n".join(analysis_path)
    }

def add_action_item(
    description: str,
    owner: str = None, # Optional: name or team responsible
    status: str = "open", # Default status
    tool_context: ToolContext = None
) -> dict:
    """Adds a new action item to the session's action list.

    Args:
        description: A clear description of the action item.
        owner: Optional. The person or team responsible for the action.
        status: Optional. The initial status of the action (e.g., "open", "in-progress").
        tool_context: The context for the tool.

    Returns:
        A dictionary containing the newly added action item with its ID,
        or an error message.
    """
    if not isinstance(description, str) or not description.strip():
        return {"error": "Action item description cannot be empty."}
    if owner is not None and not isinstance(owner, str):
        return {"error": "Owner must be a string if provided."}
    if not isinstance(status, str) or not status.strip():
        return {"error": "Status must be a non-empty string."}

    action_id = str(uuid.uuid4()) # Generate a unique ID for the action item
    action_item = {
        "id": action_id,
        "description": description,
        "owner": owner,
        "status": status,
        "created_at": pd.Timestamp.now().isoformat() # Optional: timestamp
    }

    if tool_context:
        if 'action_items' not in tool_context.state:
            tool_context.state['action_items'] = []
        tool_context.state['action_items'].append(action_item)
        return {"success": True, "action_item_added": action_item}
    else:
        # This case should ideally not happen if tool_context is always passed by the agent
        return {"error": "Tool context not available. Cannot save action item."}

def list_action_items(
    status_filter: str = None, # Optional: e.g., "open", "in-progress"
    owner_filter: str = None,  # Optional: filter by owner
    tool_context: ToolContext = None
) -> dict:
    """Lists action items from the session, with optional filters.

    Args:
        status_filter: Optional. Filter actions by this status.
        owner_filter: Optional. Filter actions by this owner.
        tool_context: The context for the tool.

    Returns:
        A dictionary containing a list of action items, or an error message.
    """
    if tool_context and 'action_items' in tool_context.state:
        actions = tool_context.state['action_items']

        if status_filter:
            if not isinstance(status_filter, str):
                return {"error": "Status filter must be a string."}
            actions = [a for a in actions if a.get('status', '').lower() == status_filter.lower()]

        if owner_filter:
            if not isinstance(owner_filter, str):
                return {"error": "Owner filter must be a string."}
            actions = [a for a in actions if a.get('owner', '').lower() == owner_filter.lower()]

        return {"action_items": actions}
    return {"action_items": []} # Return empty list if no actions or no context

def update_action_item_status(
    action_id: str,
    new_status: str,
    tool_context: ToolContext = None
) -> dict:
    """Updates the status of an existing action item.

    Args:
        action_id: The unique ID of the action item to update.
        new_status: The new status for the action item (e.g., "in-progress", "completed", "cancelled").
        tool_context: The context for the tool.

    Returns:
        A dictionary indicating success or failure, and the updated item if successful.
    """
    if not isinstance(action_id, str) or not action_id.strip():
        return {"error": "Action ID must be a non-empty string."}
    if not isinstance(new_status, str) or not new_status.strip():
        return {"error": "New status must be a non-empty string."}

    if tool_context and 'action_items' in tool_context.state:
        actions = tool_context.state['action_items']
        for item in actions:
            if item.get('id') == action_id:
                item['status'] = new_status
                item['updated_at'] = pd.Timestamp.now().isoformat() # Optional: timestamp
                # No need to save back to tool_context.state['action_items'] as 'item' is a reference to an element within that list.
                return {"success": True, "updated_action_item": item}
        return {"error": f"Action item with ID '{action_id}' not found."}

    return {"error": "No action items found in context or context unavailable."}

def query_knowledge_base(
    search_keywords: list[str],
    tool_context: ToolContext = None
) -> dict:
    """Queries a simple knowledge base for problems, causes, and solutions.

    Args:
        search_keywords: A list of keywords to search for in the knowledge base.
        tool_context: The context for the tool.

    Returns:
        A dictionary containing a list of matching entries from the knowledge base
        or an error message.
    """
    if not isinstance(search_keywords, list) or not search_keywords:
        return {"error": "Search keywords list cannot be empty."}
    if not all(isinstance(kw, str) for kw in search_keywords):
        return {"error": "All search keywords must be strings."}

    # In a real scenario, this path might be configurable or more robust.
    kb_file_path = "contributing/samples/yield_analysis_agent/knowledge_base.json"

    try:
        with open(kb_file_path, 'r') as f:
            knowledge_base_data = json.load(f)
    except FileNotFoundError:
        return {"error": f"Knowledge base file not found at {kb_file_path}."}
    except json.JSONDecodeError:
        return {"error": f"Error decoding JSON from knowledge base file {kb_file_path}."}
    except Exception as e:
        return {"error": f"An unexpected error occurred while reading the knowledge base: {str(e)}"}

    matching_entries = []
    search_keywords_lower = [kw.lower() for kw in search_keywords]

    for entry in knowledge_base_data:
        # Check if any search keyword is in the entry's keywords or problem summary
        entry_text_corpus = " ".join(entry.get("keywords", [])).lower() +                             " " + entry.get("problem_summary", "").lower()

        if any(kw_lower in entry_text_corpus for kw_lower in search_keywords_lower):
            matching_entries.append(entry)
            continue # Go to next entry if already matched

        # Optionally, extend search to possible_causes and suggested_solutions
        # For now, keeping it simpler by focusing on keywords and summary.

    if tool_context:
        if 'kb_queries' not in tool_context.state:
            tool_context.state['kb_queries'] = []
        tool_context.state['kb_queries'].append({
            "keywords_used": search_keywords,
            "matches_found": len(matching_entries)
        })

    if not matching_entries:
        return {"message": "No matching entries found in the knowledge base for the given keywords.", "results": []}

    return {"results": matching_entries}

def detect_simple_anomalies(
    data_points: list[float | int],
    window_size: int = 5, # For rolling calculations
    std_dev_threshold: float = 2.0, # Number of std devs to consider an anomaly
    absolute_upper_threshold: float = None, # Optional absolute upper limit
    absolute_lower_threshold: float = None, # Optional absolute lower limit
    tool_context: ToolContext = None
) -> dict:
    """Detects simple anomalies in a list of numerical data points.

    Anomalies can be identified based on deviation from a rolling mean
    by a certain number of standard deviations, or by exceeding absolute thresholds.

    Args:
        data_points: A list of numerical data points (time-series).
        window_size: The window size for calculating rolling mean and std dev. Min 2.
        std_dev_threshold: Number of standard deviations from the rolling mean
                           to classify a point as an anomaly.
        absolute_upper_threshold: Optional. If a point exceeds this, it's an anomaly.
        absolute_lower_threshold: Optional. If a point is below this, it's an anomaly.
        tool_context: The context for the tool.

    Returns:
        A dictionary containing:
        - anomalies: A list of dicts, each with 'index', 'value', and 'reason' for the anomaly.
        - parameters_used: A dict of the parameters used for detection.
        Or an error message if inputs are invalid.
    """
    if not isinstance(data_points, list) or len(data_points) < window_size :
        return {"error": f"Insufficient data points. At least {window_size} data points are required for window size {window_size}."}
    if not all(isinstance(x, (int, float)) for x in data_points):
        return {"error": "All data points must be numerical (int or float)."}
    if not isinstance(window_size, int) or window_size < 2:
        return {"error": "Window size must be an integer of at least 2."}
    if not isinstance(std_dev_threshold, (int,float)) or std_dev_threshold <= 0:
        return {"error": "Standard deviation threshold must be a positive number."}
    if absolute_upper_threshold is not None and not isinstance(absolute_upper_threshold, (int,float)):
        return {"error": "Absolute upper threshold must be a number if provided."}
    if absolute_lower_threshold is not None and not isinstance(absolute_lower_threshold, (int,float)):
         return {"error": "Absolute lower threshold must be a number if provided."}
    if absolute_upper_threshold is not None and absolute_lower_threshold is not None and absolute_lower_threshold >= absolute_upper_threshold:
        return {"error": "Absolute lower threshold cannot be greater than or equal to absolute upper threshold."}


    anomalies = []
    series = pd.Series(data_points)
    rolling_mean = series.rolling(window=window_size, center=True).mean()
    rolling_std = series.rolling(window=window_size, center=True).std()

    # Pad rolling calculations for edges if center=True is used, or handle NaN
    # For simplicity, we'll start comparing where rolling values are available
    # More sophisticated padding (e.g. expanding window) could be used.

    for i in range(len(data_points)):
        point_value = data_points[i]
        reason = []

        # Check absolute thresholds first
        if absolute_upper_threshold is not None and point_value > absolute_upper_threshold:
            reason.append(f"Exceeded absolute upper threshold ({absolute_upper_threshold})")
        if absolute_lower_threshold is not None and point_value < absolute_lower_threshold:
            reason.append(f"Below absolute lower threshold ({absolute_lower_threshold})")

        # Check rolling std dev based anomaly if no absolute breach or to add info
        # Only check if rolling_mean and rolling_std are not NaN for that point
        if pd.notna(rolling_mean[i]) and pd.notna(rolling_std[i]):
            upper_bound = rolling_mean[i] + (std_dev_threshold * rolling_std[i])
            lower_bound = rolling_mean[i] - (std_dev_threshold * rolling_std[i])

            if point_value > upper_bound:
                reason.append(f"Exceeded rolling upper bound ({upper_bound:.2f}, mean: {rolling_mean[i]:.2f}, std: {rolling_std[i]:.2f})")
            elif point_value < lower_bound:
                reason.append(f"Below rolling lower bound ({lower_bound:.2f}, mean: {rolling_mean[i]:.2f}, std: {rolling_std[i]:.2f})")

        if reason:
            anomalies.append({"index": i, "value": float(point_value), "reason": "; ".join(reason)})

    parameters_used = {
        "window_size": window_size,
        "std_dev_threshold": std_dev_threshold,
        "absolute_upper_threshold": absolute_upper_threshold,
        "absolute_lower_threshold": absolute_lower_threshold,
        "data_points_analyzed": len(data_points)
    }

    if tool_context:
        if 'anomaly_detection_runs' not in tool_context.state:
            tool_context.state['anomaly_detection_runs'] = []
        tool_context.state['anomaly_detection_runs'].append({
            "parameters": parameters_used,
            "anomalies_found_count": len(anomalies)
        })

    return {"anomalies": anomalies, "parameters_used": parameters_used}

from collections import defaultdict # Add this import

def identify_simple_failure_patterns(
    event_data: list[dict], # Expected keys: 'timestamp', 'event_type', 'item_id' (e.g., machine_id)
    maintenance_completed_event_type: str = "maintenance_completed",
    tool_context: ToolContext = None
) -> dict:
    """Identifies simple failure patterns from a list of historical events.

    Example patterns:
    - Time between 'maintenance_completed' and subsequent failures for the same item.
    - Frequency of different failure types.

    Args:
        event_data: A list of dictionaries, each representing an event.
                    Required keys: 'timestamp' (ISO format string or datetime object),
                                   'event_type' (string, e.g., "failure_A", "maintenance_completed"),
                                   'item_id' (string, e.g., machine ID or component ID).
        maintenance_completed_event_type: The event_type string that signifies completion of maintenance.
        tool_context: The context for the tool.

    Returns:
        A dictionary containing identified patterns or an error message.
    """
    if not isinstance(event_data, list) or not event_data:
        return {"error": "Event data list cannot be empty."}

    required_keys = ['timestamp', 'event_type', 'item_id']
    for i, event in enumerate(event_data):
        if not isinstance(event, dict) or not all(key in event for key in required_keys):
            return {"error": f"Event at index {i} is missing one or more required keys: {required_keys}."}
        try:
            # Ensure timestamp is a pandas Timestamp for easier manipulation
            event['timestamp'] = pd.to_datetime(event['timestamp'])
        except Exception as e:
            return {"error": f"Invalid timestamp format for event at index {i}: {event.get('timestamp')}. Error: {e}"}

    # Sort events by item_id and then by timestamp
    try:
        event_data.sort(key=lambda x: (x['item_id'], x['timestamp']))
    except Exception as e: # Catch potential issues if item_id is not comparable, though strings should be.
        return {"error": f"Could not sort event data. Ensure item_ids are consistent. Error: {e}"}

    patterns = {
        "failure_type_counts": defaultdict(int),
        "time_to_failure_after_maintenance": defaultdict(list), # item_id -> list of timedelta in hours
        "notes": []
    }

    last_maintenance_time = {} # item_id -> timestamp of last maintenance

    for event in event_data:
        item_id = event['item_id']
        event_type = event['event_type']
        timestamp = event['timestamp']

        # Count all event types that are not maintenance_completed as potential failures for frequency
        if event_type != maintenance_completed_event_type:
            patterns["failure_type_counts"][f"{item_id}::{event_type}"] += 1


        if event_type == maintenance_completed_event_type:
            last_maintenance_time[item_id] = timestamp
        # If it's a failure event and there was a prior maintenance for this item
        elif event_type != maintenance_completed_event_type and item_id in last_maintenance_time:
            time_since_maintenance = timestamp - last_maintenance_time[item_id]
            # Convert timedelta to hours for easier interpretation
            hours_since_maintenance = time_since_maintenance.total_seconds() / 3600.0
            patterns["time_to_failure_after_maintenance"][f"{item_id}::{event_type}"].append(round(hours_since_maintenance, 2))
            # Remove last_maintenance_time for this item_id to ensure next failure is after next maintenance
            # Or, if we want to see all failures after last maintenance, then don't delete.
            # For "time *between* maintenance and next failure", deleting is appropriate.
            del last_maintenance_time[item_id]


    # Consolidate results for output
    # Calculate average time to failure if data exists
    avg_ttf_after_maintenance = {}
    for key, times in patterns["time_to_failure_after_maintenance"].items():
        if times:
            avg_ttf_after_maintenance[key] = {"average_hours": round(np.mean(times),2), "count": len(times), "all_hours": times}

    # Make failure_type_counts a regular dict for JSON serialization
    patterns["failure_type_counts"] = dict(patterns["failure_type_counts"])
    patterns["time_to_failure_after_maintenance_summary"] = avg_ttf_after_maintenance
    del patterns["time_to_failure_after_maintenance"] # Remove raw list to simplify output

    if not patterns["failure_type_counts"] and not patterns["time_to_failure_after_maintenance_summary"]:
        patterns["notes"].append("No significant failure patterns identified with the provided data and logic.")
        patterns["notes"].append(f"Ensure '{maintenance_completed_event_type}' event type is correctly specified and present for TtF calculations.")


    if tool_context:
        if 'failure_pattern_runs' not in tool_context.state:
            tool_context.state['failure_pattern_runs'] = []
        tool_context.state['failure_pattern_runs'].append({
            "maintenance_event_type_used": maintenance_completed_event_type,
            "events_analyzed_count": len(event_data),
            "failure_types_found": len(patterns["failure_type_counts"]),
            "ttf_calculations_count": len(patterns["time_to_failure_after_maintenance_summary"])
        })

    return {"identified_patterns": patterns}
