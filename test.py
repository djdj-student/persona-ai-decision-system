import os
from dotenv import load_dotenv
load_dotenv()
import requests
import time
import re
import random
from personality import Personality
from prompt import build_prompt, build_judge_prompt

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

    response = requests.post(API_URL, headers=headers, json=data)

    try:
        return response.json()["choices"][0]["message"]["content"]
    except:
        return str(response.text)


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
def main():
    personalities = [
        Personality("保守型", 0.1, 0.2, 0.9),
        Personality("激进型", 0.9, 0.8, 0.4),
        Personality("现实平衡型", 0.5, 0.4, 0.7),
        Personality("赌徒型", 1.0, 0.9, 0.2),
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
    for p in personalities:
        result = make_decision(p, question, personalities)

        print(result)
        print("\n====================\n")

        all_results += result + "\n\n"

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

    judge_prompt = build_judge_prompt(all_results + summary, question)
    final_result = call_api(judge_prompt)

    print("🏁 最终裁决：\n")
    print(final_result)


# =========================
# ▶️ 启动
# =========================
if __name__ == "__main__":
    main()