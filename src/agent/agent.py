from src.config import config
from src.logger import logger
from src.registry import REGISTED_AGENTS, REGISTED_TOOLS
from src.models import model_manager

AUTHORIZED_IMPORTS = [
    "pandas",
    "requests",
    "numpy"
]

def create_agent():
    
    if config.agent.use_hierarchical_agent:
        # 检查是否使用军事系统
        if config.agent.use_military_system:
            return create_military_system()
        else:
            return create_general_system()
    else:
        return create_single_agent()

def create_military_system():
    """创建军事参谋系统"""
    military_chief_config = getattr(config.agent, "military_chief_of_staff_agent_config")
    
    # 创建下级军事智能体
    sub_agents_ids = military_chief_config.managed_agents
    sub_agents = []
    for sub_agent_id in sub_agents_ids:
        if sub_agent_id not in REGISTED_AGENTS:
            raise ValueError(f"Agent ID '{sub_agent_id}' is not registered.")
        sub_agent_config = getattr(config.agent, f"{sub_agent_id}_config")
        
        tool_ids = sub_agent_config.tools
        tools = []
        for tool_id in tool_ids:
            if tool_id not in REGISTED_TOOLS:
                raise ValueError(f"Tool ID '{tool_id}' is not registered.")
            tools.append(REGISTED_TOOLS[tool_id]())
            
        sub_agent = REGISTED_AGENTS[sub_agent_id](
            config=sub_agent_config,
            model=model_manager.registed_models[sub_agent_config.model_id],
            tools=tools,
            max_steps=sub_agent_config.max_steps,
            name=sub_agent_config.name,
            description=sub_agent_config.description,
            provide_run_summary=True,
        )
        
        sub_agents.append(sub_agent)
    
    # 创建军事参谋长的工具
    tool_ids = military_chief_config.tools
    tools = []
    for tool_id in tool_ids:
        if tool_id not in REGISTED_TOOLS:
            raise ValueError(f"Tool ID '{tool_id}' is not registered.")
        tools.append(REGISTED_TOOLS[tool_id]())
        
    # 创建军事参谋长智能体
    agent = REGISTED_AGENTS["military_chief_of_staff_agent"](
        config=military_chief_config,
        model=model_manager.registed_models[military_chief_config.model_id],
        tools=tools,
        max_steps=military_chief_config.max_steps,
        managed_agents=sub_agents,
        description=military_chief_config.description,
        name=military_chief_config.name,
        provide_run_summary=True,
    )
    
    return agent

def create_general_system():
    """创建通用智能体系统"""
    planning_agent_config = getattr(config.agent, "planning_agent_config")
    
    sub_agents_ids = planning_agent_config.managed_agents
    sub_agents = []
    for sub_agent_id in sub_agents_ids:
        if sub_agent_id not in REGISTED_AGENTS:
            raise ValueError(f"Agent ID '{sub_agent_id}' is not registered.")
        sub_agent_config = getattr(config.agent, f"{sub_agent_id}_config")
        
        tool_ids = sub_agent_config.tools
        tools = []
        for tool_id in tool_ids:
            if tool_id not in REGISTED_TOOLS:
                raise ValueError(f"Tool ID '{tool_id}' is not registered.")
            tools.append(REGISTED_TOOLS[tool_id]())
            
        sub_agent = REGISTED_AGENTS[sub_agent_id](
            config=sub_agent_config,
            model=model_manager.registed_models[sub_agent_config.model_id],
            tools=tools,
            max_steps=sub_agent_config.max_steps,
            name=sub_agent_config.name,
            description=sub_agent_config.description,
            provide_run_summary=True,
        )
        
        sub_agents.append(sub_agent)
    
    tool_ids = planning_agent_config.tools
    tools = []
    for tool_id in tool_ids:
        if tool_id not in REGISTED_TOOLS:
            raise ValueError(f"Tool ID '{tool_id}' is not registered.")
        tools.append(REGISTED_TOOLS[tool_id]())
        
    agent = REGISTED_AGENTS["planning_agent"](
        config=planning_agent_config,
        model=model_manager.registed_models[planning_agent_config.model_id],
        tools=tools,
        max_steps=planning_agent_config.max_steps,
        managed_agents=sub_agents,
        description=planning_agent_config.description,
        name=planning_agent_config.name,
        provide_run_summary=True,
    )
    
    return agent

def create_single_agent():
    """创建单一智能体"""
    deep_analyzer_agent_config = getattr(config.agent, "deep_analyzer_agent_config")
    tools = []
    for tool_id in deep_analyzer_agent_config.tools:
        if tool_id not in REGISTED_TOOLS:
            raise ValueError(f"Tool ID '{tool_id}' is not registered.")
        tools.append(REGISTED_TOOLS[tool_id]())
        
    agent = REGISTED_AGENTS["deep_analyzer_agent"](
        config=deep_analyzer_agent_config,
        model=model_manager.registed_models[deep_analyzer_agent_config.model_id],
        tools=tools,
        max_steps=deep_analyzer_agent_config.max_steps,
        name=deep_analyzer_agent_config.name,
        description=deep_analyzer_agent_config.description,
        provide_run_summary=True,
    )
    
    return agent