#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

from test_plan_generator.crew import TestPlanGenerator

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

def run():
    """
    Run the crew.
    """
    inputs = {
        'feature_description': 'A user login page that includes an email input, password input, and a two-factor authentication (2FA) SMS verification code.'
    }
    
    try:
        TestPlanGenerator().crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")
