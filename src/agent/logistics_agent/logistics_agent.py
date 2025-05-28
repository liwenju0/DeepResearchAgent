from typing import Any, Callable, Optional
import yaml
from src.tools import AsyncTool
from src.base.async_multistep_agent import (PromptTemplates, populate_template, AsyncMultiStepAgent)
from src.memory import AgentMemory
from src.logger import LogLevel
from src.models import Model
from src.registry import register_agent
from src.utils import assemble_project_path

@register_agent("logistics_agent")
class LogisticsAgent(AsyncMultiStepAgent):
    """
    后勤保障智能体
    
    负责：
    1. 制定后勤保障计划
    2. 规划补给线路和时间
    3. 评估后勤需求和资源
    4. 协调运输和储存
    5. 确保作战持续性
    """
    
    def __init__(
        self,
        config,
        tools: list[AsyncTool],
        model: Model,
        prompt_templates: PromptTemplates | None = None,
        max_steps: int = 10,
        add_base_tools: bool = False,
        verbosity_level: LogLevel = LogLevel.INFO,
        grammar: dict[str, str] | None = None,
        managed_agents: list | None = None,
        step_callbacks: list[Callable] | None = None,
        planning_interval: int | None = None,
        name: str | None = None,
        description: str | None = None,
        provide_run_summary: bool = False,
        final_answer_checks: list[Callable] | None = None,
        **kwargs
    ):
        self.config = config

        super(LogisticsAgent, self).__init__(
            tools=tools,
            model=model,
            prompt_templates=prompt_templates,
            max_steps=max_steps,
            add_base_tools=add_base_tools,
            verbosity_level=verbosity_level,
            grammar=grammar,
            managed_agents=managed_agents,
            step_callbacks=step_callbacks,
            planning_interval=planning_interval,
            name=name,
            description=description,
            provide_run_summary=provide_run_summary,
            final_answer_checks=final_answer_checks,
        )

        template_path = assemble_project_path(self.config.template_path)
        with open(template_path, "r") as f:
            self.prompt_templates = yaml.safe_load(f)
        
        self.system_prompt = self.initialize_system_prompt()
        self.user_prompt = self.initialize_user_prompt()

        self.memory = AgentMemory(
            system_prompt=self.system_prompt,
            user_prompt=self.user_prompt,
        )

    def initialize_system_prompt(self) -> str:
        """初始化后勤保障专家的系统提示词"""
        system_prompt = populate_template(
            self.prompt_templates["system_prompt"],
            variables={"tools": self.tools},
        )
        return system_prompt

    def initialize_user_prompt(self) -> str:
        """初始化用户提示词"""
        user_prompt = populate_template(
            self.prompt_templates["user_prompt"],
            variables={},
        )
        return user_prompt

    def initialize_task_instruction(self) -> str:
        """初始化任务指令"""
        task_instruction = populate_template(
            self.prompt_templates["task_instruction"],
            variables={"task": self.task},
        )
        return task_instruction
    
    def _substitute_state_variables(self, arguments: dict[str, str] | str) -> dict[str, Any] | str:
        """替换参数中的状态变量"""
        if isinstance(arguments, dict):
            return {
                key: self.state.get(value, value) if isinstance(value, str) else value
                for key, value in arguments.items()
            }
        return arguments
    
    async def execute_tool_call(self, tool_name: str, arguments: dict[str, str] | str) -> Any:
        """执行工具调用"""
        from src.exception import AgentToolExecutionError, AgentToolCallError
        import json
        
        # 检查工具是否存在
        available_tools = {**self.tools, **self.managed_agents}
        if tool_name not in available_tools:
            raise AgentToolExecutionError(
                f"Unknown tool {tool_name}, should be one of: {', '.join(available_tools)}.", self.logger
            )

        # 获取工具并替换状态变量
        tool = available_tools[tool_name]
        arguments = self._substitute_state_variables(arguments)
        is_managed_agent = tool_name in self.managed_agents

        try:
            # 调用工具
            if isinstance(arguments, dict):
                return await tool(**arguments) if is_managed_agent else await tool(**arguments, sanitize_inputs_outputs=True)
            elif isinstance(arguments, str):
                return await tool(arguments) if is_managed_agent else await tool(arguments, sanitize_inputs_outputs=True)
            else:
                raise TypeError(f"Unsupported arguments type: {type(arguments)}")

        except TypeError as e:
            description = getattr(tool, "description", "No description")
            if is_managed_agent:
                error_msg = (
                    f"Invalid request to team member '{tool_name}' with arguments {json.dumps(arguments, ensure_ascii=False)}: {e}\n"
                    "You should call this team member with a valid request.\n"
                    f"Team member description: {description}"
                )
            else:
                error_msg = (
                    f"Invalid call to tool '{tool_name}' with arguments {json.dumps(arguments, ensure_ascii=False)}: {e}\n"
                    "You should call this tool with correct input arguments.\n"
                    f"Expected inputs: {json.dumps(tool.parameters)}\n"
                    f"Returns output type: {tool.output_type}\n"
                    f"Tool description: '{description}'"
                )
            raise AgentToolCallError(error_msg, self.logger) from e

        except Exception as e:
            if is_managed_agent:
                error_msg = (
                    f"Error executing request to team member '{tool_name}' with arguments {json.dumps(arguments)}: {e}\n"
                    "Please try again or request to another team member"
                )
            else:
                error_msg = (
                    f"Error executing tool '{tool_name}' with arguments {json.dumps(arguments)}: {type(e).__name__}: {e}\n"
                    "Please try again or use another tool"
                )
            raise AgentToolExecutionError(error_msg, self.logger) from e
    
    async def step(self, memory_step) -> None | Any:
        """执行一个步骤"""
        from src.memory import ActionStep, ToolCall
        from src.exception import AgentGenerationError, AgentParsingError
        from src.models import ChatMessage
        from src.logger import LogLevel
        from src.utils import parse_json_if_needed
        from rich.panel import Panel
        from rich.text import Text
        
        memory_messages = await self.write_memory_to_messages()
        input_messages = memory_messages.copy()
        memory_step.model_input_messages = input_messages

        try:
            chat_message: ChatMessage = await self.model(
                input_messages,
                stop_sequences=["Observation:", "Calling tools:"],
                tools_to_call_from=list(self.tools.values()),
            )
            memory_step.model_output_message = chat_message
            model_output = chat_message.content
            self.logger.log_markdown(
                content=model_output if model_output else str(chat_message.raw),
                title="Output message of the LLM:",
                level=LogLevel.DEBUG,
            )

            memory_step.model_output_message.content = model_output
            memory_step.model_output = model_output
        except Exception as e:
            raise AgentGenerationError(f"Error while generating output:\n{e}", self.logger) from e

        if chat_message.tool_calls is None or len(chat_message.tool_calls) == 0:
            try:
                chat_message = self.model.parse_tool_calls(chat_message)
            except Exception as e:
                raise AgentParsingError(f"Error while parsing tool call from model output: {e}", self.logger)
        else:
            for tool_call in chat_message.tool_calls:
                tool_call.function.arguments = parse_json_if_needed(tool_call.function.arguments)

        tool_call = chat_message.tool_calls[0]
        tool_name, tool_call_id = tool_call.function.name, tool_call.id
        tool_arguments = tool_call.function.arguments
        memory_step.model_output = str(f"Called Tool: '{tool_name}' with arguments: {tool_arguments}")
        memory_step.tool_calls = [ToolCall(name=tool_name, arguments=tool_arguments, id=tool_call_id)]

        # 执行工具
        self.logger.log(
            Panel(Text(f"Calling tool: '{tool_name}' with arguments: {tool_arguments}")),
            level=LogLevel.INFO,
        )
        
        if tool_name == "final_answer":
            if isinstance(tool_arguments, dict):
                if "result" in tool_arguments:
                    result = tool_arguments["result"]
                else:
                    result = tool_arguments
            else:
                result = tool_arguments
            
            if isinstance(result, str) and result in self.state.keys():
                final_result = self.state[result]
                self.logger.log(
                    f"Final answer: Extracting key '{result}' from state to return value '{final_result}'.",
                    level=LogLevel.INFO,
                )
            else:
                final_result = result
                self.logger.log(
                    Text(f"Final result: {final_result}"),
                    level=LogLevel.INFO,
                )

            memory_step.action_output = final_result
            return final_result
        else:
            if tool_arguments is None:
                tool_arguments = {}
            observation = await self.execute_tool_call(tool_name, tool_arguments)
            updated_information = str(observation).strip()
            self.logger.log(
                f"Observations: {updated_information.replace('[', '|')}",
                level=LogLevel.INFO,
            )
            memory_step.observations = updated_information
            return None 