# 🧠 Agent 反思系统（多轮深度思考）

import json
import random
import re
from datetime import datetime
from typing import Dict, List
from personality import Personality

class AgentReflectionSystem:
    """
    Agent 的反思系统：
    - 对决策进行多轮思考
    - 发现逻辑漏洞
    - 生成深度分析
    - 调整策略
    """
    
    def __init__(self):
        self.reflection_logs = []
        self.depth_levels = {
            "quick": 1,      # 快速：仅 Round 1（质疑）
            "standard": 2,   # 标准：Round 1 + Round 2
            "deep": 3,       # 深度：Round 1 + Round 2 + Round 3
            "expert": 4      # 专家：在 deep 基础上增加 Round 4（预演失败）
        }
    
    # =========================
    # 🔄 多轮反思引擎
    # =========================
    def multi_round_reflection(self, 
                               personality: Personality,
                               initial_decision: str,
                               question: str,
                               risk_level: float,
                               depth: str = "standard",
                               local_reasoning: str = "") -> Dict:
        """
        多轮反思过程（不依赖 LLM 的纯本地思考）
        ROUND 0：初始决策（已做）
        ROUND 1：反思初始决策的逻辑
        ROUND 2+：深度思考
        """
        
        num_rounds = self.depth_levels.get(depth, 2)
        
        reflection_data = {
            "personality": personality.name,
            "question": question,
            "initial_decision": initial_decision,
            "depth": depth,
            "rounds": [],
            "final_verdict": initial_decision,
            "confidence_evolution": []
        }
        
        current_decision = initial_decision
        current_confidence = 7  # 初始置信度
        
        reflection_data["confidence_evolution"].append(current_confidence)
        
        # 第 1 轮反思：质疑初始决策
        round_1 = self._reflection_round_1_questioning(
            personality, current_decision, question, risk_level
        )
        reflection_data["rounds"].append(round_1)
        
        # 检查第 1 轮是否改变了决策
        if round_1["recommendation"] != current_decision:
            current_decision = round_1["recommendation"]
            current_confidence = round_1["confidence_shift"]
            reflection_data["final_verdict"] = current_decision
        
        reflection_data["confidence_evolution"].append(current_confidence)
        
        # 第 2 轮反思（如果需要）
        if num_rounds >= 2:
            round_2 = self._reflection_round_2_deepdive(
                personality, current_decision, question, risk_level, round_1, local_reasoning
            )
            reflection_data["rounds"].append(round_2)
            
            if round_2["recommendation"] != current_decision:
                current_decision = round_2["recommendation"]
                current_confidence = round_2["confidence_shift"]
                reflection_data["final_verdict"] = current_decision
            else:
                # 如果决策未改变，置信度可能有微调
                current_confidence = round_2.get("confidence_shift", current_confidence)
            
            reflection_data["confidence_evolution"].append(current_confidence)
        
        # 第 3 轮反思（如果需要）
        if num_rounds >= 3:
            round_3 = self._reflection_round_3_devils_advocate(
                personality, current_decision, question, round_1, round_2
            )
            reflection_data["rounds"].append(round_3)
            
            if round_3["recommendation"] != current_decision:
                current_decision = round_3["recommendation"]
                current_confidence = round_3["confidence_shift"]
                reflection_data["final_verdict"] = current_decision
            else:
                # 如果决策未改变，置信度可能有微调
                current_confidence = round_3.get("confidence_shift", current_confidence)
            
            reflection_data["confidence_evolution"].append(current_confidence)

        # 第 4 轮反思（expert 专属）
        if num_rounds >= 4:
            round_4 = self._reflection_round_4_pre_mortem(
                personality, current_decision, question, risk_level
            )
            reflection_data["rounds"].append(round_4)

            if round_4["recommendation"] != current_decision:
                current_decision = round_4["recommendation"]
                current_confidence = round_4["confidence_shift"]
                reflection_data["final_verdict"] = current_decision
            else:
                current_confidence = round_4.get("confidence_shift", current_confidence)

            reflection_data["confidence_evolution"].append(current_confidence)
        
        self.reflection_logs.append(reflection_data)
        
        return reflection_data
    
    def _reflection_round_1_questioning(self,
                                        personality: Personality,
                                        current_decision: str,
                                        question: str,
                                        risk_level: float) -> Dict:
        """
        第一轮反思：质疑初始决策
        Agent 问自己：这个决策真的对吗？
        """
        
        round_info = {
            "round": 1,
            "type": "质疑初始决策",
            "thought_process": [],
            "potential_issues": [],
            "recommendation": current_decision,
            "confidence_shift": 7,
            "change_reason": ""
        }
        
        # 基于人格的自我质疑
        if personality.name == "蜡笔小新":
            round_info["thought_process"].append("我真的想清楚了吗？还是只是一时冲动？")
            
            # 检查是否过于冲动
            if current_decision == "做" and risk_level > 0.7:
                round_info["potential_issues"].append("⚠️ 可能过于冲动，没有考虑后果")
                round_info["recommendation"] = "做"  # 但仍然选择做
                round_info["confidence_shift"] = 5  # 置信度下降
                round_info["change_reason"] = "确认了冲动，但这就是我啊！"
        
        elif personality.name == "夜神月":
            round_info["thought_process"].append("这个决策是否符合我的长期目标？")
            
            # 检查是否真的是"最优解"
            if current_decision == "做":
                round_info["potential_issues"].append("✓ 当前决策符合目标导向")
                round_info["confidence_shift"] = 9
        
        elif personality.name == "炭治郎":
            round_info["thought_process"].append("这个决策会伤害别人吗？")
            
            # 检查道德性
            if current_decision == "做":
                round_info["potential_issues"].append("⚠️ 需要确保不会伤害他人")
                round_info["confidence_shift"] = 6
            else:
                round_info["potential_issues"].append("✓ 这个选择是负责任的")
                round_info["confidence_shift"] = 8
        
        elif personality.name == "章鱼哥":
            round_info["thought_process"].append("为什么我要费这个劲？反正都一样...")
            
            # 更加消极
            if current_decision == "做":
                round_info["potential_issues"].append("⚠️ 为什么不直接『不做』呢？")
                round_info["recommendation"] = "不做"
                round_info["change_reason"] = "一切都没意义，还是省劲吧"
                round_info["confidence_shift"] = 3
            else:
                round_info["confidence_shift"] = 8
        
        return round_info
    
    def _reflection_round_2_deepdive(self,
                                     personality: Personality,
                                     current_decision: str,
                                     question: str,
                                     risk_level: float,
                                     round_1_result: Dict,
                                     local_reasoning: str = "") -> Dict:
        """
        第二轮反思：深入分析决策
        Agent 考虑更多维度
        """
        
        round_info = {
            "round": 2,
            "type": "深入分析",
            "critical_questions": [],
            "analysis": [],
            "recommendation": current_decision,
            "confidence_shift": 5,
            "change_reason": ""
        }
        
        # 通用的深入分析
        round_info["critical_questions"] = [
            "已有的信息是否足够？",
            "是否考虑了最坏情况？",
            "是否有其他合理的选择？",
            "决策的短期和长期影响是什么？"
        ]

        if local_reasoning:
            # 将 Stage 1 的本地推理纳入二轮复盘，增强本地模式下的反思质量
            round_info["analysis"].append(f"初始推理复盘：{local_reasoning[:120]}")
        
        # 人格特定的深入分析
        if personality.name == "蜡笔小新":
            round_info["analysis"].append(f"短期快乐指数：高（『{current_decision}』能让我开心）")
            round_info["analysis"].append("长期后果评估：不太想考虑...")
            round_info["confidence_shift"] = 4  # 没有深思，置信度下降
        elif personality.name == "夜神月":
            # 冷酷分析成本效益
            if current_decision == "做":
                round_info["analysis"].append("收益：获得目标，提升地位")
                round_info["analysis"].append("成本：可能的反律")
                round_info["analysis"].append("评估：值得")
            else:
                round_info["analysis"].append("这样的『不做』不符合我的风格")
                round_info["recommendation"] = "做"
                round_info["confidence_shift"] = 9
        
        elif personality.name == "炭治郎":
            # 道德审视
            round_info["analysis"].append("这个决策是否符合我的价值观？")
            if current_decision == "不做":
                round_info["analysis"].append("✓ 这是正确的选择")
                round_info["confidence_shift"] = 9
            else:
                round_info["analysis"].append("⚠️ 需要确保这是有道德的")
                round_info["confidence_shift"] = 6
        
        elif personality.name == "章鱼哥":
            # 虚无分析
            round_info["analysis"].append("实际上，做和不做对世界的影响都很小...")
            round_info["analysis"].append("那我就选择做吧...不，还是不做吧...")
            round_info["confidence_shift"] = 3  # 极其失信心，但不至于都是一样
        
        return round_info

    def _reflection_round_4_pre_mortem(self,
                                       personality: Personality,
                                       current_decision: str,
                                       question: str,
                                       risk_level: float) -> Dict:
        """
        第四轮反思：预演失败（Pre-mortem）
        假设当前决策失败，倒推失败原因，再决定是否坚持。
        """

        opposite_decision = "不做" if current_decision == "做" else "做"

        round_info = {
            "round": 4,
            "type": "预演失败",
            "failure_simulation": [],
            "mitigation": [],
            "recommendation": current_decision,
            "confidence_shift": 6,
            "change_reason": ""
        }

        round_info["failure_simulation"].append(f"假设『{current_decision}』失败，最可能的触发点是什么？")
        round_info["failure_simulation"].append("是否高估了自己对风险的控制能力？")

        if personality.name == "夜神月":
            round_info["mitigation"].append("为关键步骤设置替代路径，避免单点失败")
            round_info["mitigation"].append("保留对手行为预案，降低不可控变量")
            round_info["confidence_shift"] = 9

        elif personality.name == "蜡笔小新":
            round_info["mitigation"].append("先做小规模试错，避免一次性投入过大")
            if risk_level > 0.85 and current_decision == "做":
                round_info["recommendation"] = opposite_decision
                round_info["change_reason"] = "玩归玩，风险爆表时先别硬冲"
                round_info["confidence_shift"] = 5
            else:
                round_info["confidence_shift"] = 7

        elif personality.name == "炭治郎":
            round_info["mitigation"].append("确认是否会伤害他人，必要时调整执行方式")
            round_info["mitigation"].append("加入可回退机制，避免不可逆后果")
            round_info["confidence_shift"] = 8

        elif personality.name == "章鱼哥":
            round_info["mitigation"].append("减少投入，降低情绪和资源损耗")
            if current_decision == "做":
                round_info["recommendation"] = "不做"
                round_info["change_reason"] = "预演结果太麻烦，不值得"
            round_info["confidence_shift"] = 2

        return round_info
    
    def _reflection_round_3_devils_advocate(self,
                                            personality: Personality,
                                            current_decision: str,
                                            question: str,
                                            round_1: Dict,
                                            round_2: Dict) -> Dict:
        """
        第三轮反思：魔鬼代言人模式
        Agent 用对立的观点攻击自己的决策
        """
        
        round_info = {
            "round": 3,
            "type": "自我批判",
            "opposing_view": "",
            "counter_argument": "",
            "final_defense": "",
            "recommendation": current_decision,
            "confidence_shift": 6,
            "change_reason": ""
        }
        
        if current_decision == "做":
            round_info["opposing_view"] = "你为什么要『做』？这太危险了！"
        else:
            round_info["opposing_view"] = "你为什么不『做』？太保守了！"
        
        # 人格特定的自我批判
        if personality.name == "蜡笔小新":
            if current_decision == "做":
                round_info["counter_argument"] = "你真的准备好后果了吗？会不会很麻烦？"
                round_info["final_defense"] = "那又怎样？人生就是要开心！"
                round_info["confidence_shift"] = 6
        
        elif personality.name == "夜神月":
            round_info["counter_argument"] = "即使是最优解，也有风险啊！"
            round_info["final_defense"] = "我对自己的能力有信心。就这么做。"
            round_info["confidence_shift"] = 9
        
        elif personality.name == "炭治郎":
            if current_decision == "不做":
                round_info["counter_argument"] = "你是不是太瞻前顾后了？"
                round_info["final_defense"] = "谨慎行动对得起我的良心。"
                round_info["confidence_shift"] = 8
        
        elif personality.name == "章鱼哥":
            round_info["counter_argument"] = "你说什么都没意义，那为什么还要纠结？"
            round_info["final_defense"] = "你说得对...反正都一样..."
            round_info["confidence_shift"] = 1
        
        return round_info
    
    # =========================
    # 📊 反思分析
    # =========================
    def analyze_reflection_quality(self, reflection_data: Dict) -> Dict:
        """
        分析反思的质量
        """
        
        analysis = {
            "reflection_quality": "优秀",
            "decision_stability": 0.0,
            "thinking_depth": 0,
            "insights": []
        }
        
        # 计算决策稳定性（越多轮都成一样的决策，稳定性越高）
        decisions_in_rounds = [reflection_data["initial_decision"]] + \
                             [round["recommendation"] for round in reflection_data["rounds"]]
        final_decision_count = decisions_in_rounds.count(reflection_data["final_verdict"])
        analysis["decision_stability"] = round(final_decision_count / len(decisions_in_rounds), 2)
        
        # 思考深度 = 轮数 + 指出的问题数
        analysis["thinking_depth"] = len(reflection_data["rounds"]) + \
                                     sum(len(r.get("potential_issues", [])) for r in reflection_data["rounds"])
        
        # 置信度变化分析
        confidence_changes = []
        for i in range(1, len(reflection_data["confidence_evolution"])):
            change = reflection_data["confidence_evolution"][i] - reflection_data["confidence_evolution"][i-1]
            if change != 0:
                confidence_changes.append(change)
        
        if confidence_changes:
            avg_change = sum(confidence_changes) / len(confidence_changes)
            analysis["insights"].append(f"平均置信度变化：{avg_change:.1f}")
        
        # 决策品质判断
        if analysis["decision_stability"] > 0.75:
            analysis["reflection_quality"] = "✓ 优秀（决策稳定，思考深入）"
        elif analysis["decision_stability"] > 0.5:
            analysis["reflection_quality"] = "⚠️ 良好（决策有所摇摆，但合理）"
        else:
            analysis["reflection_quality"] = "❌ 不理想（决策极不稳定，可能缺乏逻辑）"
        
        return analysis


