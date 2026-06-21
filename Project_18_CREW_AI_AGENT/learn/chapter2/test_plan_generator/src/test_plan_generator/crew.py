from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent

@CrewBase
class TestPlanGenerator():
    """TestPlanGenerator crew"""

    agents: list[BaseAgent]
    tasks: list[Task]

    @agent
    def test_manager(self) -> Agent:
        return Agent(
            config=self.agents_config['test_manager'], # type: ignore[index]
            verbose=True
        )

    @agent
    def test_engineer(self) -> Agent:
        return Agent(
            config=self.agents_config['test_engineer'], # type: ignore[index]
            verbose=True
        )

    @task
    def plan_creation_task(self) -> Task:
        return Task(
            config=self.tasks_config['plan_creation_task'], # type: ignore[index]
        )

    @task
    def case_creation_task(self) -> Task:
        return Task(
            config=self.tasks_config['case_creation_task'], # type: ignore[index]
            output_file='test_artifacts.md'
        )

    @crew
    def crew(self) -> Crew:
        """Creates the TestPlanGenerator crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
