from prompt import build_prompt, build_judge_prompt, build_debate_prompt
import os
from dotenv import load_dotenv
load_dotenv()
import requests
import time
import re
import random
from personality import Personality

# 👉 API配置
API_URL = "https://api.deepseek.com/chat/completions"
API_KEY = os.getenv("DEEPSEEK_API_KEY")

# =========================
# 🔥 调用API
# =========================
def clean_text(text):
    return text.encode("utf-8", "ignore").decode("utf-8")

def call_api(prompt):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.9
    }

    for i in range(3):
        try:
            response = requests.post(
                API_URL,
                headers=headers,
                json=data,
                timeout=30
            )

            response.raise_for_status()

            res = response.json()
            return res["choices"][0]["message"]["content"]

        except requests.exceptions.RequestException as e:
            print("❌ API错误:", e)
            print(f"⚠️ 重试 {i+1}/3")
            time.sleep(2)

    return "❌ API调用失败"
# =========================
# 🔥 解析函数（最终版）
# =========================
def parse_result(result):
    decision = None
    confidence = 5
    weight = 0.5
    risk_score = 5

    # ✅ 决策解析（防bug）
    try:
        decision_part = result.split("【决策】")[1].strip().split("\n")[0]

        if "不做" in decision_part:
            decision = "不做"
        elif "做" in decision_part:
            decision = "做"
    except:
        pass

    # ✅ 置信度
    try:
        conf_part = result.split("【对自己结论的置信度】")[1]
        confidence = float(conf_part.strip().split("\n")[0])
    except:
        confidence = 5

    # ✅ 权重
    match = re.search(r"【决策权重】\s*([0-9.]+)", result)
    if match:
        weight = float(match.group(1))
    else:
        weight = confidence / 10

    # ✅ 问题风险
    try:
        risk_part = result.split("【问题风险评估】")[1]
        risk_score = float(risk_part.strip().split("\n")[0])
    except:
        risk_score = 5

    return decision, weight, confidence, risk_score


# =========================
# 🔥 人格一致性检测
# =========================
def check_personality_consistency(personality, decision):
    if personality.risk < 0.3 and decision == "做":
        print(f"⚠️ {personality.name} 偏离人设（过激进）")
    if personality.risk > 0.7 and decision == "不做":
        print(f"⚠️ {personality.name} 偏离人设（过保守）")


# =========================
# 🔥 单人格决策
# =========================
def make_decision(personality, question, all_personalities):
    prompt = build_prompt(personality, question, all_personalities)
    return call_api(prompt)


# =========================
# 🚀 主程序（比赛版）
# =========================
def run_multi_round_decision(question, personalities):
    all_results = ""

    score_do = 0
    score_not = 0

    results_round1 = []
    results_round2 = []
    # 第一轮
    for p in personalities:
        result = call_api(build_prompt(p, question, personalities))
        results_round1.append((p.name, result))

    # 第二轮
    for p in personalities:
        debate_prompt = build_debate_prompt(
            personality=p,
            question=question,
            all_personalities=personalities,
            previous_results=results_round1
        )

        result = call_api(debate_prompt)
        results_round2.append((p.name, result))

        all_results += result + "\n\n"

        decision, weight, confidence, risk_score = parse_result(result)

        if risk_score >= 7 and decision == "做":
            weight *= 0.6
        elif risk_score <= 3 and decision == "不做":
            weight *= 0.7

        import random
        weight *= random.uniform(0.85, 1.15)

        if decision == "做":
            score_do += weight
        elif decision == "不做":
            score_not += weight

    summary = f"""
支持做：{round(score_do, 2)}
支持不做：{round(score_not, 2)}
"""

    judge_prompt = build_judge_prompt(all_results + summary, question)
    final_result = call_api(judge_prompt)

    return {
        "round1": results_round1,
        "round2": results_round2,
        "summary": summary,
        "final": final_result
    }


