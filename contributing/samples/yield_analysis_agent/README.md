# Yield Analysis Agent

This is an advanced agent designed to assist with comprehensive manufacturing process analysis. It helps diagnose issues, understand process performance across various metrics, identify areas for improvement, consult a knowledge base, guide root cause analysis, track corrective actions, and more.

## Features

This agent offers a wide range of analytical capabilities:

-   **Data Input**: Load data from CSV or Excel files for various analyses.
-   **Yield Calculation**: Compute overall yield and defect rates.
-   **Stage-wise Yield Analysis**: Identify production stages performing below a specified yield threshold.
-   **Statistical Process Control (SPC)**:
    -   Calculate SPC metrics (mean, standard deviation).
    -   Determine Upper and Lower Control Limits (UCL/LCL).
    -   Identify out-of-control data points.
-   **Time-Series Anomaly Detection**: Detect simple anomalies in numerical data based on rolling statistics or absolute thresholds.
-   **Failure Pattern Identification**: Analyze historical event data to find patterns like failure type frequencies and time-to-failure after maintenance.
-   **Guided Root Cause Analysis (RCA)**: Interactively guide users through the 5 Whys methodology to find root causes of problems.
-   **Knowledge Base Querying**: Search a predefined knowledge base for common problems, causes, and solutions based on keywords.
-   **Action Item Tracking**: Add, list, and update the status of action items within the current session.
-   **Enhanced Suggestion Generation**: Provide improvement suggestions based on a combination of inputs from other analyses (yield, SPC, RCA).

## Prerequisites

-   Google Agent Development Kit (ADK) installed.
-   Access to a supported LLM (e.g., Gemini 1.5 Flash).
-   Python environment where the ADK and its dependencies (including `pandas` and `numpy`) are available.

## Required Data / Inputs

The agent can work with various types of data, typically provided by the user directly or by loading from files:

-   **Overall Production Numbers**: For `calculate_yield_metrics` (e.g., total units, defective units).
-   **Stage-wise Production Data**: For `identify_low_yield_stages` (e.g., list of dictionaries with 'stage_name', 'input_units', 'output_units').
-   **Time-Series Data**: For `calculate_spc_metrics_and_limits` and `detect_simple_anomalies` (e.g., list of numerical data like defect counts per batch, sensor readings).
-   **Historical Event Logs**: For `identify_simple_failure_patterns` (e.g., list of dictionaries with 'timestamp', 'event_type', 'item_id').
-   **Problem Statements**: For `guide_root_cause_analysis_5whys`.
-   **Search Keywords**: For `query_knowledge_base`.
-   **Action Item Details**: For `add_action_item` (description, owner, status) and `update_action_item_status` (action ID, new status).

## Tools

The agent utilizes the following tools defined in `tools.py`:

1.  **`read_csv_data(...)`**
    -   **Description**: Reads data from a CSV file for various analyses.
    -   **Args**: `file_path` (str), optional column name parameters (e.g., `total_units_col`, `defective_units_col`, `stage_name_col`, `input_units_col`, `output_units_col`, a column for `data_points`, or columns for `timestamp`, `event_type`, `item_id`).
    -   **Returns**: A dictionary containing the extracted data (e.g., total/defective units, list of stage data, list of numerical data points, list of event dictionaries) or an error.

2.  **`read_excel_data(...)`**
    -   **Description**: Reads data from an Excel file sheet for various analyses.
    -   **Args**: `file_path` (str), `sheet_name` (str|int, default 0), optional column name parameters (similar to `read_csv_data`).
    -   **Returns**: A dictionary containing the extracted data or an error.

3.  **`calculate_yield_metrics(total_units: int, defective_units: int, ...)`**
    -   **Description**: Calculates overall yield and defect rates.
    -   **Args**: `total_units` (int), `defective_units` (int).
    -   **Returns**: Dictionary with `yield_rate` and `defect_rate`.

4.  **`identify_low_yield_stages(production_data_per_stage: list[dict], yield_threshold: float, ...)`**
    -   **Description**: Identifies production stages performing below a specified yield threshold.
    -   **Args**: `production_data_per_stage` (list of dicts), `yield_threshold` (float, user must specify, e.g., 0.90 for 90%).
    -   **Returns**: Dictionary with a list of `low_yield_stages`.

5.  **`calculate_spc_metrics_and_limits(data_points: list[float | int], control_limit_sigma: float = 3.0, ...)`**
    -   **Description**: Calculates SPC metrics (mean, std dev) and control limits.
    -   **Args**: `data_points` (list of numbers), `control_limit_sigma` (float, defaults to 3.0; agent should ask user for preference).
    -   **Returns**: Dictionary with `mean`, `std_dev`, `upper_control_limit` (UCL), `lower_control_limit` (LCL).

6.  **`identify_out_of_control_points(data_points: list[float | int], upper_control_limit: float, lower_control_limit: float, ...)`**
    -   **Description**: Identifies data points outside given SPC control limits.
    -   **Args**: `data_points` (list of numbers), `upper_control_limit` (float), `lower_control_limit` (float).
    -   **Returns**: Dictionary with a list of `out_of_control_points`.

7.  **`detect_simple_anomalies(data_points: list[float | int], window_size: int = 5, std_dev_threshold: float = 2.0, ...)`**
    -   **Description**: Detects simple anomalies in time-series data.
    -   **Args**: `data_points` (list of numbers). Optional, user-configurable args: `window_size` (int, default 5), `std_dev_threshold` (float, default 2.0), `absolute_upper_threshold` (float), `absolute_lower_threshold` (float). Agent should confirm these with user.
    -   **Returns**: Dictionary with a list of `anomalies` (each with index, value, reason) and `parameters_used`.

