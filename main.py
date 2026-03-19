from devhive.services.dev_team_agent import DevTeamAgent
import json

def main():
    print("Welcome to DevHive MVP - AI Development Team Orchestrator\n")
    
    # Instantiate the development team agent
    # This acts as the public interface for external systems
    team = DevTeamAgent()
    
    # Define a feature request
    feature_request = "Implement CSV export functionality in the analytics dashboard"
    
    print(f"Submitting request: \"{feature_request}\"...\n")
    
    # Execute the request through the orchestrator pipeline
    result = team.build_feature(feature_request)
    
    # Display the structured output
    print("\n--- Project Execution Summary ---")
    print(json.dumps(result, indent=4))
    
    # Example of how an external agent would access specific outputs
    if "implementer" in result:
        print("\n--- Implementation Details ---")
        code_plan = result["implementer"].get("modules", {})
        for file, code in code_plan.items():
            print(f"File: {file}")
            # print(code) # Uncomment to see code
            
if __name__ == "__main__":
    main()