class AgentDialogueSystem:
    """
    Agent 之间的对话系统
    多个 Agent 进行讨论和辩论
    """
    
    def __init__(self):
        self.dialogue_history = []
        self._last_variant_index = {}

    def _choose_from_pool(self, key: str, options: List[str]) -> str:
        """从候选句池随机取一条，并尽量避免与上次同key重复。"""
        if not options:
            return ""
        if len(options) == 1:
            self._last_variant_index[key] = 0
            return options[0]

        last_idx = self._last_variant_index.get(key, -1)
        idx = random.randrange(len(options))
        if idx == last_idx:
            idx = (idx + 1) % len(options)

        self._last_variant_index[key] = idx
        return options[idx]

    def _line_variant(self,
                      speaker: Personality,
                      opponent: Personality,
                      phase: str,
                      core_line: str,
                      channel: str) -> str:
        """给核心句套上2-3个口语变体壳，避免同分支复读。"""
        if not core_line:
            return ""

        key = f"{speaker.name}:{opponent.name}:{phase}:{channel}"

        prefix_pool = {
            "argument": ["先把话挑明：", "我先把核心掰开说：", "我直说重点："],
            "counter": ["我就抓你这点说：", "你这句我得正面回：", "先反打你这个逻辑："],
            "rebuttal": ["我再补一刀：", "我把结论钉死：", "最后我就说透："],
        }

        suffix_pool = {
            "argument": ["这不是情绪，这是判断。", "这一条我不会让步。", "这句你得听进去。"],
            "counter": ["这就是你的漏洞。", "这点你绕不过去。", "你要反驳先补这块。"],
            "rebuttal": ["我的立场不会变。", "这个结论我继续扛。", "到这里我不再退。"],
        }

        tone_hint = {
            "夜神月": ["按我的计算，", "变量已经摆在这，", "你先看执行面，"],
            "蜡笔小新": ["哈哈，", "欸先别急，", "我跟你说哦，"],
            "炭治郎": ["我认真讲，", "我必须讲清楚，", "这件事我不能含糊，"],
            "章鱼哥": ["（叹气）", "（又叹气）", "唉，"],
        }

        pfx = self._choose_from_pool(
            f"{key}:pfx",
            prefix_pool.get(phase, [""])
        )
        sfx = self._choose_from_pool(
            f"{key}:sfx",
            suffix_pool.get(phase, [""])
        )
        hint = self._choose_from_pool(
            f"{key}:hint",
            tone_hint.get(speaker.name, [""])
        )

        return f"{hint}{pfx}{core_line}{sfx}"

    def _apply_persona_voice(self, speaker: Personality, text: str, phase: str) -> str:
        """把模板化文本压成更口语、更有角色辨识度的发言。"""
        if not text:
            return text

        cleaned = text.strip()

        # 去掉常见的书面AI腔，替换成更口语的表达
        replacements = {
            "综合来看": "我就直说",
            "从客观角度": "说白了",
            "首先": "先说重点",
            "其次": "再说一句",
            "最后": "最后一句",
            "建议": "我就要",
        }
        for old, new in replacements.items():
            cleaned = cleaned.replace(old, new)

        # 统一压缩重复空白
        cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
        cleaned = re.sub(r"[ \t]{2,}", " ", cleaned)

        openers = {
            "夜神月": {
                "argument": "听清楚，",
                "counter": "我只回你一句，",
                "rebuttal": "结论不变，",
            },
            "蜡笔小新": {
                "argument": "哈哈，",
                "counter": "欸你先等一下，",
                "rebuttal": "我还是那句，",
            },
            "炭治郎": {
                "argument": "我认真说，",
                "counter": "我必须回应你，",
                "rebuttal": "我不会退这一步，",
            },
            "章鱼哥": {
                "argument": "（叹气），",
                "counter": "（叹气）我回你一句，",
                "rebuttal": "（继续叹气）行吧，",
            },
        }

        closers = {
            "夜神月": "记住，规则只会站在赢的人这边。",
            "蜡笔小新": "反正我就这么选，开心最重要。",
            "炭治郎": "我问心无愧，这就是答案。",
            "章鱼哥": "随便吧，结局大概也差不多。",
        }

        phase_key = "argument"
        if phase == "counter":
            phase_key = "counter"
        elif phase == "rebuttal":
            phase_key = "rebuttal"

        persona_openers = openers.get(speaker.name, {})
        opener = persona_openers.get(phase_key, "")

        if opener and not cleaned.startswith(opener):
            cleaned = opener + cleaned

        closer = closers.get(speaker.name, "")
        if closer and closer not in cleaned:
            if not cleaned.endswith(("。", "！", "?", "？", "!")):
                cleaned += "。"
            cleaned += " " + closer

        return cleaned

    def _secondary_target(self, speaker: Personality, opponent: Personality) -> str:
        """从四人格中挑一个次级攻击目标，避免只盯着一个人。"""
        names = ["夜神月", "蜡笔小新", "炭治郎", "章鱼哥"]
        candidates = [n for n in names if n not in (speaker.name, opponent.name)]
        return candidates[0] if candidates else opponent.name

    def _risk_score_for_persona(self, speaker: Personality, position: str) -> int:
        """按人格给风险分，避免所有人雷同。"""
        if speaker.name == "夜神月":
            return 8 if position == "做" else 9
        if speaker.name == "蜡笔小新":
            return 8 if position == "做" else 7
        if speaker.name == "炭治郎":
            return 2 if position == "不做" else 3
        if speaker.name == "章鱼哥":
            return 3
        return 5

    def _extract_claims(self, text: str) -> Dict[str, bool]:
        """从对方发言里提取核心主张，用于有针对性的反驳。"""
        t = (text or "").lower()
        return {
            "control": any(k in t for k in ["控制", "最优解", "变量", "规则", "效率", "模型"]),
            "morality": any(k in t for k in ["道德", "良心", "负责", "底线", "伤害", "无辜"]),
            "fun": any(k in t for k in ["开心", "好玩", "快乐", "爽", "直觉"]),
            "nihilism": any(k in t for k in ["没意义", "都一样", "叹气", "无所谓", "空虚"]),
            "risk": any(k in t for k in ["风险", "危险", "后果", "代价"]),
        }

    def _reasoning_signal(self, reasoning: str, limit: int = 42) -> str:
        """提取思考痕迹短句，让对话显式体现推理来源。"""
        if not reasoning:
            return "我先按经验做判断。"

        candidates = []
        for raw in reasoning.replace("\n", "；").split("；"):
            s = raw.strip()
            if not s:
                continue
            if any(k in s for k in ["风险", "后果", "底线", "变量", "思考", "证据", "初始", "终局"]):
                candidates.append(s)

        if not candidates:
            candidates = [reasoning.strip()]

        chosen = candidates[0]
        if len(chosen) > limit:
            chosen = chosen[:limit] + "..."
        return f"我刚才复盘过：{chosen}"

    def _duel_strategy(self, speaker: Personality, opponent: Personality, phase: str) -> Dict[str, str]:
        """同一主人格对不同对手使用不同反驳模板。"""
        persona_map = {
            "夜神月": {
                "蜡笔小新": {
                    "argument": "你的判断像即兴玩乐，我按系统优化来。",
                    "counter": "你把快乐当方向盘，决策会直接失控。",
                    "rebuttal": "你的随机性就是最大风险源。",
                },
                "炭治郎": {
                    "argument": "你的道德感可敬，但它不能替代执行方案。",
                    "counter": "只有底线没有路径，等于把决策外包给运气。",
                    "rebuttal": "善良不是策略，控制才是策略。",
                },
                "章鱼哥": {
                    "argument": "你的虚无不是看透，只是放弃计算。",
                    "counter": "你说都一样，是因为你拒绝承担决策成本。",
                    "rebuttal": "不行动本身也是一种失败选择。",
                },
            },
            "蜡笔小新": {
                "夜神月": {
                    "argument": "你把人生当实验室，太紧绷了。",
                    "counter": "你每句话都像在写操作手册，真的很无聊。",
                    "rebuttal": "你想算赢一切，结果先输掉了快乐。",
                },
                "炭治郎": {
                    "argument": "你太想当好人，动作慢半拍。",
                    "counter": "你一直怕伤害别人，连自己想做什么都忘了。",
                    "rebuttal": "你的谨慎很体面，但会错过时机。",
                },
                "章鱼哥": {
                    "argument": "你这人最大的问题就是没劲。",
                    "counter": "你说都没意义，只是在给不行动找台阶。",
                    "rebuttal": "你把空虚讲成真理，听着就想睡。",
                },
            },
            "炭治郎": {
                "夜神月": {
                    "argument": "你过分追求控制，忽视了人的代价。",
                    "counter": "你把人当变量，这一点我不能接受。",
                    "rebuttal": "再高效的方案，越过底线就是错。",
                },
                "蜡笔小新": {
                    "argument": "你把快乐放第一位，但后果同样要负责。",
                    "counter": "冲动不是勇敢，承担后果才是。",
                    "rebuttal": "我不是反对行动，我反对无责任行动。",
                },
                "章鱼哥": {
                    "argument": "你把无意义当结论，其实是在逃避选择。",
                    "counter": "就算困难，也不能把责任交给消极。",
                    "rebuttal": "我会继续做对的事，不会因为疲惫放弃。",
                },
            },
            "章鱼哥": {
                "夜神月": {
                    "argument": "你太沉迷掌控，现实可没那么听话。",
                    "counter": "你把一切都当可计算变量，迟早翻车。",
                    "rebuttal": "你的自信常常只是延迟到来的失望。",
                },
                "蜡笔小新": {
                    "argument": "你靠兴奋决策，冷下来就只剩烂摊子。",
                    "counter": "你说开心就做，但麻烦不会因为开心消失。",
                    "rebuttal": "短暂热闹以后，还是同样空。",
                },
                "炭治郎": {
                    "argument": "你想拯救所有人，最后常常先耗尽自己。",
                    "counter": "高道德姿态很好看，但现实会很累。",
                    "rebuttal": "你坚持得很动人，结局通常很普通。",
                },
            },
        }

        default_map = {
            "argument": "我先把你核心漏洞挑出来。",
            "counter": "你这条逻辑链条不完整。",
            "rebuttal": "你还没回应关键矛盾。",
        }

        persona_strategy = persona_map.get(speaker.name, {})
        versus = persona_strategy.get(opponent.name, default_map)
        core_line = versus.get(phase, default_map.get(phase, ""))
        return {
            "line": self._line_variant(speaker, opponent, phase, core_line, "style")
        }

    def _versus_payload(self, speaker: Personality, opponent: Personality, phase: str, position: str) -> str:
        """对手特异主干句：确保同一人格面对三位对手时不是同模板。"""
        payload = {
            "夜神月": {
                "蜡笔小新": {
                    "argument": f"你靠兴奋感推进『{position}』，这不是决策，是掷骰子。",
                    "counter": "你的逻辑只有即时快感，没有风险闭环。",
                    "rebuttal": "我在谈可复制胜率，你在谈当下情绪。",
                },
                "炭治郎": {
                    "argument": f"你把善意放在第一位，但『{position}』需要的是执行秩序。",
                    "counter": "你的判断过于理想化，缺少现实约束条件。",
                    "rebuttal": "道德是约束，不是发动机。",
                },
                "章鱼哥": {
                    "argument": f"你先否定一切再评价『{position}』，等于放弃推理资格。",
                    "counter": "你所谓看透，本质是拒绝承担。",
                    "rebuttal": "不作为只是把失败时间推迟。",
                },
            },
            "蜡笔小新": {
                "夜神月": {
                    "argument": f"你把『{position}』讲得像军事命令，紧张得要命。",
                    "counter": "你太想每一步都算对，结果连出手都变慢。",
                    "rebuttal": "你活在计划里，我活在现场里。",
                },
                "炭治郎": {
                    "argument": f"你总怕做错事，结果『{position}』永远慢一步。",
                    "counter": "你考虑别人太久，会把自己的机会耗光。",
                    "rebuttal": "我承认你善良，但机会不会等道德会议开完。",
                },
                "章鱼哥": {
                    "argument": f"你先说都没意义，再否定『{position}』，这就是摆烂循环。",
                    "counter": "你的问题不是看得清，是根本不想动。",
                    "rebuttal": "你一直退场，当然觉得舞台无聊。",
                },
            },
            "炭治郎": {
                "夜神月": {
                    "argument": f"你为了达成『{position}』愿意牺牲别人，这一点不能接受。",
                    "counter": "你的效率来自对他人代价的低估。",
                    "rebuttal": "不把人当人，再漂亮的方案都不成立。",
                },
                "蜡笔小新": {
                    "argument": f"你把『{position}』交给心情决定，这会伤害无辜的人。",
                    "counter": "你把冲动叫自由，但后果需要别人买单。",
                    "rebuttal": "快乐重要，但责任更不能缺席。",
                },
                "章鱼哥": {
                    "argument": f"你因为疲惫就否定『{position}』，这是把逃避当答案。",
                    "counter": "你一直说结果都一样，是因为你放弃了改变。",
                    "rebuttal": "即使艰难，也不能把不作为合理化。",
                },
            },
            "章鱼哥": {
                "夜神月": {
                    "argument": f"你把『{position}』当控制实验，现实只会给你反噬。",
                    "counter": "你越想完全掌控，崩盘时越难看。",
                    "rebuttal": "你把不确定性当敌人，最后会被它教育。",
                },
                "蜡笔小新": {
                    "argument": f"你靠情绪推进『{position}』，热度一过就是收拾烂摊子。",
                    "counter": "你说开心就做，但麻烦从不会自动消失。",
                    "rebuttal": "短暂热闹之后，空虚照旧。",
                },
                "炭治郎": {
                    "argument": f"你把『{position}』道德化了，现实不会因为善意更轻松。",
                    "counter": "你总想两全，通常只会两边都累。",
                    "rebuttal": "你的坚持很动人，但世界没那么在乎。",
                },
            },
        }

        core_line = payload.get(speaker.name, {}).get(opponent.name, {}).get(phase, "")
        return self._line_variant(speaker, opponent, phase, core_line, "payload")

    def _targeted_hit(self,
                      speaker: Personality,
                      opponent: Personality,
                      claims: Dict[str, bool],
                      position: str) -> str:
        """根据对手刚说的话，生成有针对性的打击句。"""
        if speaker.name == "夜神月":
            if claims.get("fun"):
                return f"你把『开心』当决策引擎，这就是把『{position}』做成投骰子。"
            if claims.get("morality"):
                return f"你把道德当终点，但没有执行路径，道德口号撑不起『{position}』。"
            if claims.get("nihilism"):
                return "你说都一样，是因为你没有能力把差异做出来。"
            return "你的发言没有可执行结构，只有情绪音量。"

        if speaker.name == "蜡笔小新":
            if claims.get("control"):
                return "你说一堆模型和规则，听起来很厉害，但活起来真的很无聊。"
            if claims.get("morality"):
                return "你把自己绑在底线上，结果连尝试都不敢尝试。"
            if claims.get("nihilism"):
                return "你说都没意义，是因为你从来没认真开心过。"
            return "你讲得很满，但一点都不好玩。"

        if speaker.name == "炭治郎":
            if claims.get("control"):
                return "你把人当变量，这已经越过我的底线。"
            if claims.get("fun"):
                return "快乐不能建立在他人风险之上，这是不负责任。"
            if claims.get("nihilism"):
                return "把一切说成无意义，只是在逃避承担后果。"
            return "你的逻辑没有把他人代价算进去。"

        if speaker.name == "章鱼哥":
            if claims.get("control"):
                return "你以为自己能掌控局面，现实通常只会反手打脸。"
            if claims.get("morality"):
                return "你那套高尚说法在现实里经常换来更累的结局。"
            if claims.get("fun"):
                return "短暂快乐之后还是同样的空虚，区别不大。"
            return "你说得很努力，但结果大概率还是一样。"

        return "我不同意你的核心判断。"
    
    def generate_disagreement_dialogue(self, 
                                       personality1: Personality,
                                       decision1: str,
                                       reasoning1: str,
                                       personality2: Personality,
                                       decision2: str,
                                       reasoning2: str) -> Dict:
        """
        生成两个人格之间的对话（完全本地生成，不用 LLM）
        """
        
        dialogue = {
            "participants": [personality1.name, personality2.name],
            "stance": [decision1, decision2],
            "exchanges": [],
            "conflict_intensity": 0.0
        }
        
        # 根据人格生成对话
        # 第 1 次发言：personality1 论述自己的立场
        exchange_1 = self._generate_argument(
            personality1, decision1, reasoning1, personality2, decision2
        )
        dialogue["exchanges"].append(exchange_1)
        
        # 第 2 次发言：personality2 反驳
        exchange_2 = self._generate_counterargument(
            personality2, decision2, reasoning2, personality1, decision1,
            opponent_argument=exchange_1.get("argument", "")
        )
        dialogue["exchanges"].append(exchange_2)
        
        # 第 3 次发言：personality1 再次论证（用不同的论点，不重复）
        exchange_3 = self._generate_rebuttal(
            personality1, decision1, reasoning1, personality2, decision2,
            opponent_counter=exchange_2.get("counter_argument", ""),
            own_argument=exchange_1.get("argument", "")
        )
        exchange_3["round"] = 2
        dialogue["exchanges"].append(exchange_3)
        
        # 冲突强度 = 两个人格的差异程度 + 决策是否相反
        conflict_intensity = abs(personality1.risk - personality2.risk) * 0.5
        if decision1 != decision2:
            conflict_intensity += 0.5
        
        dialogue["conflict_intensity"] = min(conflict_intensity, 1.0)
        
        return dialogue
    
    def _generate_argument(self,
                          speaker: Personality,
                          position: str,
                          reasoning: str,
                          opponent: Personality,
                          opponent_position: str) -> Dict:
        """第一轮立场：强人格、自白式、去AI腔。"""
        
        arg = {
            "speaker": speaker.name,
            "position": position,
            "argument": "",
            "tone": speaker.tone,
            "risk_score": self._risk_score_for_persona(speaker, position),
            "stance": "强烈支持" if position == "做" else "坚决反对",
        }
        second_target = self._secondary_target(speaker, opponent)
        trace = self._reasoning_signal(reasoning)
        style = self._duel_strategy(speaker, opponent, "argument")
        versus = self._versus_payload(speaker, opponent, "argument", position)

        if speaker.name == "夜神月":
            raw_text = (
                f"我站『{position}』，风险给 {arg['risk_score']}/10。"
                f"{trace}"
                f"{style['line']}"
                f"{versus}"
                f"这就是唯一最优解。变量我已经算完：时间、成本、机会、执行窗口，全部指向同一个结论。"
                f"{opponent.name}把情绪当判断，{second_target}把犹豫当谨慎，你们太幼稚了。"
                f"我不要被安慰，我要控制权。规则要么由我制定，要么被我重写。"
            )
            arg["argument"] = self._apply_persona_voice(speaker, raw_text, "argument")
        elif speaker.name == "蜡笔小新":
            raw_text = (
                f"我选『{position}』，风险就给 {arg['risk_score']}/10。"
                f"{trace}"
                f"{style['line']}"
                f"{versus}"
                f"好玩才重要，开心就做啊，想那么多干嘛。"
                f"{opponent.name}一开口就是规则和控制，{second_target}一开口就是道德和牺牲，听着就累。"
                f"你们活得像说明书，我活得像人生。现在想做就做，这才叫在活。"
            )
            arg["argument"] = self._apply_persona_voice(speaker, raw_text, "argument")
        elif speaker.name == "炭治郎":
            raw_text = (
                f"我选『{position}』，风险我给 {arg['risk_score']}/10。"
                f"{trace}"
                f"{style['line']}"
                f"{versus}"
                f"这是底线，不是情绪。"
                f"{opponent.name}把人当变量，{second_target}把快乐当借口，这两种做法都会让无辜者承担代价。"
                f"我不能伤害别人，也不能把责任推给命运。哪怕难走，我也要走问心无愧的路。"
            )
            arg["argument"] = self._apply_persona_voice(speaker, raw_text, "argument")
        elif speaker.name == "章鱼哥":
            raw_text = (
                f"你们吵吧，我选『{position}』，风险给 {arg['risk_score']}/10。"
                f"{trace}"
                f"{style['line']}"
                f"{versus}"
                f"『{position}』也好，『{opponent_position}』也罢，结果都一样。"
                f"{opponent.name}以为自己能掌控一切，{second_target}以为热血就能救世界，听起来都很努力，但都没意义。"
                f"我不是相信它有多伟大，我只是懒得再演那套改变命运的戏。"
            )
            arg["argument"] = self._apply_persona_voice(speaker, raw_text, "argument")

        else:
            arg["argument"] = f"我坚持『{position}』，风险 {arg['risk_score']}/10。"
        return arg
    
    def _generate_counterargument(self,
                                  speaker: Personality,
                                  position: str,
                                  reasoning: str,
                                  opponent: Personality,
                                  opponent_position: str,
                                  opponent_argument: str = "") -> Dict:
        """第二轮反驳：短句、攻击、人格语气。"""
        
        arg = {
            "speaker": speaker.name,
            "counter_to": opponent.name,
            "position": position,
            "counter_argument": "",
            "tone": speaker.tone
        }
        
        second_target = self._secondary_target(speaker, opponent)
        claims = self._extract_claims(opponent_argument)
        hit = self._targeted_hit(speaker, opponent, claims, position)
        trace = self._reasoning_signal(reasoning)
        style = self._duel_strategy(speaker, opponent, "counter")
        versus = self._versus_payload(speaker, opponent, "counter", position)

        if speaker.name == "夜神月":
            raw_text = (
                f"{trace}"
                f"{style['line']}"
                f"{versus}"
                f"你刚才那套说法，我已经听完了。{hit}"
                f"听清楚，『{position}』不是口号，是可执行的最优解。"
                f"{opponent.name}在回避变量，{second_target}在回避责任。你们把冲动包装成勇气，把拖延包装成谨慎。"
                f"我不和情绪争辩，我只看结果，而结果会站在『{position}』这一边。"
            )
            arg["counter_argument"] = self._apply_persona_voice(speaker, raw_text, "counter")
        
        elif speaker.name == "蜡笔小新":
            raw_text = (
                f"{trace}"
                f"{style['line']}"
                f"{versus}"
                f"你刚才讲那一大段，我抓到重点了：{hit}"
                f"哈哈，你想太多啦。『{position}』就是更好玩、更爽、更像活人。"
                f"{opponent.name}要我按规则活，{second_target}要我按道德活，你们都想把人生变成作业。"
                f"我不要完美答案，我要现在就能笑出来的答案。开心就做啊，这就是我的判断。"
            )
            arg["counter_argument"] = self._apply_persona_voice(speaker, raw_text, "counter")
        
        elif speaker.name == "炭治郎":
            raw_text = (
                f"{trace}"
                f"{style['line']}"
                f"{versus}"
                f"我听到了你的理由，我只回应关键点：{hit}"
                f"我听到了你的理由，但我不能接受。『{position}』必须先过道德这一关。"
                f"{opponent.name}在用效率掩盖伤害，{second_target}在用情绪逃避后果。"
                f"我必须负责，不能伤害别人。这不是软弱，这是底线。"
            )
            arg["counter_argument"] = self._apply_persona_voice(speaker, raw_text, "counter")
        
        elif speaker.name == "章鱼哥":
            raw_text = (
                f"{trace}"
                f"{style['line']}"
                f"{versus}"
                f"（叹气）你刚才那段我听到了：{hit}"
                f"（叹气）你们还在争这个？『{position}』和『{opponent_position}』最后都一样。"
                f"{opponent.name}太自恋，{second_target}太天真，一个想控制世界，一个想感动世界。"
                f"世界根本不在乎。随便吧，少折腾一点就是赢。"
            )
            arg["counter_argument"] = self._apply_persona_voice(speaker, raw_text, "counter")
        
        else:
            arg["counter_argument"] = f"等等，我不同意你的看法。你忽视了『{position}』的一个关键优势，那就是..."
        
        return arg
    
    def _generate_rebuttal(self,
                         speaker: Personality,
                         position: str,
                         reasoning: str,
                         opponent: Personality,
                         opponent_position: str,
                         opponent_counter: str = "",
                         own_argument: str = "") -> Dict:
        """第三轮再论证：加压收口，不重复第一轮。"""
        
        arg = {
            "speaker": speaker.name,
            "position": position,
            "rebuttal": "",
            "tone": speaker.tone
        }
        
        second_target = self._secondary_target(speaker, opponent)
        counter_claims = self._extract_claims(opponent_counter)
        counter_hit = self._targeted_hit(speaker, opponent, counter_claims, position)
        trace = self._reasoning_signal(reasoning)
        style = self._duel_strategy(speaker, opponent, "rebuttal")
        versus = self._versus_payload(speaker, opponent, "rebuttal", position)

        if speaker.name == "夜神月":
            raw_text = (
                f"{trace}"
                f"{style['line']}"
                f"{versus}"
                f"你上一轮的反驳我记住了：{counter_hit}"
                f"我再说一次，『{position}』不是偏好，是结论。"
                f"{opponent.name}和{second_target}都在回避关键变量：执行成本、回报速度、控制半径。"
                f"你们想要的是被安慰，我要的是胜利。等结果出来，你们会知道谁才配制定规则。"
            )
            arg["rebuttal"] = self._apply_persona_voice(speaker, raw_text, "rebuttal")
        
        elif speaker.name == "蜡笔小新":
            raw_text = (
                f"{trace}"
                f"{style['line']}"
                f"{versus}"
                f"你刚刚反驳我的点，我就一句：{counter_hit}"
                f"哈哈，还在讲大道理？我不买账。『{position}』让我现在就有劲，这就够了。"
                f"{opponent.name}要我变成机器，{second_target}要我变成苦行僧，我才不要。"
                f"你们等“正确时机”，我直接开玩。人生是现场，不是彩排。"
            )
            arg["rebuttal"] = self._apply_persona_voice(speaker, raw_text, "rebuttal")
        
        elif speaker.name == "炭治郎":
            raw_text = (
                f"{trace}"
                f"{style['line']}"
                f"{versus}"
                f"你刚才的反驳我回应完了：{counter_hit}"
                f"我的答案不会变：『{position}』。因为我必须负责，这是我的底线。"
                f"{opponent.name}忽视了人的痛苦，{second_target}轻视了后果。"
                f"我可以承受困难，但不能把代价丢给别人。只要这点不变，我就会坚持到底。"
            )
            arg["rebuttal"] = self._apply_persona_voice(speaker, raw_text, "rebuttal")
        
        elif speaker.name == "章鱼哥":
            raw_text = (
                f"{trace}"
                f"{style['line']}"
                f"{versus}"
                f"（继续叹气）你上一轮说的那些，我只回一句：{counter_hit}"
                f"（继续叹气）我还是那句话：『{position}』和『{opponent_position}』，都不会把你们从空虚里救出来。"
                f"{opponent.name}太用力，{second_target}太入戏。你们把选择说得像史诗，其实就是普通失望的不同版本。"
                f"所以我就这样选。不是相信，而是看透。"
            )
            arg["rebuttal"] = self._apply_persona_voice(speaker, raw_text, "rebuttal")
        
        else:
            arg["rebuttal"] = f"我坚守我的立场。『{position}』是对的。"
        
        return arg
# 🎯 测试代码
# =========================
if __name__ == "__main__":
    from personality import Personality
    
    # 创建人格
    personality = Personality(
        "蜡笔小新", 0.8, 1.0, 0.2,
        "世界用来开心", "开心就做", "随便"
    )
    
    # 测试反思系统
    reflector = AgentReflectionSystem()
    
    print("🧠 Agent 反思系统演示")
    print("=" * 60)
    
    reflection = reflector.multi_round_reflection(
        personality=personality,
        initial_decision="做",
        question="我该不该辞职创业？",
        risk_level=0.7,
        depth="deep"
    )
    
    print(f"初始决策：{reflection['initial_decision']}")
    print(f"最终决策：{reflection['final_verdict']}")
    print(f"置信度演变：{reflection['confidence_evolution']}")
    
    print(f"\n📊 反思质量分析：")
    analysis = reflector.analyze_reflection_quality(reflection)
    print(f"决策稳定性：{analysis['decision_stability']}")
    print(f"思考深度：{analysis['thinking_depth']}")
    print(f"评价：{analysis['reflection_quality']}")
    
    print("\n✅ 反思系统演示完成！")
