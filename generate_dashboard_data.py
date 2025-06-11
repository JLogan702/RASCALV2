import pandas as pd
import json
from datetime import datetime

# Helper function to get stoplight color based on percentage
def get_stoplight_color(percentage):
    if percentage >= 80:
        return 'green'
    elif percentage >= 50:
        return 'yellow'
    else:
        return 'red'

def calculate_sprint_readiness(df):
    """
    Calculates Sprint Readiness % overall and by component, including stoplight color and status counts.
    Definition: (Number of story tickets in future sprint AND in "To Do" or "Ready for Development")
                ÷ (Total number of story tickets in future sprint)
    """
    story_tickets = df[df['Issue Type'] == 'Story'].copy()
    future_sprints = ['Eng-Prod Sprint 8: 6/18 - 7/2', 'Eng-AIOps Sprint 8: 6/18-7/2', 'Design Sprint 8:  6/18-7/2']
    ready_statuses = ['To Do'] 

    # Filter for tickets explicitly assigned to future sprints for Sprint Readiness
    future_sprint_tickets = story_tickets[story_tickets['Sprint'].isin(future_sprints)]

    # Overall Sprint Readiness
    overall_numerator = future_sprint_tickets[future_sprint_tickets['Status'].isin(ready_statuses)].shape[0]
    overall_denominator = future_sprint_tickets.shape[0]
    overall_percentage = (overall_numerator / overall_denominator) * 100 if overall_denominator > 0 else 0

    # Sprint Readiness by Component
    component_readiness = {}
    
    # Dynamically collect all unique components from relevant columns present in the DataFrame
    all_components = pd.Series(dtype=str)
    component_cols_to_check = ['Components', 'Components.1', 'Components.2']
    
    for col in component_cols_to_check:
        if col in df.columns:
            all_components = pd.concat([all_components, df[col].dropna()])
    
    unique_components = all_components.unique()
    
    # Filter out 'Product' component if present
    filtered_components = [comp for comp in unique_components if comp != 'Product']


    for component in filtered_components: # Iterate over filtered components
        # Filter tickets that have this component in any of the available component columns
        component_filter_series = pd.Series([False] * len(future_sprint_tickets), index=future_sprint_tickets.index)
        
        for col in component_cols_to_check:
            if col in future_sprint_tickets.columns:
                component_filter_series = component_filter_series | (future_sprint_tickets[col] == component)
        
        component_tickets = future_sprint_tickets[component_filter_series]
        
        numerator = component_tickets[component_tickets['Status'].isin(ready_statuses)].shape[0]
        denominator = component_tickets.shape[0]
            
        percentage = (numerator / denominator) * 100 if denominator > 0 else 0

        # Collect status counts for this component
        status_counts = component_tickets['Status'].value_counts().to_dict()
        
        component_readiness[component] = {
            'numerator': numerator,
            'denominator': denominator,
            'percentage': round(percentage, 2),
            'stoplight': get_stoplight_color(percentage),
            'status_counts': status_counts
        }

    return {
        'overall': {
            'numerator': overall_numerator,
            'denominator': overall_denominator,
            'percentage': round(overall_percentage, 2),
            'stoplight': get_stoplight_color(overall_percentage)
        },
        'by_component': component_readiness
    }

def calculate_backlog_health(df):
    """
    Calculates Backlog Health % based on the refined definition for the active backlog.
    Numerator: Count of 'To Do' stories in the active backlog.
    Denominator: Total count of 'Story' tickets that are not 'Done',
                 and are either unassigned or in future sprints.
    """
    story_tickets_df = df[df['Issue Type'] == 'Story'].copy()
    
    # Define statuses that are considered "Done" or "finished" for exclusion from active backlog
    finished_statuses = ['Done', 'Canceled'] # Add any other 'finished' statuses from your data if needed
    
    future_sprints_list = ['Eng-Prod Sprint 8: 6/18 - 7/2', 'Eng-AIOps Sprint 8: 6/18-7/2', 'Design Sprint 8:  6/18-7/2']
    
    # Denominator: total stories in the active backlog (not Done, not in active/past sprints, but either unassigned or in future sprints)
    total_backlog_scope_df = story_tickets_df[
        (~story_tickets_df['Status'].isin(finished_statuses)) & # Status is NOT 'Done' or 'Canceled'
        (
            (story_tickets_df['Sprint'].isna()) | # Sprint is unassigned (NaN)
            (story_tickets_df['Sprint'].isin(future_sprints_list)) # OR Sprint is one of the defined future sprints
        )
    ].copy()
    
    total_story_tickets_in_backlog_scope = total_backlog_scope_df.shape[0]

    # Numerator: healthy stories within this refined active backlog scope
    healthy_statuses_backlog = ['To Do'] 
    healthy_story_tickets = total_backlog_scope_df[total_backlog_scope_df['Status'].isin(healthy_statuses_backlog)].shape[0]

    backlog_health_percentage = (healthy_story_tickets / total_story_tickets_in_backlog_scope) * 100 if total_story_tickets_in_backlog_scope > 0 else 0

    # Backlog Health by Component
    component_health = {}

    # Dynamically collect all unique components from relevant columns present in the DataFrame
    all_components = pd.Series(dtype=str)
    component_cols_to_check = ['Components', 'Components.1', 'Components.2']
    
    for col in component_cols_to_check:
        if col in df.columns:
            all_components = pd.concat([all_components, df[col].dropna()])
    
    unique_components = all_components.unique()

    # Filter out 'Product' component if present
    filtered_components = [comp for comp in unique_components if comp != 'Product']


    for component in filtered_components: # Iterate over filtered components
        # Filter tickets that have this component in any of the available component columns
        component_filter_series = pd.Series([False] * len(total_backlog_scope_df), index=total_backlog_scope_df.index)
        
        for col in component_cols_to_check:
            if col in total_backlog_scope_df.columns:
                component_filter_series = component_filter_series | (total_backlog_scope_df[col] == component)

        component_tickets = total_backlog_scope_df[component_filter_series]
        
        numerator = component_tickets[component_tickets['Status'].isin(healthy_statuses_backlog)].shape[0]
        denominator = component_tickets.shape[0]
        
        percentage = (numerator / denominator) * 100 if denominator > 0 else 0

        # Collect status counts for this component
        status_counts = component_tickets['Status'].value_counts().to_dict()

        component_health[component] = {
            'numerator': numerator,
            'denominator': denominator,
            'percentage': round(percentage, 2),
            'stoplight': get_stoplight_color(percentage),
            'status_counts': status_counts
        }

    return {
        'overall': {
            'numerator': healthy_story_tickets,
            'denominator': total_story_tickets_in_backlog_scope,
            'percentage': round(backlog_health_percentage, 2),
            'stoplight': get_stoplight_color(backlog_health_percentage)
        },
        'by_component': component_health
    }

