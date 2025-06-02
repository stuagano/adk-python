#!/bin/bash

# Helper function for Yes/No questions
# $1: Prompt message
# $2: Default choice (y or n)
# Returns 0 for yes, 1 for no
ask_yes_no() {
    local prompt="$1"
    local default_choice="$2"
    local choice

    while true; do
        if [[ "$default_choice" == "y" ]]; then
            read -r -p "$prompt [Y/n]: " choice
            choice=${choice:-Y}
        elif [[ "$default_choice" == "n" ]]; then
            read -r -p "$prompt [y/N]: " choice
            choice=${choice:-N}
        else
            read -r -p "$prompt [y/n]: " choice # Should not happen if used correctly
        fi

        case "$choice" in
            [Yy]* ) return 0;; # Yes
            [Nn]* ) return 1;; # No
            * ) echo "Please answer yes (y) or no (n).";;
        esac
    done
}

run_locally() {
    echo -e "\n--- Run ADK Web UI Locally ---"
    local agents_dir
    while true; do
        read -r -p "Enter the path to your AGENTS_DIR (e.g., ./my_adk_agents): " agents_dir
        if [[ -d "$agents_dir" ]]; then
            break
        else
            echo "Error: Directory '$agents_dir' not found. Please enter a valid path."
        fi
    done

    read -r -p "Enter HOST address (default: 127.0.0.1): " host
    host=${host:-127.0.0.1}

    read -r -p "Enter PORT number (default: 8080): " port
    port=${port:-8080}

    local reload_opt=""
    if ask_yes_no "Enable auto-reload?" "y"; then
        reload_opt="--reload"
    fi

    local cmd="adk web \"$agents_dir\" --host \"$host\" --port \"$port\" $reload_opt"
    echo -e "\nConstructed command:"
    echo "$cmd"

    if ask_yes_no "Run this command?" "y"; then
        echo "Executing command..."
        eval "$cmd" # Using eval to correctly handle quotes and spaces in paths
    else
        echo "Command not executed."
    fi
}

deploy_cloud_run() {
    echo -e "\n--- Deploy ADK Agent to Cloud Run (with Web UI) ---"
    local agent_path
    while true; do
        read -r -p "Enter the path to your specific AGENT's directory (e.g., ./my_adk_agents/my_agent): " agent_path
        if [[ -d "$agent_path" ]]; then
            break
        else
            echo "Error: Directory '$agent_path' not found. Please enter a valid path."
        fi
    done

    local project_id
    while true; do
        read -r -p "Enter your Google Cloud Project ID: " project_id
        if [[ -n "$project_id" ]]; then
            break
        else
            echo "Error: Project ID cannot be empty."
        fi
    done

    local region
    while true; do
        read -r -p "Enter the Google Cloud Region (e.g., us-central1): " region
        if [[ -n "$region" ]]; then
            break
        else
            echo "Error: Region cannot be empty."
        fi
    done

    local with_ui_opt=""
    if ask_yes_no "Deploy with Web UI?" "y"; then
        with_ui_opt="--with_ui"
    fi

    local agent_basename=$(basename "$agent_path")
    local suggested_service_name="${agent_basename}-ui"
    read -r -p "Enter Service Name (default: $suggested_service_name): " service_name
    service_name=${service_name:-$suggested_service_name}

    read -r -p "Enter Session DB URL (optional, press Enter to skip): " session_db_url
    local session_db_opt=""
    if [[ -n "$session_db_url" ]]; then
        session_db_opt="--session_db_url \"$session_db_url\""
    fi

    local cmd="adk deploy cloud_run \"$agent_path\" --project \"$project_id\" --region \"$region\" --service_name \"$service_name\" $with_ui_opt $session_db_opt"
    echo -e "\nConstructed command:"
    echo "$cmd"

    if ask_yes_no "Run this command?" "y"; then
        echo "Executing command..."
        echo "Note: This may take a few minutes and require gcloud authentication and permissions."
        eval "$cmd" # Using eval for correct parsing
    else
        echo "Command not executed."
    fi
}

# Main menu
while true; do
    echo -e "\nADK Agent Management"
    echo "----------------------"
    echo "1. Run ADK Web UI locally"
    echo "2. Deploy ADK Agent to Cloud Run (with Web UI)"
    echo "3. Exit"
    echo "----------------------"
    read -r -p "Enter your choice [1-3]: " main_choice

    case $main_choice in
        1)
            run_locally
            ;;
        2)
            deploy_cloud_run
            ;;
        3)
            echo "Exiting."
            break
            ;;
        *)
            echo "Invalid option. Please try again."
            ;;
    esac
    echo -e "\nReturning to main menu..."
done
# To make this script executable: chmod +x startup.sh
# Then run it with: ./startup.sh
