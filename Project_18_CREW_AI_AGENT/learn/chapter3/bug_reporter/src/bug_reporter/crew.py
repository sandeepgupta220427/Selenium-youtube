from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent

@CrewBase
class BugReporter():
    """BugReporter crew"""

    agents: list[BaseAgent]
    tasks: list[Task]

    @agent
    def qa_reporter(self) -> Agent:
        return Agent(
            config=self.agents_config['qa_reporter'], # type: ignore[index]
            verbose=True
        )

    @agent
    def dev_triage(self) -> Agent:
        return Agent(
            config=self.agents_config['dev_triage'], # type: ignore[index]
            verbose=True
        )

    @task
    def generate_bug_report(self) -> Task:
        return Task(
            config=self.tasks_config['generate_bug_report'], # type: ignore[index]
        )

    @task
    def triage_bug_report(self) -> Task:
        return Task(
            config=self.tasks_config['triage_bug_report'], # type: ignore[index]
            output_file='final_bug_report.md'
        )

    @crew
    def crew(self) -> Crew:
        """Creates the BugReporter crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