8.  **`identify_simple_failure_patterns(event_data: list[dict], maintenance_completed_event_type: str = "maintenance_completed", ...)`**
    -   **Description**: Identifies simple failure patterns from historical event data.
    -   **Args**: `event_data` (list of dicts with 'timestamp', 'event_type', 'item_id'), `maintenance_completed_event_type` (str, defaults to "maintenance_completed"; agent should ask user if their term is different).
    -   **Returns**: Dictionary with `identified_patterns` (e.g., failure type counts, time-to-failure summaries).

9.  **`guide_root_cause_analysis_5whys(problem_statement: str, previous_whys: list[dict] = None, ...)`**
    -   **Description**: Interactively guides a 5 Whys root cause analysis.
    -   **Args**: `problem_statement` (str), `previous_whys` (list of dicts, managed by agent during conversation).
    -   **Returns**: Dictionary with `next_prompt_for_user` or `conclusion_prompt`, `current_depth`, and `analysis_summary`.

10. **`query_knowledge_base(search_keywords: list[str], ...)`**
    -   **Description**: Queries a local JSON knowledge base for common problems, causes, and solutions.
    -   **Args**: `search_keywords` (list of strings).
    -   **Returns**: Dictionary with a list of `results` (matching entries).
    -   **Note**: The knowledge base is stored in `contributing/samples/yield_analysis_agent/knowledge_base.json` and can be customized by users.

11. **`suggest_improvement_actions(...)`**
    -   **Description**: Suggests potential improvement actions based on various analyses.
    -   **Args (all optional)**: `low_yield_stages` (list), `common_defect_types` (list), `spc_out_of_control_points` (list), `rca_summary` (str).
    -   **Returns**: Dictionary with a list of `suggested_actions`.

12. **`add_action_item(description: str, owner: str = None, status: str = "open", ...)`**
    -   **Description**: Adds a new action item to a session-based list.
    -   **Args**: `description` (str), `owner` (str, optional), `status` (str, default "open").
    -   **Returns**: Dictionary with the `action_item_added` (including its unique ID).

13. **`list_action_items(status_filter: str = None, owner_filter: str = None, ...)`**
    -   **Description**: Lists action items from the current session, with optional filters.
    -   **Args**: `status_filter` (str, optional), `owner_filter` (str, optional).
    -   **Returns**: Dictionary with a list of `action_items`.

14. **`update_action_item_status(action_id: str, new_status: str, ...)`**
    -   **Description**: Updates the status of an existing action item.
    -   **Args**: `action_id` (str), `new_status` (str).
    -   **Returns**: Dictionary indicating `success` and the `updated_action_item`.

## How to Run the Agent

This agent is designed to be run within the Google ADK framework. Use the ADK CLI or a custom script to serve and interact with the agent. The agent will guide you on required inputs for each capability.

**Example Interaction Flow (Conceptual):**

1.  **User**: "I want to analyze yield data from `production_log.csv`."
    -   **Agent**: "Okay, I can help with that. To read the CSV, I'll need the column names. For example, what's the column name for total units produced, and what's the column for defective units?"
    -   *(User provides column names)*
    -   **Agent (calls `read_csv_data`, then `calculate_yield_metrics`)**: "Thanks! Based on the data, the overall yield is 92.7%..."
2.  **User**: "That seems low. Can we find out why?"
    -   **Agent**: "We could perform a Root Cause Analysis using the 5 Whys method. Would you like to start with the problem 'Overall yield is 92.7%'?"
    -   *(User agrees, agent proceeds with `guide_root_cause_analysis_5whys` over several turns)*
3.  **Agent (after RCA)**: "...The RCA summary suggests a key cause is 'material inconsistency from supplier X'. I can also query our knowledge base for 'supplier material inconsistency'. Want to try that?"
    -   *(User agrees, agent calls `query_knowledge_base`)*
4.  **Agent**: "I found an entry suggesting 'Implement stricter incoming material inspection' and 'Work with supplier on quality control'. Based on this and our RCA, I can suggest some improvement actions. Ready?"
    -   *(User agrees, agent calls `suggest_improvement_actions` with RCA summary)*
5.  **Agent**: "Here are some suggestions: 1. Implement stricter incoming material inspection for Supplier X. 2. Schedule a meeting with Supplier X to discuss quality control. Would you like to add these as action items to track?"
    -   *(User agrees, agent calls `add_action_item` for each)*

## Agent Configuration

-   **Model**: `gemini-1.5-flash` (configurable in `agent.py`).
-   **Tools**: All tools are defined in `tools.py`.
-   **Instructions**: The agent's detailed behavior, including its persona, how it uses tools, how it handles parameters, and its interaction flow, is defined in the `instruction` parameter within `agent.py`.
-   **Knowledge Base**: A simple JSON-based knowledge base is located at `contributing/samples/yield_analysis_agent/knowledge_base.json`. This can be expanded with more domain-specific information.

## Customization

-   **Tools**: Modify or add new tools in `tools.py` to extend functionality.
-   **Instructions**: Adjust the agent's instructions in `agent.py` to change its persona, specialize its knowledge, or modify how it uses tools and handles parameters.
-   **Knowledge Base**: Add or edit entries in `knowledge_base.json` to improve the relevance of the `query_knowledge_base` tool.
-   **Model**: Experiment with different LLM models compatible with the ADK.

This agent provides a comprehensive suite of tools for manufacturing analysis. Depending on specific needs, further enhancements to tools, data integrations, and analytical capabilities can be developed.
