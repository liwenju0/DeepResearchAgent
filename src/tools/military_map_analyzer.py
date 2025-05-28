import asyncio
import json
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from src.tools import AsyncTool
from src.registry import register_tool

class MapAnalysisResult(BaseModel):
    """地图分析结果"""
    terrain_type: str = Field(description="地形类型")
    elevation_analysis: Dict[str, Any] = Field(description="高程分析")
    key_features: List[str] = Field(description="关键地形特征")
    military_value: Dict[str, str] = Field(description="军事价值评估")
    recommended_routes: List[str] = Field(description="推荐路线")
    tactical_considerations: List[str] = Field(description="战术考量")

@register_tool("military_map_analyzer")
class MilitaryMapAnalyzer(AsyncTool):
    """
    军事地图分析工具
    
    功能：
    1. 分析地形地貌特征
    2. 评估地形军事价值
    3. 识别关键地形要点
    4. 推荐行进路线
    5. 提供战术建议
    """
    
    name = "military_map_analyzer"
    description = "分析军事地图，评估地形特征和军事价值，提供战术建议"
    parameters = {
        "type": "object",
        "properties": {
            "map_data": {
                "type": "string",
                "description": "地图数据或地区描述信息"
            },
            "analysis_type": {
                "type": "string", 
                "description": "分析类型：terrain（地形分析）、tactical（战术分析）、route（路线规划）",
                "enum": ["terrain", "tactical", "route", "comprehensive"],
                "nullable": True
            },
            "mission_type": {
                "type": "string",
                "description": "任务类型：attack（攻击）、defense（防御）、reconnaissance（侦察）、movement（机动）",
                "enum": ["attack", "defense", "reconnaissance", "movement"],
                "nullable": True
            }
        },
        "required": ["map_data"]
    }
    output_type = "object"
    
    def __init__(self):
        super().__init__()
    
    async def forward(
        self, 
        map_data: str,
        analysis_type: Optional[str] = "comprehensive",
        mission_type: Optional[str] = "attack"
    ) -> MapAnalysisResult:
        """
        执行地图分析
        
        Args:
            map_data: 地图数据或地区描述
            analysis_type: 分析类型
            mission_type: 任务类型
        
        Returns:
            MapAnalysisResult: 地图分析结果
        """
        try:
            # 模拟地图分析过程
            await asyncio.sleep(1)  # 模拟分析时间
            
            # 基于输入数据进行分析
            terrain_features = self._analyze_terrain(map_data)
            military_assessment = self._assess_military_value(terrain_features, mission_type)
            routes = self._plan_routes(terrain_features, mission_type)
            tactical_advice = self._generate_tactical_advice(terrain_features, mission_type)
            
            result = MapAnalysisResult(
                terrain_type=terrain_features.get("type", "混合地形"),
                elevation_analysis=terrain_features.get("elevation", {}),
                key_features=terrain_features.get("features", []),
                military_value=military_assessment,
                recommended_routes=routes,
                tactical_considerations=tactical_advice
            )
            
            return result
            
        except Exception as e:
            raise Exception(f"地图分析失败: {str(e)}")
    
    def _analyze_terrain(self, map_data: str) -> Dict[str, Any]:
        """分析地形特征"""
        # 简化的地形分析逻辑
        features = []
        terrain_type = "平原"
        elevation = {"min": 0, "max": 100, "average": 50}
        
        # 基于关键词识别地形特征
        if "山" in map_data or "高地" in map_data:
            terrain_type = "山地"
            features.extend(["制高点", "陡峭坡面", "山谷通道"])
            elevation = {"min": 200, "max": 1500, "average": 800}
        elif "河" in map_data or "水" in map_data:
            features.extend(["河流", "桥梁", "渡口"])
        elif "森林" in map_data or "林" in map_data:
            features.extend(["密林", "林间空地", "隐蔽条件"])
        elif "城市" in map_data or "建筑" in map_data:
            features.extend(["建筑群", "道路网", "制高建筑"])
            
        return {
            "type": terrain_type,
            "features": features,
            "elevation": elevation
        }
    
    def _assess_military_value(self, terrain: Dict[str, Any], mission_type: str) -> Dict[str, str]:
        """评估军事价值"""
        assessment = {}
        
        if mission_type == "attack":
            assessment["进攻价值"] = "中等"
            assessment["掩护条件"] = "良好" if "密林" in terrain.get("features", []) else "一般"
            assessment["机动性"] = "良好" if terrain["type"] == "平原" else "受限"
        elif mission_type == "defense":
            assessment["防御价值"] = "优秀" if "制高点" in terrain.get("features", []) else "一般"
            assessment["观察条件"] = "优秀" if terrain["type"] == "山地" else "良好"
            assessment["火力控制"] = "优秀" if "制高点" in terrain.get("features", []) else "一般"
        
        return assessment
    
    def _plan_routes(self, terrain: Dict[str, Any], mission_type: str) -> List[str]:
        """规划推荐路线"""
        routes = []
        
        if terrain["type"] == "山地":
            routes.extend(["山谷主通道", "侧翼小径", "制高点迂回路线"])
        elif terrain["type"] == "平原":
            routes.extend(["主要道路", "田间小路", "直线突进路线"])
        else:
            routes.extend(["综合路线A", "备选路线B"])
            
        return routes
    
    def _generate_tactical_advice(self, terrain: Dict[str, Any], mission_type: str) -> List[str]:
        """生成战术建议"""
        advice = []
        
        if mission_type == "attack":
            if "制高点" in terrain.get("features", []):
                advice.append("优先占领制高点，控制战场主动权")
            if "河流" in terrain.get("features", []):
                advice.append("注意渡河点安全，确保后续部队通过")
        elif mission_type == "defense":
            if "制高点" in terrain.get("features", []):
                advice.append("在制高点构建主要防御阵地")
            advice.append("利用地形设置交叉火力网")
            
        return advice 