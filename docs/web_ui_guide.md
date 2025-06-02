## Running the ADK Web UI Locally

The ADK Web UI provides a convenient way to interact with and test your agents. To run the UI locally, use the `adk web` command.

### Command Usage

The basic syntax for running the ADK Web UI is:

```bash
adk web <AGENTS_DIR> [OPTIONS]
```

### `AGENTS_DIR` Argument

The `AGENTS_DIR` argument is a required path to the directory containing your agent definitions. The ADK expects a specific structure for this directory:

*   The `AGENTS_DIR` itself should be a directory.
*   Each immediate sub-directory within `AGENTS_DIR` represents an individual agent.
*   Inside each agent's sub-directory, you should have the necessary Python files that define your agent, typically including:
    *   `__init__.py`: This can be an empty file, but it's needed to make the agent directory a Python package.
    *   `agent.py`: This file usually contains the core logic and class definition for your agent.

**Example Directory Structure:**

```
my_adk_agents/
├── agent_one/
│   ├── __init__.py
│   └── agent.py
└── agent_two/
    ├── __init__.py
    └── agent.py
```

In this example, `my_adk_agents` would be your `AGENTS_DIR`.

### Common Options

You can modify the behavior of the `adk web` command with several useful options:

*   `--port <PORT_NUMBER>`: Specifies the port on which the Web UI will run. If not provided, it defaults to `8000`.
    *Example:* `--port 8080`
*   `--host <HOST_ADDRESS>`: Specifies the host address the Web UI will bind to. The default is `127.0.0.1` (localhost), which means the UI will only be accessible from your local machine. To make it accessible from other machines on your network, you can use `0.0.0.0`.
    *Example:* `--host 0.0.0.0`
*   `--reload`: Enables auto-reloading of the server when code changes are detected. This is very useful during development as it saves you from manually restarting the server after every modification.

### Example Command

Assuming you have an ADK agents project located in a directory named `my_adk_agents` in your current path, you can run the Web UI with the following command:

```bash
adk web ./my_adk_agents --port 8001 --reload
```

This command will:

1.  Start the ADK Web UI.
2.  Look for agent definitions in the `./my_adk_agents` directory.
3.  Make the UI accessible on port `8001`.
4.  Enable automatic reloading on code changes.

### Accessing the UI

Once the `adk web` command is running, you will see output in your terminal indicating that the server has started, typically mentioning the address and port.

To access the UI, open your web browser and navigate to:

```
http://localhost:PORT
```

Replace `PORT` with the port number you specified (or `8000` if you used the default). For the example command above, you would go to:

```
http://localhost:8001
```

You should then see the ADK Web UI, allowing you to select and interact with the agents found in your `AGENTS_DIR`.

## Deploying an Agent with Web UI to Google Cloud Run

You can deploy your ADK agent, along with the Web UI for interaction, directly to Google Cloud Run using the `adk deploy cloud_run` command. This command automates the process of containerizing your agent and deploying it as a scalable service.

### Command Usage

The basic syntax for deploying to Cloud Run is:

```bash
adk deploy cloud_run <AGENT> [OPTIONS]
```

### `--with_ui` Flag

To include the Web UI in your Cloud Run deployment, you must use the `--with_ui` flag. Without this flag, only the agent's API endpoints would be deployed.

```bash
adk deploy cloud_run <AGENT> --with_ui [OTHER_OPTIONS]
```

### Mandatory Arguments

*   `AGENT`: This is the path to the specific agent's source code folder that you want to deploy. Unlike `adk web` which takes a directory of multiple agents, this command requires the path to a single agent's directory (e.g., `my_adk_agents/my_specific_agent`).
*   `--project <PROJECT_ID>`: Your Google Cloud Project ID where the agent will be deployed.
    *Example:* `--project my-gcp-project-123`
*   `--region <REGION>`: The Google Cloud region where your Cloud Run service will be hosted (e.g., `us-central1`, `europe-west2`).
    *Example:* `--region us-central1`

### Important Optional Arguments

