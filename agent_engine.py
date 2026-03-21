# 🤖 Agent 决策引擎（本地推理模块）

import json
from datetime import datetime
from typing import Dict, List, Tuple
from personality import Personality

class AgentDecisionEngine:
    """完全本地的 Agent 决策引擎，不依赖 LLM"""
    
    def __init__(self):
        self.decision_history = []  # 决策历史记录
        self.consistency_checks = []  # 一致性检查日志
        
    # =========================
    # 🧠 第1层：快速本地决策
    # =========================
    def quick_decision(self, personality: Personality, question: str, context: str = "") -> Dict:
        """
        基于人格参数进行快速决策（完全本地），不调用 LLM
        这是真正的 Agent 推理，而不是语言模型
        """
        
        # 第1步：提取问题特征
        risk_level = self._analyze_question_risk(question, context)  # 问题本身的风险等级
        
        # 第2步：基于人格做决策（硬逻辑）
        decision = self._personality_driven_decision(personality, risk_level)
        
        # 第3步：计算置信度和权重（根据人格的一致性）
        confidence = self._calculate_confidence(personality, decision, risk_level)
        weight = self._calculate_weight(personality, confidence, risk_level)
        
        # 第4步：评估风险（从人格角度）
        risk_score = self._assess_risk(personality, risk_level, decision)
        
        return {
            "origin": "local_agent",  # 标记这是本地 Agent 的决策
            "personality": personality.name,
            "decision": decision,
            "confidence": confidence,
            "weight": weight,
            "risk_score": risk_score,
            "reasoning": self._generate_local_reasoning(personality, decision, risk_level),
            "timestamp": datetime.now().isoformat()
        }
    
    def _analyze_question_risk(self, question: str, context: str) -> float:
        """
        分析问题本身的风险等级（0=无风险，1=高风险）
        这是 Agent 对问题的理解，而不是 LLM 的理解
        """
        
        # 风险关键词
        high_risk_keywords = {
            "钱": 0.3, "投资": 0.4, "创业": 0.4, "辞职": 0.3, "结婚": 0.2,
            "离婚": 0.3, "生孩子": 0.2, "出国": 0.2, "手术": 0.4, "买房": 0.3,
            "贷款": 0.3, "重大": 0.2, "生命": 0.5, "死亡": 0.5, "背叛": 0.3
        }
        
        medium_risk_keywords = {
            "改变": 0.1, "尝试": 0.1, "挑战": 0.1, "冒险": 0.2, "新": 0.05
        }
        
        question_lower = question.lower()
        risk_score = 0.0
        
        # 扫描关键词
        for keyword, score in high_risk_keywords.items():
            if keyword in question_lower:
                risk_score += score
        
        for keyword, score in medium_risk_keywords.items():
            if keyword in question_lower:
                risk_score += score
        
        # 归一化到 0-1
        return min(risk_score, 1.0)
    
    def _personality_driven_decision(self, personality: Personality, risk_level: float) -> str:
        """
        纯逻辑决策：根据人格参数和问题风险做出决策
        这是真正的 Agent 推理逻辑
        """
        
        # 基于风险偏好和风险等级的决策逻辑
        # 风险偏好高 + 高风险 = 可能做
        # 风险偏好低 + 高风险 = 往往不做
        
        decision_score = personality.risk - risk_level  # 正值偏向"做"，负值偏向"不做"
        
        # 考虑人格中心性（某些人格天生倾向某个决策）
        if personality.name == "蜡笔小新":  # 极度冒险
            decision_score += 0.3  # 加分，更可能"做"
        elif personality.name == "夜神月":  # 聪明冷酷，但有目标导向
            decision_score += 0.1  # 微小倾斜，但主要看风险
        elif personality.name == "炭治郎":  # 道德谨慎
            decision_score -= 0.2  # 减分，更倾向"不做"
        elif personality.name == "章鱼哥":  # 极度消极
            decision_score -= 0.4  # 强烈减分，极其不想做
        
        # 阈值判断：>0.3 = 做，<-0.3 = 不做，否则看情感
        if decision_score > 0.3:
            return "做"
        elif decision_score < -0.3:
            return "不做"
        else:
            # 中间地带：看情感倾向
            return "做" if personality.emotion > 0.5 else "不做"
    
    def _calculate_confidence(self, personality: Personality, decision: str, risk_level: float) -> int:
        """
        计算对决策的置信度（0-10）
        基于人格的理性程度和决策是否符合人格特征
        """
        
        base_confidence = personality.logic * 10  # 理性=置信度基础
        
        # 人格一致性加分
        if (personality.name == "蜡笔小新" and decision == "做") or \
           (personality.name == "章鱼哥" and decision == "不做") or \
           (personality.name == "炭治郎" and decision == "不做") or \
           (personality.name == "夜神月" and decision == "做"):
            base_confidence += 2  # 符合人格特征，置信度更高
        
        # 风险不匹配减分
        if personality.risk < 0.3 and decision == "做" and risk_level > 0.7:
            base_confidence -= 3  # 保守的人冒高风险，置信度低
        
        # 情感波动
        if personality.emotion > 0.5:
            base_confidence *= 0.9  # 情感强的人置信度更波动
        
        return int(min(max(base_confidence, 1), 10))
    
    def _calculate_weight(self, personality: Personality, confidence: int, risk_level: float) -> float:
        """
        计算决策权重（0.1-1.0）
        权重越高说明这个人格的声音越应该被听取
        """
        
        # 基础权重 = 理性程度
        base_weight = 0.3 + personality.logic * 0.7  # 0.3-1.0
        
        # 置信度调整
        weight = base_weight * (confidence / 10)  # 置信度越高，权重越高
        
        # 人格强度调整（个性越强烈，权重越高）
        strong_personality_bonus = abs(personality.risk - 0.5) * 0.2  # 极端人格权重更高
        
        weight += strong_personality_bonus
        weight = min(max(weight, 0.1), 1.0)  # 归一化到 0.1-1.0
        
        return round(weight, 2)
    
    def _assess_risk(self, personality: Personality, risk_level: float, decision: str) -> int:
        """
        从人格角度评估 decision 的风险（0-10）
        不是绝对的风险，而是这个人格如何看待这个决策的风险
        """
        
        # 基础风险 = 问题本身的风险等级 * 10
        base_risk = int(risk_level * 10)
        
        # 人格风险认知修正
        # 高风险偏好的人认为风险更低
        # 低风险偏好的人认为风险更高
        personality_adjustment = int((0.5 - personality.risk) * 5)  # -2.5 到 +2.5
        
        risk_score = base_risk + personality_adjustment
        
        # 如果决策与人格冲突，认为风险更高
        if (personality.name == "蜡笔小新" and decision == "不做") or \
           (personality.name == "章鱼哥" and decision == "做"):
            risk_score += 2  # 违背天性，风险认知增加
        
        # 确保在 1-10 范围内（禁止 5 分！）
        risk_score = max(min(risk_score, 10), 1)
        if risk_score == 5:
            risk_score = 4 if personality.risk < 0.5 else 6  # 打破平衡
        
        return risk_score
    
    def _generate_local_reasoning(self, personality: Personality, decision: str, risk_level: float) -> str:
        """
        生成本地 Agent 的推理过程（不依赖 LLM）
        这是 Agent 自己的思考，而不是 LLM 的回复
        """
        
        reasoning_parts = []
        reasoning_parts.append(f"[{personality.name} 的本地推理过程]")
        reasoning_parts.append(f"1. 问题分析：风险等级 {risk_level:.2f}")
        reasoning_parts.append(f"2. 人格特性：风险偏好 {personality.risk}，理性程度 {personality.logic}")
        
        if personality.name == "蜡笔小新":
            reasoning_parts.append(f"3. 思考：嘿！这看起来很有趣耶！应该{decision}！")
        elif personality.name == "夜神月":
            reasoning_parts.append(f"3. 分析：这是在我的控制范围内的。{decision}是最优解。")
        elif personality.name == "炭治郎":
            reasoning_parts.append(f"3. 考虑：我需要考虑这对别人的影响。{decision}是正确的选择。")
        elif personality.name == "章鱼哥":
            reasoning_parts.append(f"3. 感受：没劲。反正做什么都一样，不如{decision}。")
        
        reasoning_parts.append(f"4. 决策：{decision}")
        
        return "\n".join(reasoning_parts)
    
    # =========================
    # ✅ 一致性检查
    # =========================
    def check_consistency(self, personality: Personality, decision: str, reasoning: str) -> Dict:
        """
        检查人格与决策的一致性（Agent 的自我检查）
        """
        
        check_result = {
            "personality": personality.name,
            "decision": decision,
            "checks_passed": [],
            "checks_failed": [],
            "overall_consistency_score": 0.0
        }
        
        # 检查1：风险偏好与决策的一致性
        if personality.risk > 0.6 and decision == "做":
            check_result["checks_passed"].append("风险偏好与决策匹配（高风险倾向=做）")
        elif personality.risk < 0.4 and decision == "不做":
            check_result["checks_passed"].append("风险偏好与决策匹配（低风险倾向=不做）")
        else:
            if personality.risk > 0.6 and decision == "不做":
                check_result["checks_failed"].append(f"❌ {personality.name} 风险偏好较高但选择了『不做』（可能违背人设）")
            elif personality.risk < 0.4 and decision == "做":
                check_result["checks_failed"].append(f"❌ {personality.name} 风险偏好较低但选择了『做』（可能违背人设）")
        
        # 检查2：人格特有的决策倾向
        personality_checks = {
            "蜡笔小新": ("做", "极度冒险派，应该倾向做"),
            "章鱼哥": ("不做", "虚无消极派，应该倾向不做"),
            "炭治郎": ("不做", "道德谨慎派，应该倾向不做"),
            "夜神月": ("做", "目标导向派，应该倾向做")
        }
        
        expected_decision, reason = personality_checks.get(personality.name, ("做", "未定义"))
        if decision == expected_decision:
            check_result["checks_passed"].append(f"✅ 符合 {personality.name} 的典型特征：{reason}")
        else:
            check_result["checks_failed"].append(f"⚠️ 可能偏离 {personality.name} 的典型特征：{reason}，但选择了『{decision}』")
        
        # 计算一致性评分
        passed = len(check_result["checks_passed"])
        failed = len(check_result["checks_failed"])
        total = passed + failed if (passed + failed) > 0 else 1
        check_result["overall_consistency_score"] = round(passed / total * 100, 1)
        
        self.consistency_checks.append(check_result)
        
        return check_result
    
    # =========================
    # 📊 决策历史和学习
    # =========================
    def save_decision(self, decision_data: Dict):
        """保存决策到历史记录"""
        self.decision_history.append({
            **decision_data,
            "saved_at": datetime.now().isoformat()
        })
    
    def get_decision_stats(self, personality_name: str = None) -> Dict:
        """
        获取决策统计信息（Agent 的自我认知）
        可用于反思和调整
        """
        
        if not self.decision_history:
            return {"total_decisions": 0, "personalities": {}}
        
        stats = {
            "total_decisions": len(self.decision_history),
            "personalities": {},
            "decision_distribution": {"做": 0, "不做": 0}
        }
        
        for record in self.decision_history:
            p_name = record.get("personality", "unknown")
            decision = record.get("decision", "未知")
            
            # 按人格统计
            if p_name not in stats["personalities"]:
                stats["personalities"][p_name] = {
                    "total": 0,
                    "做": 0,
                    "不做": 0,
                    "avg_confidence": 0,
                    "avg_weight": 0
                }
            
            stats["personalities"][p_name]["total"] += 1
            stats["personalities"][p_name][decision] = stats["personalities"][p_name].get(decision, 0) + 1
            stats["personalities"][p_name]["avg_confidence"] += record.get("confidence", 5)
            stats["personalities"][p_name]["avg_weight"] += record.get("weight", 0.5)
            
            # 全局统计
            stats["decision_distribution"][decision] += 1
        
        # 计算平均值
        for p_name in stats["personalities"]:
            total = stats["personalities"][p_name]["total"]
            stats["personalities"][p_name]["avg_confidence"] = round(
                stats["personalities"][p_name]["avg_confidence"] / total, 1
            )
            stats["personalities"][p_name]["avg_weight"] = round(
                stats["personalities"][p_name]["avg_weight"] / total, 2
            )
        
        return stats
    
    def export_history(self, filename: str = "agent_decision_history.json"):
        """导出完整的决策历史"""
        export_data = {
            "exported_at": datetime.now().isoformat(),
            "total_decisions": len(self.decision_history),
            "decision_history": self.decision_history,
            "consistency_checks": self.consistency_checks,
            "statistics": self.get_decision_stats()
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        return f"✅ 决策历史已导出到 {filename}"


# =========================
# 🎯 集成使用示例
# =========================
if __name__ == "__main__":
    from personality import Personality
    
    # 创建 Agent 引擎
    agent = AgentDecisionEngine()
    
    # 创建人格
    personalities = [
        Personality("夜神月", 0.6, 0.3, 1.0, "世界是可控的", "追求最优解", "冷酷"),
        Personality("蜡笔小新", 0.8, 1.0, 0.2, "世界用来开心", "开心就做", "随便"),
        Personality("炭治郎", 0.3, 0.8, 0.6, "善恶分明", "优先道德", "温和"),
        Personality("章鱼哥", 0.1, 0.4, 0.7, "世界无意义", "倾向否定", "讽刺"),
    ]
    
    # 测试问题
    test_question = "我该不该辞职创业？"
    
    print("🤖 本地 Agent 决策演示")
    print("=" * 60)
    
    for personality in personalities:
        # 快速决策（本地，不调用 API）
        decision = agent.quick_decision(personality, test_question)
        
        print(f"\n【{personality.name}】")
        print(f"决策：{decision['decision']}")
        print(f"置信度：{decision['confidence']}/10")
        print(f"权重：{decision['weight']}")
        print(f"风险评分：{decision['risk_score']}/10")
        print(f"\n推理过程：\n{decision['reasoning']}")
        
        # 一致性检查
        consistency = agent.check_consistency(personality, decision['decision'], decision['reasoning'])
        print(f"\n一致性检查：{consistency['overall_consistency_score']}% 通过")
        
        # 保存记录
        agent.save_decision(decision)
    
    # 显示统计信息
    print("\n\n📊 决策统计")
    print("=" * 60)
    stats = agent.get_decision_stats()
    print(f"总决策数：{stats['total_decisions']}")
    print(f"决策分布：{stats['decision_distribution']}")
    
    print("\n✅ 本地 Agent 系统演示完成！")
