from typing import (
    Any,
    Callable,
    Optional
)
import json
import yaml
from rich.panel import Panel
from rich.text import Text

from src.tools import AsyncTool
from src.exception import (
    AgentGenerationError,
    AgentParsingError,
    AgentToolExecutionError,
    AgentToolCallError
)
from src.base.async_multistep_agent import (PromptTemplates,
                                            populate_template,
                                            AsyncMultiStepAgent
                                            )
from src.memory import (ActionStep,
                        ToolCall,
                        AgentMemory)
from src.logger import (LogLevel, 
                        YELLOW_HEX, 
                        logger)
from src.models import Model, parse_json_if_needed
from src.utils.agent_types import (
    AgentAudio,
    AgentImage,
)
from src.registry import register_agent
from src.utils import assemble_project_path

@register_agent("military_chief_of_staff_agent")
class MilitaryChiefOfStaffAgent(AsyncMultiStepAgent):
    """
    军事参谋长智能体
    
    负责：
    1. 接收军事任务目标
    2. 分析任务复杂度和需求
    3. 协调各专业军事智能体
    4. 整合各部门建议形成最终作战方案
    5. 输出完整的作战部署计划
    """
    
    def __init__(
        self,
        config,
        tools: list[AsyncTool],
        model: Model,
        prompt_templates: PromptTemplates | None = None,
        max_steps: int = 30,
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

        super(MilitaryChiefOfStaffAgent, self).__init__(
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
        """初始化军事参谋长的系统提示词"""
        system_prompt = populate_template(
            self.prompt_templates["system_prompt"],
            variables={"tools": self.tools, "managed_agents": self.managed_agents},
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
        """
        执行工具调用或管理的智能体
        
        Args:
            tool_name: 工具或智能体名称
            arguments: 传递给工具的参数
        """
        # 检查工具是否存在
        available_tools = {**self.tools, **self.managed_agents}
        if tool_name not in available_tools:
            raise AgentToolExecutionError(
                f"未知工具 {tool_name}，可用工具: {', '.join(available_tools)}.", self.logger
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
                raise TypeError(f"不支持的参数类型: {type(arguments)}")

        except TypeError as e:
            # 处理无效参数
            description = getattr(tool, "description", "无描述")
            if is_managed_agent:
                error_msg = (
                    f"向军事专家 '{tool_name}' 发送无效请求，参数 {json.dumps(arguments, ensure_ascii=False)}: {e}\n"
                    "您应该向此军事专家发送有效请求。\n"
                    f"专家描述: {description}"
                )
            else:
                error_msg = (
                    f"调用工具 '{tool_name}' 时参数无效 {json.dumps(arguments, ensure_ascii=False)}: {e}\n"
                    "您应该使用正确的输入参数调用此工具。\n"
                    f"期望输入: {json.dumps(tool.parameters)}\n"
                    f"返回输出类型: {tool.output_type}\n"
                    f"工具描述: '{description}'"
                )
            raise AgentToolCallError(error_msg, self.logger) from e

        except Exception as e:
            # 处理执行错误
            if is_managed_agent:
                error_msg = (
                    f"执行向军事专家 '{tool_name}' 的请求时出错，参数 {json.dumps(arguments)}: {e}\n"
                    "请重试或请求其他军事专家"
                )
            else:
                error_msg = (
                    f"执行工具 '{tool_name}' 时出错，参数 {json.dumps(arguments)}: {type(e).__name__}: {e}\n"
                    "请重试或使用其他工具"
                )
            raise AgentToolExecutionError(error_msg, self.logger) from e 

    async def step(self, memory_step: ActionStep) -> None | Any:
        """
        执行一个步骤：军事参谋长思考、行动并观察结果
        如果步骤不是最终步骤，返回None
        """
        memory_messages = await self.write_memory_to_messages()
        input_messages = memory_messages.copy()
        memory_step.model_input_messages = input_messages

        try:
            chat_message = await self.model(
                input_messages,
                stop_sequences=["Observation:", "Calling tools:"],
                tools_to_call_from=list(self.tools.values()),
            )
            memory_step.model_output_message = chat_message
            model_output = chat_message.content
            self.logger.log_markdown(
                content=model_output if model_output else str(chat_message.raw),
                title="军事参谋长输出:",
                level=LogLevel.DEBUG,
            )

            memory_step.model_output_message.content = model_output
            memory_step.model_output = model_output
        except Exception as e:
            raise AgentGenerationError(f"生成输出时出错:\n{e}", self.logger) from e

        if chat_message.tool_calls is None or len(chat_message.tool_calls) == 0:
            try:
                chat_message = self.model.parse_tool_calls(chat_message)
            except Exception as e:
                raise AgentParsingError(f"解析模型输出中的工具调用时出错: {e}", self.logger)
        else:
            for tool_call in chat_message.tool_calls:
                tool_call.function.arguments = parse_json_if_needed(tool_call.function.arguments)

        tool_call = chat_message.tool_calls[0]
        tool_name, tool_call_id = tool_call.function.name, tool_call.id
        tool_arguments = tool_call.function.arguments
        memory_step.model_output = str(f"调用工具: '{tool_name}' 参数: {tool_arguments}")
        memory_step.tool_calls = [ToolCall(name=tool_name, arguments=tool_arguments, id=tool_call_id)]

        # 执行工具
        self.logger.log(
            Panel(Text(f"调用工具: '{tool_name}' 参数: {tool_arguments}")),
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
                    f"[bold {YELLOW_HEX}]最终答案:[/bold {YELLOW_HEX}] 从状态中提取键 '{result}' 返回值 '{final_result}'.",
                    level=LogLevel.INFO,
                )
            else:
                final_result = result
                self.logger.log(
                    Text(f"最终结果: {final_result}", style=f"bold {YELLOW_HEX}"),
                    level=LogLevel.INFO,
                )

            memory_step.action_output = final_result
            return final_result
        else:
            if tool_arguments is None:
                tool_arguments = {}
            observation = await self.execute_tool_call(tool_name, tool_arguments)
            observation_type = type(observation)
            if observation_type in [AgentImage, AgentAudio]:
                if observation_type == AgentImage:
                    observation_name = "image.png"
                elif observation_type == AgentAudio:
                    observation_name = "audio.mp3"
                
                self.state[observation_name] = observation
                updated_information = f"已将 '{observation_name}' 存储到内存中。"
            else:
                updated_information = str(observation).strip()
            
            self.logger.log(
                f"观察结果: {updated_information.replace('[', '|')}",  # 转义潜在的rich标签组件
                level=LogLevel.INFO,
            )
            memory_step.observations = updated_information
            return None 