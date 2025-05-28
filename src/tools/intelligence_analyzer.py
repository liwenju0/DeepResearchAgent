import asyncio
import json
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from src.tools import AsyncTool
from src.registry import register_tool

class IntelligenceReport(BaseModel):
    """情报分析报告"""
    enemy_strength: Dict[str, Any] = Field(description="敌方兵力评估")
    threat_level: str = Field(description="威胁等级")
    equipment_analysis: Dict[str, str] = Field(description="装备分析")
    deployment_pattern: List[str] = Field(description="部署模式")
    vulnerabilities: List[str] = Field(description="弱点分析")
    recommendations: List[str] = Field(description="建议措施")

@register_tool("intelligence_analyzer")
class IntelligenceAnalyzer(AsyncTool):
    """
    情报分析工具
    
    功能：
    1. 分析敌方兵力部署
    2. 评估威胁等级
    3. 识别装备能力
    4. 发现战术弱点
    5. 提供应对建议
    """
    
    name = "intelligence_analyzer"
    description = "分析军事情报，评估敌方能力和威胁，提供战术建议"
    parameters = {
        "type": "object",
        "properties": {
            "intelligence_data": {
                "type": "string",
                "description": "情报数据或敌情描述"
            },
            "analysis_focus": {
                "type": "string",
                "description": "分析重点：strength（兵力）、equipment（装备）、deployment（部署）、comprehensive（综合）",
                "enum": ["strength", "equipment", "deployment", "comprehensive"],
                "nullable": True
            },
            "threat_context": {
                "type": "string",
                "description": "威胁背景：immediate（即时威胁）、potential（潜在威胁）、strategic（战略威胁）",
                "enum": ["immediate", "potential", "strategic"],
                "nullable": True
            }
        },
        "required": ["intelligence_data"]
    }
    output_type = "object"
    
    def __init__(self):
        super().__init__()
    
    async def forward(
        self, 
        intelligence_data: str,
        analysis_focus: Optional[str] = "comprehensive",
        threat_context: Optional[str] = "immediate"
    ) -> IntelligenceReport:
        """
        执行情报分析
        
        Args:
            intelligence_data: 情报数据
            analysis_focus: 分析重点
            threat_context: 威胁背景
        
        Returns:
            IntelligenceReport: 情报分析报告
        """
        try:
            # 模拟情报分析过程
            await asyncio.sleep(1.5)  # 模拟分析时间
            
            # 分析敌方兵力
            enemy_strength = self._analyze_enemy_strength(intelligence_data)
            
            # 评估威胁等级
            threat_level = self._assess_threat_level(intelligence_data, threat_context)
            
            # 分析装备能力
            equipment_analysis = self._analyze_equipment(intelligence_data)
            
            # 识别部署模式
            deployment_pattern = self._identify_deployment_pattern(intelligence_data)
            
            # 发现弱点
            vulnerabilities = self._identify_vulnerabilities(intelligence_data)
            
            # 生成建议
            recommendations = self._generate_recommendations(intelligence_data, threat_level)
            
            report = IntelligenceReport(
                enemy_strength=enemy_strength,
                threat_level=threat_level,
                equipment_analysis=equipment_analysis,
                deployment_pattern=deployment_pattern,
                vulnerabilities=vulnerabilities,
                recommendations=recommendations
            )
            
            return report
            
        except Exception as e:
            raise Exception(f"情报分析失败: {str(e)}")
    
    def _analyze_enemy_strength(self, data: str) -> Dict[str, Any]:
        """分析敌方兵力"""
        strength = {
            "personnel": "未知",
            "units": [],
            "command_structure": "常规",
            "readiness_level": "中等"
        }
        
        # 基于关键词分析兵力
        if "师" in data or "旅" in data:
            strength["personnel"] = "5000-15000人"
            strength["units"] = ["装甲部队", "步兵部队", "炮兵支援"]
        elif "营" in data or "连" in data:
            strength["personnel"] = "100-1000人"
            strength["units"] = ["步兵", "支援部队"]
        
        if "精锐" in data or "特种" in data:
            strength["readiness_level"] = "高"
        elif "预备役" in data or "民兵" in data:
            strength["readiness_level"] = "低"
            
        return strength
    
    def _assess_threat_level(self, data: str, context: str) -> str:
        """评估威胁等级"""
        if "重型装备" in data or "导弹" in data or "坦克" in data:
            return "高威胁"
        elif "轻武器" in data or "步兵" in data:
            return "中等威胁"
        else:
            return "低威胁"
    
    def _analyze_equipment(self, data: str) -> Dict[str, str]:
        """分析装备能力"""
        equipment = {}
        
        if "坦克" in data:
            equipment["装甲力量"] = "具备重型坦克，火力强大"
        if "火炮" in data:
            equipment["火力支援"] = "配备远程火炮，射程覆盖广"
        if "防空" in data:
            equipment["防空能力"] = "具备防空系统，制空权争夺激烈"
        if "通信" in data:
            equipment["指挥控制"] = "通信系统完善，指挥协调能力强"
            
        return equipment
    
    def _identify_deployment_pattern(self, data: str) -> List[str]:
        """识别部署模式"""
        patterns = []
        
        if "防御" in data:
            patterns.append("防御性部署，重点加强关键阵地")
        if "机动" in data:
            patterns.append("机动部署，保持战术灵活性")
        if "集中" in data:
            patterns.append("兵力集中部署，准备重点突破")
        if "分散" in data:
            patterns.append("分散部署，降低被打击风险")
            
        return patterns if patterns else ["常规部署模式"]
    
    def _identify_vulnerabilities(self, data: str) -> List[str]:
        """识别弱点"""
        vulnerabilities = []
        
        if "补给线" in data:
            vulnerabilities.append("补给线路较长，容易被切断")
        if "通信" in data and "干扰" in data:
            vulnerabilities.append("通信系统可能存在干扰风险")
        if "侧翼" in data:
            vulnerabilities.append("侧翼防护相对薄弱")
        if "夜间" in data:
            vulnerabilities.append("夜间作战能力有限")
            
        return vulnerabilities if vulnerabilities else ["暂未发现明显弱点"]
    
    def _generate_recommendations(self, data: str, threat_level: str) -> List[str]:
        """生成建议措施"""
        recommendations = []
        
        if threat_level == "高威胁":
            recommendations.extend([
                "加强侦察监视，密切关注敌方动向",
                "准备反装甲武器，应对重型装备威胁",
                "制定多套作战方案，确保应对灵活性"
            ])
        elif threat_level == "中等威胁":
            recommendations.extend([
                "保持警戒状态，定期更新情报",
                "加强防御工事建设",
                "准备快速反应部队"
            ])
        else:
            recommendations.extend([
                "维持常规警戒",
                "继续情报收集",
                "保持部队训练水平"
            ])
            
        return recommendations 