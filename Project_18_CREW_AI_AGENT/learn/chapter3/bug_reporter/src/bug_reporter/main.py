#!/usr/bin/env python
import sys
import warnings

from bug_reporter.crew import BugReporter

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

def run():
    """
    Run the crew.
    """
    inputs = {
        'screenshot_metadata': 'The submission button on the checkout page is totally hidden behind the sticky site footer on screens under 768px wide.'
    }
    
    try:
        BugReporter().crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")