def process_dependencies_data(df_dependencies):
    """
    Processes the dependencies data for Epics.
    """
    epic_tickets = df_dependencies[df_dependencies['Issue Type'] == 'Epic'].copy()

    dependencies_by_component = {}
    blocked_epics_unique_count = set() 
    
    # Dynamically collect all unique components from relevant columns present in the DataFrame
    all_components = pd.Series(dtype=str)
    component_cols_to_check = ['Components', 'Components.1', 'Components.2']
    
    for col in component_cols_to_check:
        if col in df_dependencies.columns: # Use df_dependencies for this context
            all_components = pd.concat([all_components, df_dependencies[col].dropna()])
    
    unique_components = all_components.unique()
    
    # Filter out 'Product' component if present
    filtered_components = [comp for comp in unique_components if comp != 'Product']

    # Initialize dependencies_by_component for all filtered components, even if they have no epics yet
    for component in filtered_components:
        dependencies_by_component[component] = []

    # Iterate through each Epic to gather dependency info
    for index, row in epic_tickets.iterrows():
        issue_key = row['Issue key']
        summary = row['Summary']
        status = row['Status']
        
        # Determine the primary component for grouping from available component columns
        component = 'Unassigned Team' # Default
        for col in component_cols_to_check:
            if col in row.index and pd.notna(row[col]): # Use row.index to check if column exists in Series
                component = row[col]
                break 
            
        # Skip if this component is 'Product'
        if component == 'Product':
            continue

        blocks = []
        blocked_by = []

        # Collect 'Blocks' relationships
        for col in ['Outward issue link (Blocks)', 'Outward issue link (Blocks).1']:
            if col in row.index and pd.notna(row[col]):
                blocks.append(row[col])

        # Collect 'Blocked By' relationships
        current_blocked_by_links = []
        for col in ['Inward issue link (Blocks)', 'Inward issue link (Blocks).1', 'Inward issue link (Blocks).2']:
            if col in row.index and pd.notna(row[col]):
                current_blocked_by_links.append(row[col])
        
        if current_blocked_by_links:
            blocked_epics_unique_count.add(issue_key) 
            blocked_by.extend(current_blocked_by_links)

        # Ensure component exists in dependencies_by_component (it should if initialized above)
        if component not in dependencies_by_component:
             dependencies_by_component[component] = [] # Fallback, should ideally not happen after initialization

        dependencies_by_component[component].append({
            'issue_key': issue_key,
            'summary': summary,
            'status': status,
            'blocks': blocks,
            'blocked_by': blocked_by
        })
        
    return {
        'dependencies_by_component': dependencies_by_component,
        'blocked_epics_count': len(blocked_epics_unique_count) 
    }


def generate_dashboard_data_js(main_csv_file='rascal_data.csv', dependencies_csv_file='rascal_dependencies.csv', output_js_file='dashboard_data.js'):
    df_main = pd.read_csv(main_csv_file)
    df_dependencies = pd.read_csv(dependencies_csv_file)

    sprint_readiness_data = calculate_sprint_readiness(df_main)
    backlog_health_data = calculate_backlog_health(df_main)
    dependencies_data = process_dependencies_data(df_dependencies)

    # Calculate overall program status for Program Summary
    program_summary_status = "green" 
    
    # Check for red conditions
    if sprint_readiness_data['overall']['stoplight'] == 'red' or \
       backlog_health_data['overall']['stoplight'] == 'red' or \
       dependencies_data['blocked_epics_count'] > 5: 
        program_summary_status = "red"
    # Check for yellow conditions (only if not already red)
    elif sprint_readiness_data['overall']['stoplight'] == 'yellow' or \
         backlog_health_data['overall']['stoplight'] == 'yellow' or \
         (dependencies_data['blocked_epics_count'] > 0 and dependencies_data['blocked_epics_count'] <= 5): 
        program_summary_status = "yellow"

    dashboard_data = {
        'sprintReadiness': sprint_readiness_data,
        'backlogHealth': backlog_health_data,
        'dependencies': dependencies_data,
        'programSummary': {
            'overall_status': program_summary_status,
            'generation_date': datetime.now().strftime("%B %d, %Y")
        }
    }

    js_content = f"const dashboardData = {json.dumps(dashboard_data, indent=2)};"

    with open(output_js_file, 'w') as f:
        f.write(js_content)
    print(f"Generated {output_js_file} successfully!")

if __name__ == "__main__":
    generate_dashboard_data_js()