*   `--service_name <SERVICE_NAME>`: Allows you to specify a custom name for your Cloud Run service. If not provided, a name will be generated based on your agent or app name.
    *Example:* `--service_name my-cool-agent-ui`
*   `--app_name <APP_NAME>`: If you want the application name (which might be used in URLs or service identifiers) to be different from the agent's folder name, you can set it with this option.
    *Example:* `--app_name my-custom-app`
*   `--session_db_url <DATABASE_URL>`: For agents that require session persistence (e.g., to remember conversation history across requests when using the UI), you can provide a database URL. This typically points to a Firestore database or a Cloud SQL instance. A brief mention here; detailed configuration depends on your specific database choice.
    *Example:* `--session_db_url firestore://?collection=my_agent_sessions`

### Example Command

Let's assume you have an agent located in `my_adk_agents/my_specific_agent`, and you want to deploy it to your GCP project `my-gcp-project-123` in the `us-east1` region, with the Web UI included:

```bash
adk deploy cloud_run ./my_adk_agents/my_specific_agent \
    --with_ui \
    --project my-gcp-project-123 \
    --region us-east1 \
    --service_name my-specific-agent-ui
```

This command will:

1.  Take the agent code from `./my_adk_agents/my_specific_agent`.
2.  Include the Web UI in the deployment.
3.  Target your `my-gcp-project-123` project and the `us-east1` region.
4.  Name the resulting Cloud Run service `my-specific-agent-ui`.

### Containerization and Deployment

The `adk deploy cloud_run` command handles the complexities of packaging your agent and the Web UI into a Docker container, pushing this container to Google Container Registry (or Artifact Registry), and then deploying it to Cloud Run. You don't need to write a Dockerfile manually for this process.

### Prerequisites

Before running the deployment command, ensure you have the following:

*   **`gcloud` CLI Installed and Authenticated:** The Google Cloud CLI must be installed on your machine and configured (e.g., via `gcloud auth login` and `gcloud config set project <YOUR_PROJECT_ID>`).
*   **Permissions:** The authenticated `gcloud` user or service account must have the necessary IAM permissions in your Google Cloud Project to:
    *   Enable and use the Cloud Build API (for container building).
    *   Push images to Container Registry or Artifact Registry.
    *   Create and manage Cloud Run services.
    *   (If applicable) Access other services like Firestore or Cloud SQL if using `--session_db_url`.

Once deployed, the command will output the URL of your Cloud Run service, which you can use to access your agent's Web UI.

## Using the Interactive Startup Script (`startup.sh`)

To simplify the process of running the ADK Web UI locally or deploying an agent to Google Cloud Run, an interactive shell script named `startup.sh` is provided at the root of the repository. This script guides you through the necessary steps and helps construct the required `adk` commands.

### Making the Script Executable

Before you can run the script, you need to make it executable. Open your terminal, navigate to the root directory of the ADK repository, and run:

```bash
chmod +x startup.sh
```

### Running the Script

Once executable, you can run the script with:

```bash
./startup.sh
```

### Main Menu Options

The script will present you with a main menu:

1.  **Run ADK Web UI locally:** This option guides you through setting up and running the `adk web` command for local testing.
2.  **Deploy ADK Agent to Cloud Run (with Web UI):** This option assists in constructing and running the `adk deploy cloud_run` command, including the Web UI.
3.  **Exit:** Closes the script.

### Guided Prompts

For both local execution and Cloud Run deployment, the script will:

*   Prompt you for necessary information, such as directory paths for your agents (`AGENTS_DIR` or specific `AGENT_PATH`), Google Cloud Project ID, region, desired port numbers, etc.
*   Provide sensible defaults for some options (e.g., host address `127.0.0.1`, port `8080`).
*   Validate certain inputs (e.g., ensuring specified directories exist).

### Command Confirmation

A key feature of the `startup.sh` script is that it will display the fully constructed `adk` command based on your inputs *before* executing it. You will then be asked to confirm whether you want to run the displayed command. This allows you to review the command for correctness or copy it for manual use if preferred.

Using `startup.sh` can be a great way to get started with running and deploying your ADK agents without needing to memorize all the command-line arguments immediately.