def main():
    personalities = [

        Personality(
            name="夜神月",
            risk=0.6,
            emotion=0.3,
            logic=1.0,
            worldview="世界是一个可以被优化的系统，自己是规则制定者",
            decision_style="追求最优解，可以牺牲他人以达成目标",
            tone="冷静、压迫感强、带优越感"
        ),

        Personality(
            name="蜡笔小新",
            risk=0.8,
            emotion=1.0,
            logic=0.2,
            worldview="世界是用来享受和娱乐的",
            decision_style="凭感觉行动，只要开心就做",
            tone="随便、调侃、不严肃、胡闹"
        ),

        Personality(
            name="炭治郎",
            risk=0.3,
            emotion=0.8,
            logic=0.6,
            worldview="世界需要被善意对待，人和情感很重要",
            decision_style="优先道德，不伤害他人，有底线",
            tone="温和、真诚、坚定"
        ),

        Personality(
            name="章鱼哥",
            risk=0.1,
            emotion=0.4,
            logic=0.7,
            worldview="世界大多数事情没有意义",
            decision_style="倾向否定行动，避免麻烦",
            tone="冷淡、讽刺、不耐烦"
        )
    ]

    # ✅ 自由提问
    question = input("\n👉 请输入你的问题：\n> ")

    all_results = ""

    score_do = 0
    score_not = 0

    print("\n🔥 多人格决策开始\n")

    # =========================
    # 🧠 多人格执行
    # =========================
    # =========================
    # 🧠 第一轮（初始决策）
    # =========================
    results_round1 = []

    for p in personalities:
        result = call_api(build_prompt(p, question, personalities))
        print(f"\n🧠 {p.name} 第一轮：\n")
        print(result)
        print("\n====================\n")

        results_round1.append(result)


    # =========================
    # ⚔️ 第二轮（人格博弈）
    # =========================
    results_round2 = []

    # ========================================================
    # 🔥 防御性导入：在这里强制重新加载函数，彻底解决 NameError
    # ========================================================
    try:
        from prompt import build_debate_prompt, build_judge_prompt
    except ImportError:
        print("❌ 错误：无法从 prompt.py 导入函数，请检查文件名是否正确！")

    # 开始循环
    for i, p in enumerate(personalities):
        # 此时 build_debate_prompt 已被加载到局部作用域，绝对可用
        debate_prompt = build_debate_prompt(
            personality=p,
            question=question,
            all_personalities=personalities,
            previous_results=results_round1
        )
        
        # 调用 API
        result = call_api(debate_prompt)
        # --- 后续逻辑保持不变 ---

        print(f"\n🔥 {p.name} 第二轮（反驳后）：\n")
        print(result)
        print("\n====================\n")

        results_round2.append(result)

        # 🔥 解析
        decision, weight, confidence, risk_score = parse_result(result)

        # 🔥 展示增强（比赛加分点）
        print(f"👉 解析：决策={decision} | 权重={weight:.2f} | 置信度={confidence} | 风险={risk_score}")

        # 🔥 人格检测
        check_personality_consistency(p, decision)

        # =========================
        # 🔥 风险修正（核心亮点）
        # =========================
        if risk_score >= 7 and decision == "做":
            weight *= 0.6
        elif risk_score <= 3 and decision == "不做":
            weight *= 0.7

        # =========================
        # 🔥 微随机扰动（解决2v2问题）
        # =========================
        weight *= random.uniform(0.85, 1.15)

        # 🔥 加权
        if decision == "做":
            score_do += weight
        elif decision == "不做":
            score_not += weight

    # =========================
    # 📊 投票结果
    # =========================
    summary = f"""
【加权投票结果】
支持做：{round(score_do, 2)}
支持不做：{round(score_not, 2)}
"""

    print(summary)

    # =========================
    # 🔥 冲突指数（比赛亮点）
    # =========================
    total = score_do + score_not
    if total > 0:
        conflict = 1 - abs(score_do - score_not) / total
        print(f"⚔️ 人格冲突指数：{round(conflict * 100)}%")

    # =========================
    # 🧠 裁判系统
    # =========================
    print("\n🧠 裁判决策中...\n")

    # 1. 确保使用的是刚才合并好的第二轮所有人的发言
    all_debate_text = "\n\n".join(results_round2) 

    # 2. 🔥 修正：把 all_results 改为 all_debate_text
    judge_prompt = build_judge_prompt(all_debate_text + summary, question)
    
    # 3. 发送给 API
    final_result = call_api(judge_prompt)

    print("🏁 最终裁决：\n")
    print(final_result)