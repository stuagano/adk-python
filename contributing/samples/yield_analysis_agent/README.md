# Yield Analysis Agent

This agent assists in performing yield analysis for manufacturing processes. It can calculate key yield metrics, identify stages with low yield, and suggest potential areas for improvement.

## Features

-   **Calculate Yield Metrics**: Computes yield rate and defect rate based on total units produced and defective units.
-   **Identify Low-Yield Stages**: Pinpoints production stages that fall below a specified yield threshold.
-   **Suggest Improvement Actions**: Offers potential actions to address low-yield stages and common defect types.

## Prerequisites

-   Google Agent Development Kit (ADK) installed.
-   Access to a supported LLM (e.g., Gemini 1.5 Flash).
-   Python environment where the ADK and its dependencies are available.

## Tools

The agent utilizes the following tools:

1.  `calculate_yield_metrics(total_units: int, defective_units: int)`
    -   **Description**: Calculates yield and defect rates.
    -   **Args**:
        -   `total_units` (int): Total number of units produced.
        -   `defective_units` (int): Number of defective units.
    -   **Returns**: A dictionary with `yield_rate` and `defect_rate`.

2.  `identify_low_yield_stages(production_data_per_stage: list[dict], yield_threshold: float)`
    -   **Description**: Identifies production stages performing below a yield threshold.
    -   **Args**:
        -   `production_data_per_stage` (list[dict]): Data for each stage, e.g., `[{'stage_name': 'Assembly', 'input_units': 100, 'output_units': 95}, ...]`.
        -   `yield_threshold` (float): The minimum acceptable yield (e.g., 0.95 for 95%).
    -   **Returns**: A dictionary with a list of `low_yield_stages`, including their names and calculated yields.

3.  `suggest_improvement_actions(low_yield_stages: list[dict], common_defect_types: list[str])`
    -   **Description**: Suggests actions to improve yield.
    -   **Args**:
        -   `low_yield_stages` (list[dict]): Output from `identify_low_yield_stages` or manually provided.
        -   `common_defect_types` (list[str]): A list of common defect descriptions (e.g., `["Cracked casing", "Faulty sensor"]`).
    -   **Returns**: A dictionary with a list of `suggested_actions`.

## How to Run the Agent

This agent is designed to be run within the Google ADK framework. Typically, you would use the ADK CLI or a custom script to serve and interact with the agent.

**Example Interaction (Conceptual):**

1.  **User**: "Calculate the yield if we produced 1000 widgets and 50 were defective."
    -   **Agent (calls `calculate_yield_metrics`)**: "The yield rate is 95.0% and the defect rate is 5.0%."

2.  **User**: "Analyze the following stage data with a 90% yield threshold: Stage A (Input: 200, Output: 185), Stage B (Input: 185, Output: 160), Stage C (Input: 160, Output: 155)."
    -   **Agent (calls `identify_low_yield_stages`)**: "Stage B has a yield of approximately 86.49%, which is below the 90% threshold."

3.  **User**: "Stage B is a problem, and we're seeing a lot of 'incomplete welds'. What should we do?"
    -   **Agent (calls `suggest_improvement_actions`)**: "Based on low yield at Stage B and 'incomplete welds' defects, I suggest: Investigate root causes for low yield at stage: Stage B. Implement corrective actions for defect type: incomplete welds."

## Agent Configuration

-   **Model**: `gemini-1.5-flash` (configurable in `agent.py`)
-   **Tools**: Defined in `tools.py`
-   **Instructions**: The agent's behavior and tool usage guidelines are defined in the `instruction` parameter within `agent.py`.

## Customization

-   **Tools**: Modify or add new tools in `tools.py` to extend functionality (e.g., connect to a database for production data, perform statistical analysis).
-   **Instructions**: Adjust the agent's instructions in `agent.py` to change its persona, specialize its knowledge, or modify how it uses tools.
-   **Model**: Experiment with different LLM models compatible with the ADK.

This agent provides a foundational example for yield analysis. Depending on the complexity of the manufacturing environment, further enhancements to tools, data integration, and analytical capabilities may be required.
