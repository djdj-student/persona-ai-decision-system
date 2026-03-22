# 🚀 混合决策系统（Agent + LLM）

from typing import Dict, List
from personality import Personality
from agent_engine import AgentDecisionEngine
from agent_reflection import AgentReflectionSystem, AgentDialogueSystem
import json
import re
from datetime import datetime

class HybridDecisionSystem:
    """
    混合决策系统：结合本地 Agent 推理和 LLM 验证
    
    工作流：
    1️⃣ 本地快速决策 (Agent 自己思考)
    2️⃣ LLM 验证和强化 (问大模型确认)
    3️⃣ 多轮反思 (Agent 深入思考)
    4️⃣ 人格对话 (Agent 之间讨论)
    5️⃣ 最终合成 (综合所有决策)
    """
    
    def __init__(self, llm_call_func=None):
        self.agent_engine = AgentDecisionEngine()
        self.reflection_system = AgentReflectionSystem()
        self.dialogue_system = AgentDialogueSystem()
        self.llm_call_func = llm_call_func  # 外部 LLM 调用函数
        self.workflow_logs = []
    
    # =========================
    # 🔄 主工作流
    # =========================
    def full_decision_workflow(self,
                              personalities: List[Personality],
                              question: str,
                              context: str = "",
                              depth: str = "deep",
                              use_llm: bool = True) -> Dict:
        """
        完整的混合决策工作流
        """
        
        # 全局固定深度为 deep，忽略外部传入值
        depth = "deep"

        workflow = {
            "question": question,
            "context": context,
            "depth": depth,
            "timestamp": datetime.now().isoformat(),
            "stages": {}
        }
        
        print(f"\n🚀 启动混合决策系统")
        print(f"问题：{question}")
        print(f"深度：{depth}，使用 LLM：{use_llm}")
        print("=" * 70)
        
        # =========================
        # STAGE 1: 本地快速决策
        # =========================
        print("\n📍 STAGE 1：本地快速决策（各人格独立决策）")
        print("-" * 70)
        
        stage1_decisions = {}
        for personality in personalities:
            local_decision = self.agent_engine.quick_decision(
                personality, question, context
            )
            stage1_decisions[personality.name] = local_decision
            
            print(f"  ✓ {personality.name}：{local_decision['decision']} "
                  f"（信心 {local_decision['confidence']}/10，权重 {local_decision['weight']}）")
        
        workflow["stages"]["1_local_decisions"] = stage1_decisions
        
        # =========================
        # STAGE 2: LLM 验证（如果启用）
        # =========================
        if use_llm and self.llm_call_func:
            print("\n📍 STAGE 2：LLM 验证和强化")
            print("-" * 70)
            
            stage2_validations = {}
            for personality in personalities:
                local_decision = stage1_decisions[personality.name]
                
                # 用本地决策作为 LLM 的"起点"
                validation_result = self._llm_validate_decision(
                    personality, question, local_decision
                )
                stage2_validations[personality.name] = validation_result
                
                if validation_result["validated"]:
                    print(f"  ✓ {personality.name} 的决策通过 LLM 验证")
                else:
                    print(f"  ⚠️ {personality.name} 的决策需要调整：{validation_result['reason']}")
            
            workflow["stages"]["2_llm_validations"] = stage2_validations
        
        # =========================
        # STAGE 3: 多轮反思
        # =========================
        print("\n📍 STAGE 3：多轮深度反思")
        print("-" * 70)
        
        stage3_reflections = {}
        for personality in personalities:
            local_decision = stage1_decisions[personality.name]
            
            reflection = self.reflection_system.multi_round_reflection(
                personality=personality,
                initial_decision=local_decision["decision"],
                question=question,
                risk_level=self.agent_engine._analyze_question_risk(question, context),
                depth=depth,
                local_reasoning=local_decision["reasoning"]
            )
            stage3_reflections[personality.name] = reflection
            
            # 分析反思质量
            analysis = self.reflection_system.analyze_reflection_quality(reflection)
            print(f"  ✓ {personality.name}：{reflection['final_verdict']} "
                  f"（稳定性 {analysis['decision_stability']}，深度 {analysis['thinking_depth']}）")
            print(f"    {analysis['reflection_quality']}")
        
        workflow["stages"]["3_reflections"] = stage3_reflections
        
        # =========================
        # STAGE 4: 人格对话和冲突
        # =========================
        print("\n📍 STAGE 4：人格对话和博弈")
        print("-" * 70)
        
        stage4_dialogues = {}
        for i, p1 in enumerate(personalities):
            for p2 in personalities[i+1:]:
                reflection1 = stage3_reflections[p1.name]
                reflection2 = stage3_reflections[p2.name]
                reasoning1 = self._build_dialogue_reasoning(reflection1)
                reasoning2 = self._build_dialogue_reasoning(reflection2)

                if use_llm and self.llm_call_func:
                    dialogue = self._generate_stage4_dialogue_with_llm(
                        p1,
                        reflection1["final_verdict"],
                        reasoning1,
                        p2,
                        reflection2["final_verdict"],
                        reasoning2,
                        question,
                    )
                else:
                    dialogue = self.dialogue_system.generate_disagreement_dialogue(
                        p1, reflection1["final_verdict"], reasoning1,
                        p2, reflection2["final_verdict"], reasoning2,
                        question=question,
                    )
                
                dialogue_key = f"{p1.name}_vs_{p2.name}"
                stage4_dialogues[dialogue_key] = dialogue
                
                if dialogue["conflict_intensity"] > 0.5:
                    print(f"  ⚔️ {p1.name} vs {p2.name}：强烈冲突（强度 {dialogue['conflict_intensity']:.2f}）")
                else:
                    print(f"  💬 {p1.name} vs {p2.name}：温和讨论（强度 {dialogue['conflict_intensity']:.2f}）")
        
        workflow["stages"]["4_dialogues"] = stage4_dialogues
        
        # =========================
        # STAGE 4.5: 裁判评估系统
        # =========================
        print("\n📍 STAGE 4.5：裁判评估系统（质量评审）")
        print("-" * 70)
        
        stage45_judge = self._judge_all_decisions(
            personalities,
            stage1_decisions,
            stage3_reflections,
        )
        
        workflow["stages"]["4.5_judge"] = stage45_judge
        
        print(f"  🏆 最佳人格：{stage45_judge['best_personality']} "
              f"（综合评分 {stage45_judge['best_personality_score']}/10）")
        print(f"  ❌ 最差人格：{stage45_judge['worst_personality']} "
              f"（理由：{stage45_judge['worst_personality_reason'][:30]}...）")
        
        # =========================
        # STAGE 5: 最终合成
        # =========================
        print("\n📍 STAGE 5：最终决策合成")
        print("-" * 70)
        
        stage5_final = self._synthesize_final_decision(
            personalities,
            stage1_decisions,
            stage3_reflections
        )
        
        workflow["stages"]["5_synthesis"] = stage5_final
        
        print(f"  🏁 最终决策：{stage5_final['final_decision']}")
        print(f"  支持『做』：总权重 {stage5_final['score_do']:.2f}")
        print(f"  支持『不做』：总权重 {stage5_final['score_not']:.2f}")
        print(f"  冲突指数：{stage5_final['conflict_index']:.1f}%")
        
        # =========================
        # 保存工作流
        # =========================
        self.workflow_logs.append(workflow)
        
        print("\n" + "=" * 70)
        print("✅ 混合决策工作流完成！\n")
        
        return workflow
    
    # =========================
    # 🔧 子流程
    # =========================

    def _build_dialogue_reasoning(self, reflection: Dict) -> str:
        """把 Stage 3 反思压缩为可供 Stage 4 使用的思考摘要。"""
        rounds = reflection.get("rounds", [])
        points = []

        for r in rounds:
            for item in r.get("potential_issues", []):
                points.append(str(item))
            for item in r.get("analysis", []):
                points.append(str(item))
            for item in r.get("failure_simulation", []):
                points.append(str(item))
            for item in r.get("mitigation", []):
                points.append(str(item))

        thought_process = []
        for r in rounds:
            for item in r.get("thought_process", []):
                thought_process.append(str(item))

        compact_points = "；".join(points[:4])
        compact_thought = "；".join(thought_process[:2])

        return (
            f"初始={reflection.get('initial_decision', '')}；"
            f"终局={reflection.get('final_verdict', '')}；"
            f"思考={compact_thought or '无'}；"
            f"证据={compact_points or '无'}"
        )

    def _generate_stage4_dialogue_with_llm(self,
                                           p1: Personality,
                                           d1: str,
                                           r1: str,
                                           p2: Personality,
                                           d2: str,
                                           r2: str,
                                           question: str) -> Dict:
        """Stage 4 优先使用 LLM 生成人格对话，避免固定模板化表达。"""

        prompt = f"""
你现在要生成两个人格的一对一辩论，禁止模板句，必须像角色本人说话。

角色A：
- 名字：{p1.name}
- 风险偏好：{p1.risk}
- 情绪强度：{p1.emotion}
- 理性程度：{p1.logic}
- 世界观：{p1.worldview}
- 决策方式：{p1.decision_style}
- 语言风格：{p1.tone}
- 当前结论：{d1}
- 思考线索：{r1}

角色B：
- 名字：{p2.name}
- 风险偏好：{p2.risk}
- 情绪强度：{p2.emotion}
- 理性程度：{p2.logic}
- 世界观：{p2.worldview}
- 决策方式：{p2.decision_style}
- 语言风格：{p2.tone}
- 当前结论：{d2}
- 思考线索：{r2}

任务要求：
1. 生成3轮对话：A立场陈述 -> B反驳 -> A强硬回应。
2. 每轮必须有“思考痕迹”，体现该角色如何从线索得出当前句子。
3. A对B的强硬回应必须针对B本轮内容，不能复述A第一轮。
4. 必须围绕用户原问题展开，不能跑题；每轮至少提到一次问题核心（例如“辞职/创业”等关键词）。
4. 禁止出现“作为AI/综合来看/首先其次最后/建议你”等模板化表达。
5. 语言要自然、有情绪，不要报告体。

用户原问题：{question}

仅输出严格JSON，不要任何额外说明：
{{
  "exchanges": [
    {{"speaker":"{p1.name}", "type":"argument", "content":"..."}},
    {{"speaker":"{p2.name}", "type":"counter_argument", "content":"..."}},
    {{"speaker":"{p1.name}", "type":"rebuttal", "content":"..."}}
  ]
}}
"""

        try:
            resp = (self.llm_call_func(prompt) or "").strip()
            text = resp

            # 清理可能的 markdown code fence
            if text.startswith("```"):
                lines = text.splitlines()
                if len(lines) >= 3:
                    text = "\n".join(lines[1:-1]).strip()

            data = json.loads(text)
            raw_exchanges = data.get("exchanges", [])

            exchanges = []
            for item in raw_exchanges[:3]:
                speaker = item.get("speaker", "")
                etype = item.get("type", "")
                content = str(item.get("content", "")).strip()

                if not content:
                    continue

                if etype == "argument":
                    exchanges.append({"speaker": speaker, "position": d1 if speaker == p1.name else d2, "argument": content})
                elif etype == "counter_argument":
                    exchanges.append({"speaker": speaker, "counter_to": p1.name if speaker == p2.name else p2.name, "position": d2 if speaker == p2.name else d1, "counter_argument": content})
                elif etype == "rebuttal":
                    exchanges.append({"speaker": speaker, "position": d1 if speaker == p1.name else d2, "rebuttal": content})

            if len(exchanges) < 3:
                raise ValueError("LLM 对话结构不足")

            conflict_intensity = abs(p1.risk - p2.risk) * 0.5
            if d1 != d2:
                conflict_intensity += 0.5

            return {
                "participants": [p1.name, p2.name],
                "stance": [d1, d2],
                "exchanges": exchanges,
                "conflict_intensity": min(conflict_intensity, 1.0),
                "origin": "llm"
            }
        except Exception:
            # 兜底回退：LLM 失败时使用本地生成，保证流程不中断
            return self.dialogue_system.generate_disagreement_dialogue(
                p1, d1, r1, p2, d2, r2, question=question
            )
    
    def _llm_validate_decision(self, personality: Personality, question: str, local_decision: Dict) -> Dict:
        """
        使用 LLM 验证本地决策
        LLM 的作用是"验证和强化"，而不是"独立决策"
        """
        
        if not self.llm_call_func:
            return {"validated": True, "reason": "无 LLM 可用"}
        
        # 构建验证提示词
        validation_prompt = f"""
你是 {personality.name} 的思维验证者。

本地 Agent 给出的决策是：{local_decision['decision']}
置信度：{local_decision['confidence']}/10
理由摘要：{local_decision['reasoning'][:200]}

问题：{question}

请评估这个决策是否：
1. 符合 {personality.name} 的人格特征？
2. 逻辑是否自洽？
3. 是否有明显的漏洞？

请严格按以下格式输出：
【结论】验证通过 / 需要调整
【人格特征符合度】一句话
【逻辑一致性】一句话
【漏洞】一句话（若无写“无明显漏洞”）
【调整建议】一句话（若无需调整写“保持当前决策”）

要求：总长度控制在220字以内，避免冗长。
"""
        
        try:
            response = self.llm_call_func(validation_prompt)
            text = (response or "").strip()

            # 更稳的结论解析：优先读【结论】字段，其次关键词兜底
            verdict_match = re.search(r"【结论】\s*(验证通过|需要调整)", text)
            if verdict_match:
                validated = verdict_match.group(1) == "验证通过"
            else:
                validated = ("验证通过" in text) and ("需要调整" not in text)

            # 不再截断 reason，避免出现“半句断掉”的体验
            reason = text

            return {
                "validated": validated,
                "reason": reason,
                "full_response": text
            }
        except Exception as e:
            return {
                "validated": True,
                "reason": f"LLM 调用失败：{str(e)[:50]}",
                "error": str(e)
            }
    
    def _synthesize_final_decision(self,
                                   personalities: List[Personality],
                                   stage1: Dict,
                                   stage3: Dict) -> Dict:
        """
        综合所有决策得到最终结论
        """
        
        synthesis = {
            "decision_breakdown": {},
            "score_do": 0,
            "score_not": 0,
            "conflict_index": 0,
            "final_decision": "未定",
            "confidence": 0,
            "recommendation": ""
        }
        
        total_weight = 0
        conflicting_votes = 0
        
        for personality in personalities:
            local_decision = stage1[personality.name]
            reflection = stage3[personality.name]
            
            # 最终决策 = 反思后的决策
            final_decision = reflection["final_verdict"]
            weight = local_decision["weight"]
            confidence = local_decision["confidence"]
            
            synthesis["decision_breakdown"][personality.name] = {
                "decision": final_decision,
                "weight": weight,
                "confidence": confidence
            }
            
            total_weight += weight
            
            # 加权投票
            if final_decision == "做":
                synthesis["score_do"] += weight * (confidence / 10)
            else:
                synthesis["score_not"] += weight * (confidence / 10)
        
        # 计算冲突指数
        if total_weight > 0:
            do_proportion = synthesis["score_do"] / total_weight if total_weight > 0 else 0
            not_proportion = synthesis["score_not"] / total_weight if total_weight > 0 else 0
            
            # 冲突指数 = 两方差异程度（0% = 完全一致，100% = 完全分裂）
            synthesis["conflict_index"] = abs(do_proportion - not_proportion) * 100
        
        # 最终决策
        if synthesis["score_do"] > synthesis["score_not"]:
            synthesis["final_decision"] = "做"
        elif synthesis["score_not"] > synthesis["score_do"]:
            synthesis["final_decision"] = "不做"
        else:
            synthesis["final_decision"] = "平衡"
        
        # 推荐文本
        if synthesis["conflict_index"] > 80:
            synthesis["recommendation"] = "⚠️ 各方意见差异很大，需要谨慎考虑"
        elif synthesis["conflict_index"] > 50:
            synthesis["recommendation"] = "💭 存在不同观点，建议多角度考虑"
        else:
            synthesis["recommendation"] = "✓ 多方观点较为一致"
        
        return synthesis
    
    # =========================
    # 🏆 裁判评估系统
    # =========================
    
    def _judge_all_decisions(self,
                            personalities: List[Personality],
                            stage1: Dict,
                            stage3: Dict) -> Dict:
        """
        STAGE 4.5 裁判系统：评估所有人格的决策质量
        
        职责：
        1. 评估逻辑自洽性
        2. 评估风险判断合理性
        3. 选出最佳人格（逻辑清晰、风险控制好）
        4. 选出最差人格（逻辑漏洞、过于极端）
        5. 给出综合评分
        """
        
        judge_result = {
            "best_personality": "",
            "best_personality_score": 0,
            "worst_personality": "",
            "worst_personality_reason": "",
            "personality_evaluations": {},
            "vote_summary": {"做": [], "不做": []},
            "recommendation": ""
        }
        
        # 第1步：提取每个人格的核心观点和评分
        for personality in personalities:
            local_decision = stage1[personality.name]
            reflection = stage3[personality.name]
            
            # 收集数据
            final_decision = reflection["final_verdict"]
            confidence = local_decision["confidence"]
            risk = local_decision.get("risk_score", 5)
            
            # 评估维度
            evaluation = {
                "name": personality.name,
                "decision": final_decision,
                "confidence": confidence,
                "risk_score": risk,
                "logic_consistency": self._evaluate_logic_consistency(personality, reflection),
                "realism": self._evaluate_realism(personality, local_decision),
                "bias_level": self._evaluate_bias(personality)
            }
            
            # 综合评分 (0-10)
            # 逻辑一致性 (0-3) + 现实性 (0-3) + 低偏见程度 (0-3) + 信心稳定性 (0-1)
            composite_score = (
                evaluation["logic_consistency"] * 3 +
                evaluation["realism"] * 3 +
                (1 - evaluation["bias_level"]) * 3 +
                min(confidence / 10, 1.0)
            )
            
            evaluation["composite_score"] = round(composite_score, 2)
            judge_result["personality_evaluations"][personality.name] = evaluation
            
            # 投票统计
            judge_result["vote_summary"][final_decision].append(personality.name)
        
        # 第2步：选出最佳和最差人格
        evaluations = judge_result["personality_evaluations"]
        
        # 最佳人格 = 综合评分最高
        best = max(evaluations.items(), key=lambda x: x[1]["composite_score"])
        judge_result["best_personality"] = best[0]
        judge_result["best_personality_score"] = best[1]["composite_score"]
        
        # 最差人格 = 综合评分最低
        worst = min(evaluations.items(), key=lambda x: x[1]["composite_score"])
        judge_result["worst_personality"] = worst[0]
        
        # 最差原因
        worst_eval = worst[1]
        if worst_eval["logic_consistency"] < 0.3:
            reason = "逻辑漏洞明显"
        elif worst_eval["bias_level"] > 0.8:
            reason = "极端偏见"
        elif worst_eval["realism"] < 0.3:
            reason = "决策不现实"
        else:
            reason = "综合评分最低"
        
        judge_result["worst_personality_reason"] = reason
        
        # 第3步：建议
        vote_do = len(judge_result["vote_summary"]["做"])
        vote_not = len(judge_result["vote_summary"]["不做"])
        
        if vote_do > vote_not:
            judge_result["recommendation"] = f"✓ 多数倾向『做』（{vote_do}:{vote_not}），最佳决策来自 {judge_result['best_personality']}"
        elif vote_not > vote_do:
            judge_result["recommendation"] = f"✓ 多数倾向『不做』（{vote_not}:{vote_do}），最佳决策来自 {judge_result['best_personality']}"
        else:
            judge_result["recommendation"] = f"⚠️ 意见分裂（{vote_do}:{vote_not}），建议采纳 {judge_result['best_personality']} 的观点"
        
        return judge_result
    
    def _evaluate_logic_consistency(self, personality: Personality, reflection: Dict) -> float:
        """评估逻辑自洽性 (0-1)"""
        # 检查是否改变了决策（不改变 = 更一致）
        initial = reflection.get("initial_decision", "未知")
        final = reflection.get("final_verdict", "未知")
        
        if initial == final:
            consistency = 0.9  # 保持一致
        else:
            # 检查是否有理由变更
            rounds = reflection.get("rounds", [])
            if len(rounds) > 1 and rounds[-1].get("analysis"):
                consistency = 0.7  # 有理由的改变
            else:
                consistency = 0.4  # 随意改变
        
        return consistency
    
    def _evaluate_realism(self, personality: Personality, decision: Dict) -> float:
        """评估决策现实性 (0-1)"""
        # 高风险但有理由 = 现实
        # 低风险但说法幼稚 = 不现实
        
        risk = decision.get("risk_score", 5)
        reasoning = decision.get("reasoning", "")
        
        # 如果reasoning超过50字 = 考虑周全
        if len(reasoning) > 50:
            realism = min(1.0, (risk + 5) / 10)  # 越高风险越现实
        else:
            realism = max(0.2, (risk - 3) / 10)  # 理由不充分
        
        return realism
    
    def _evaluate_bias(self, personality: Personality) -> float:
        """评估人格偏见程度 (0-1) 越高越有偏见"""
        # 情绪越强，偏见越大
        emotion = personality.emotion
        # 理性越低，偏见越大
        logic = personality.logic
        
        bias = (emotion * 0.6 + (1 - logic) * 0.4)
        return min(1.0, bias)
    
    # =========================
    # 📊 决策合成（原有）
    # =========================
    
    def export_workflow_report(self, workflow_index: int = -1, filename: str = None) -> str:
        """导出工作流报告"""
        
        if not self.workflow_logs:
            return "❌ 没有工作流记录"
        
        workflow = self.workflow_logs[workflow_index]
        
        if not filename:
            timestamp = workflow["timestamp"].replace(":", "-")
            filename = f"workflow_report_{timestamp}.json"
        
        report = {
            "workflow": workflow,
            "agent_statistics": self.agent_engine.get_decision_stats(),
            "reflection_quality": [
                self.reflection_system.analyze_reflection_quality(r)
                for r in workflow["stages"].get("3_reflections", {}).values()
                if isinstance(r, dict)
            ]
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        return f"✅ 工作流报告已导出：{filename}"


# =========================
# 🎯 集成使用示例
# =========================
if __name__ == "__main__":
    from personality import Personality
    
    # 创建混合系统（不使用 LLM）
    hybrid_system = HybridDecisionSystem(llm_call_func=None)
    
    # 创建人格
    personalities = [
        Personality("夜神月", 0.6, 0.3, 1.0, "世界是可控的", "追求最优解", "冷酷"),
        Personality("蜡笔小新", 0.8, 1.0, 0.2, "世界用来开心", "开心就做", "随便"),
        Personality("炭治郎", 0.3, 0.8, 0.6, "善恶分明", "优先道德", "温和"),
        Personality("章鱼哥", 0.1, 0.4, 0.7, "世界无意义", "倾向否定", "讽刺"),
    ]
    
    # 运行工作流
    workflow = hybrid_system.full_decision_workflow(
        personalities=personalities,
        question="我该不该辞职创业？",
        depth="deep",
        use_llm=False
    )
    
    # 导出报告
    report_file = hybrid_system.export_workflow_report()
    print(report_file)
    
    print("✅ 混合决策系统演示完成！")
