import asyncio
import json
import base64
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
from PIL import Image
from pydantic import BaseModel, Field
from src.tools import AsyncTool
from src.models import model_manager
from src.models.base import MessageRole
from src.registry import register_tool
from src.utils.image_utils import encode_image
from src.logger import logger

class ImageMapAnalysisResult(BaseModel):
    """图片地图分析结果"""
    terrain_classification: str = Field(description="地形分类")
    elevation_features: Dict[str, Any] = Field(description="高程特征")
    key_landmarks: List[str] = Field(description="关键地标")
    vegetation_analysis: Dict[str, str] = Field(description="植被分析")
    water_features: List[str] = Field(description="水系特征")
    infrastructure: List[str] = Field(description="基础设施")
    military_assessment: Dict[str, str] = Field(description="军事评估")
    tactical_recommendations: List[str] = Field(description="战术建议")
    visibility_analysis: Dict[str, str] = Field(description="可见性分析")
    movement_corridors: List[str] = Field(description="机动走廊")

@register_tool("military_image_map_analyzer")
class MilitaryImageMapAnalyzer(AsyncTool):
    """
    军事地形图图片分析工具
    
    功能：
    1. 分析地形图图片中的地形地貌特征
    2. 识别关键地形要素和地标
    3. 评估地形的军事价值
    4. 分析植被覆盖和水系分布
    5. 识别基础设施和人工建筑
    6. 提供战术建议和机动路线
    7. 分析可见性和隐蔽条件
    """
    
    name = "military_image_map_analyzer"
    description = "分析军事地形图图片，识别地形特征、评估军事价值并提供战术建议"
    parameters = {
        "type": "object",
        "properties": {
            "image_path": {
                "type": "string",
                "description": "地形图图片文件路径"
            },
            "analysis_focus": {
                "type": "string",
                "description": "分析重点：terrain（地形分析）、tactical（战术分析）、infrastructure（基础设施）、comprehensive（综合分析）",
                "enum": ["terrain", "tactical", "infrastructure", "comprehensive"],
                "nullable": True
            },
            "mission_context": {
                "type": "string",
                "description": "任务背景：offensive（攻击任务）、defensive（防御任务）、reconnaissance（侦察任务）、logistics（后勤任务）",
                "enum": ["offensive", "defensive", "reconnaissance", "logistics"],
                "nullable": True
            },
            "scale_reference": {
                "type": "string",
                "description": "地图比例尺参考信息（如1:50000）",
                "nullable": True
            }
        },
        "required": ["image_path"]
    }
    output_type = "object"
    
    def __init__(self):
        super().__init__()
    
    async def forward(
        self, 
        image_path: str,
        analysis_focus: Optional[str] = "comprehensive",
        mission_context: Optional[str] = "offensive",
        scale_reference: Optional[str] = None
    ) -> ImageMapAnalysisResult:
        """
        执行地形图图片分析
        
        Args:
            image_path: 地形图图片文件路径
            analysis_focus: 分析重点
            mission_context: 任务背景
            scale_reference: 地图比例尺参考
        
        Returns:
            ImageMapAnalysisResult: 图片地图分析结果
        """
        try:
            # 验证图片文件存在
            if not Path(image_path).exists():
                raise FileNotFoundError(f"图片文件不存在: {image_path}")
            
            # 使用AI模型分析图片
            analysis_result = await self._analyze_image_with_ai(
                image_path, analysis_focus, mission_context, scale_reference
            )
            
            # 解析AI分析结果并结构化
            structured_result = self._structure_analysis_result(
                analysis_result, analysis_focus, mission_context
            )
            
            return structured_result
            
        except Exception as e:
            logger.error(f"地形图图片分析失败: {str(e)}")
            raise Exception(f"地形图图片分析失败: {str(e)}")
    
    async def _analyze_image_with_ai(
        self, 
        image_path: str, 
        analysis_focus: str, 
        mission_context: str,
        scale_reference: Optional[str]
    ) -> str:
        """使用AI模型分析地形图图片"""
        
        # 构建分析提示词
        prompt = self._build_analysis_prompt(analysis_focus, mission_context, scale_reference)
        
        # 准备消息内容
        content = [
            {"type": "text", "text": prompt},
            {"type": "image", "image": Image.open(image_path)}
        ]
        
        messages = [
            {
                "role": MessageRole.USER,
                "content": content,
            }
        ]
        
        # 获取模型并进行分析 - 使用默认的视觉模型
        # 优先使用支持视觉的模型，如gpt-4o或claude37-sonnet
        available_models = model_manager.registed_models
        vision_models = ["gpt-4o", "claude37-sonnet", "claude37-sonnet-thinking"]
        
        model = None
        for model_name in vision_models:
            if model_name in available_models:
                model = available_models[model_name]
                break
        
        if model is None:
            # 如果没有找到视觉模型，使用第一个可用模型
            if available_models:
                model = list(available_models.values())[0]
            else:
                raise Exception("没有可用的AI模型")
        
        response = await model(messages=messages)
        
        return response.content
    
    def _build_analysis_prompt(
        self, 
        analysis_focus: str, 
        mission_context: str, 
        scale_reference: Optional[str]
    ) -> str:
        """构建AI分析提示词"""
        
        base_prompt = """
作为军事地形分析专家，请对这张地形图进行详细分析。请从以下方面进行分析：

1. **地形分类**: 识别主要地形类型（山地、丘陵、平原、河谷等）
2. **高程特征**: 分析地形起伏、坡度、制高点等
3. **关键地标**: 识别重要的地形标志和参考点
4. **植被分析**: 分析植被覆盖类型和密度
5. **水系特征**: 识别河流、湖泊、水渠等水体
6. **基础设施**: 识别道路、桥梁、建筑物等人工设施
7. **军事评估**: 评估地形的军事价值和战术意义
8. **战术建议**: 基于地形特点提供战术建议
9. **可见性分析**: 分析观察条件和隐蔽性
10. **机动走廊**: 识别适合部队机动的路线

"""
        
        # 根据分析重点调整提示词
        if analysis_focus == "terrain":
            base_prompt += "\n**重点关注地形地貌特征和自然环境要素。**"
        elif analysis_focus == "tactical":
            base_prompt += "\n**重点关注军事战术价值和作战运用建议。**"
        elif analysis_focus == "infrastructure":
            base_prompt += "\n**重点关注基础设施和人工建筑的识别与评估。**"
        
        # 根据任务背景调整提示词
        if mission_context == "offensive":
            base_prompt += "\n**从攻击作战角度分析，重点关注突击路线和火力支援阵地。**"
        elif mission_context == "defensive":
            base_prompt += "\n**从防御作战角度分析，重点关注防御阵地和阻击要点。**"
        elif mission_context == "reconnaissance":
            base_prompt += "\n**从侦察任务角度分析，重点关注观察哨位和隐蔽接敌路线。**"
        elif mission_context == "logistics":
            base_prompt += "\n**从后勤保障角度分析，重点关注补给路线和集结地域。**"
        
        if scale_reference:
            base_prompt += f"\n**地图比例尺参考: {scale_reference}**"
        
        base_prompt += """

请以JSON格式返回分析结果，包含以下字段：
- terrain_classification: 地形分类
- elevation_features: 高程特征（包含最高点、最低点、平均坡度等）
- key_landmarks: 关键地标列表
- vegetation_analysis: 植被分析（类型、覆盖率等）
- water_features: 水系特征列表
- infrastructure: 基础设施列表
- military_assessment: 军事评估（包含战术价值、优势、劣势等）
- tactical_recommendations: 战术建议列表
- visibility_analysis: 可见性分析（观察条件、隐蔽性等）
- movement_corridors: 机动走廊列表
"""
        
        return base_prompt
    
    def _structure_analysis_result(
        self, 
        ai_result: str, 
        analysis_focus: str, 
        mission_context: str
    ) -> ImageMapAnalysisResult:
        """结构化AI分析结果"""
        
        try:
            # 尝试解析JSON格式的结果
            if ai_result.strip().startswith('{'):
                result_data = json.loads(ai_result)
            else:
                # 如果不是JSON格式，进行文本解析
                result_data = self._parse_text_result(ai_result)
            
            # 确保所有必需字段都存在
            result_data = self._ensure_required_fields(result_data)
            
            return ImageMapAnalysisResult(**result_data)
            
        except Exception as e:
            logger.warning(f"解析AI结果失败，使用默认结构: {str(e)}")
            return self._create_default_result(ai_result, analysis_focus, mission_context)
    
    def _parse_text_result(self, text_result: str) -> Dict[str, Any]:
        """解析文本格式的分析结果"""
        
        # 简化的文本解析逻辑
        result = {
            "terrain_classification": "混合地形",
            "elevation_features": {"description": "地形起伏适中"},
            "key_landmarks": [],
            "vegetation_analysis": {"type": "混合植被", "coverage": "中等"},
            "water_features": [],
            "infrastructure": [],
            "military_assessment": {"tactical_value": "中等", "advantages": "地形多样", "disadvantages": "复杂地形"},
            "tactical_recommendations": [],
            "visibility_analysis": {"observation": "良好", "concealment": "中等"},
            "movement_corridors": []
        }
        
        # 基于关键词提取信息
        text_lower = text_result.lower()
        
        # 地形分类
        if "山地" in text_result or "mountain" in text_lower:
            result["terrain_classification"] = "山地"
        elif "平原" in text_result or "plain" in text_lower:
            result["terrain_classification"] = "平原"
        elif "丘陵" in text_result or "hill" in text_lower:
            result["terrain_classification"] = "丘陵"
        
        # 提取关键信息
        lines = text_result.split('\n')
        for line in lines:
            if "地标" in line or "landmark" in line.lower():
                result["key_landmarks"].append(line.strip())
            elif "道路" in line or "road" in line.lower():
                result["infrastructure"].append(line.strip())
            elif "河流" in line or "river" in line.lower():
                result["water_features"].append(line.strip())
            elif "建议" in line or "recommend" in line.lower():
                result["tactical_recommendations"].append(line.strip())
        
        return result
    
    def _ensure_required_fields(self, result_data: Dict[str, Any]) -> Dict[str, Any]:
        """确保所有必需字段都存在"""
        
        required_fields = {
            "terrain_classification": "未分类地形",
            "elevation_features": {},
            "key_landmarks": [],
            "vegetation_analysis": {},
            "water_features": [],
            "infrastructure": [],
            "military_assessment": {},
            "tactical_recommendations": [],
            "visibility_analysis": {},
            "movement_corridors": []
        }
        
        for field, default_value in required_fields.items():
            if field not in result_data:
                result_data[field] = default_value
        
        return result_data
    
    def _create_default_result(
        self, 
        ai_result: str, 
        analysis_focus: str, 
        mission_context: str
    ) -> ImageMapAnalysisResult:
        """创建默认分析结果"""
        
        return ImageMapAnalysisResult(
            terrain_classification="复合地形",
            elevation_features={"description": "地形特征复杂，需要详细勘察"},
            key_landmarks=["需要进一步识别关键地标"],
            vegetation_analysis={"type": "混合植被", "coverage": "中等密度"},
            water_features=["需要识别水系分布"],
            infrastructure=["需要识别基础设施"],
            military_assessment={
                "tactical_value": "需要详细评估",
                "analysis_focus": analysis_focus,
                "mission_context": mission_context
            },
            tactical_recommendations=["建议进行实地勘察", "制定详细作战计划"],
            visibility_analysis={"observation": "需要评估", "concealment": "需要评估"},
            movement_corridors=["需要规划机动路线"]
        ) 