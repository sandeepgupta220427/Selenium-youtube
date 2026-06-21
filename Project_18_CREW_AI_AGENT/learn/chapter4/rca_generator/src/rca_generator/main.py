#!/usr/bin/env python
import sys
import warnings

from rca_generator.crew import RcaGenerator

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

def run():
    """
    Run the crew.
    """
    inputs = {
        'jira_ticket_details': 'JIRA-10984: Major production outage on Auth Service. At 09:30 AM, users started getting 503 errors logging in. CPU spiked to 100% on auth gateway pods. Auto-scaling failed because max pods limit was reached. It was resolved at 10:15 AM by rolling back the 09:15 AM release that introduced a regex bug in email validation.'
    }
    
    try:
        RcaGenerator().crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")
