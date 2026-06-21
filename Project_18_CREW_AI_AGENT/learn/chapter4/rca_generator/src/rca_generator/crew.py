from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent

@CrewBase
class RcaGenerator():
    """RcaGenerator crew"""

    agents: list[BaseAgent]
    tasks: list[Task]

    @agent
    def devops_engineer(self) -> Agent:
        return Agent(
            config=self.agents_config['devops_engineer'], # type: ignore[index]
            verbose=True
        )

    @agent
    def post_mortem_writer(self) -> Agent:
        return Agent(
            config=self.agents_config['post_mortem_writer'], # type: ignore[index]
            verbose=True
        )

    @task
    def analyze_jira_issue(self) -> Task:
        return Task(
            config=self.tasks_config['analyze_jira_issue'], # type: ignore[index]
        )

    @task
    def generate_rca_doc(self) -> Task:
        return Task(
            config=self.tasks_config['generate_rca_doc'], # type: ignore[index]
            output_file='RCADocument.md'
        )

    @crew
    def crew(self) -> Crew:
        """Creates the RcaGenerator crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
