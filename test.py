from prompt import build_prompt, build_judge_prompt, build_debate_prompt
import os
from dotenv import load_dotenv
load_dotenv()
import requests
import time
import re
import random
import json
from datetime import datetime
from personality import Personality

# 🔧 配置日志
LOG_DIR = "decision_logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

def log_message(msg):
    """记录日志到控制台和文件"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{timestamp}] {msg}"
    print(log_msg)

# 👉 API配置
API_URL = "https://api.deepseek.com/chat/completions"
API_KEY = os.getenv("DEEPSEEK_API_KEY")

def call_api(prompt, max_retries=3):
    """调用 DeepSeek API，带重试机制和详细错误日志"""
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

    for attempt in range(max_retries):
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

        except requests.exceptions.Timeout:
            log_message(f"❌ API 超时错误 (尝试 {attempt + 1}/{max_retries})")
        except requests.exceptions.ConnectionError as e:
            log_message(f"❌ API 连接错误: {str(e)[:100]} (尝试 {attempt + 1}/{max_retries})")
        except requests.exceptions.HTTPError as e:
            log_message(f"❌ API HTTP错误: {response.status_code} (尝试 {attempt + 1}/{max_retries})")
        except (KeyError, ValueError) as e:
            log_message(f"❌ API 响应解析错误: {str(e)[:100]} (尝试 {attempt + 1}/{max_retries})")
            return "❌ 无法解析 API 响应"
        except Exception as e:
            log_message(f"❌ 未知错误: {str(e)[:100]} (尝试 {attempt + 1}/{max_retries})")
        
        if attempt < max_retries - 1:
            time.sleep(2)

    log_message("❌ API 调用失败：已超过最大重试次数")
    return "❌ API 调用失败"
# =========================
# 🔥 解析函数（最终版）
# =========================
def parse_result(result, debug=False):
    """解析 API 返回的决策信息，包含详细错误日志"""
    decision = None
    confidence = 5
    weight = 0.5
    risk_score = 5
    
    if debug:
        log_message(f"🔍 调试模式：原始响应前200字符:  {result[:200]}")

    # ✅ 决策解析（防bug）
    try:
        decision_part = result.split("【决策】")[1].strip().split("\n")[0].strip()
        if "不做" in decision_part:
            decision = "不做"
        elif "做" in decision_part:
            decision = "做"
        if debug and decision:
            log_message(f"✅ 决策成功解析: {decision}")
    except (IndexError, AttributeError) as e:
        log_message(f"⚠️ 决策解析失败: {str(e)[:100]}")

    # ✅ 信心度（对应 Prompt 中的【信心】，0-10）
    try:
        # 尝试新标签
        conf_part = result.split("【信心】")[1]
        confidence_str = conf_part.strip().split("\n")[0].strip()
        confidence = float(confidence_str)
        if debug:
            log_message(f"✅ 信心度成功解析: {confidence}")
    except (IndexError, ValueError):
        try:
            # 备选标签以兼容旧格式
            conf_part = result.split("【对自己结论的置信度】")[1]
            confidence_str = conf_part.strip().split("\n")[0].strip()
            confidence = float(confidence_str)
            if debug:
                log_message(f"✅ 置信度(备选)成功解析: {confidence}")
        except (IndexError, ValueError) as e:
            log_message(f"⚠️ 信心度解析失败，使用默认值 5: {str(e)[:100]}")
            if debug:
                log_message(f"   搜索文本中是否包含【信心】或【置信度】...")
            confidence = 5

    # ✅ 权重（对应 Prompt 中的【决策权重】，0-1）
    try:
        match = re.search(r"【决策权重】\s*([0-9.]+)", result)
        if match:
            weight = float(match.group(1))
            if debug:
                log_message(f"✅ 权重成功解析: {weight}")
        else:
            weight = min(confidence / 10, 0.99)
            if debug:
                log_message(f"⚠️ 权重未找到，使用信心度推算: {weight}")
    except ValueError as e:
        log_message(f"⚠️ 权重转换失败: {str(e)[:100]}")
        weight = confidence / 10

    # ✅ 风险评分（对应 Prompt 中的【风险评分】，0-10）
    try:
        # 尝试新标签
        risk_match = re.search(r"【风险评分】\s*([0-9]+)", result)
        if risk_match:
            risk_score = float(risk_match.group(1))
            if debug:
                log_message(f"✅ 风险评分成功解析: {risk_score}")
        else:
            raise ValueError("未找到【风险评分】")
    except (IndexError, ValueError):
        try:
            # 备选标签以兼容旧格式
            risk_part = result.split("【问题风险评估】")[1]
            risk_score = float(risk_part.strip().split("\n")[0])
            if debug:
                log_message(f"✅ 风险评估(备选)成功解析: {risk_score}")
        except (IndexError, ValueError) as e:
            log_message(f"⚠️ 风险评分解析失败，使用默认值 5: {str(e)[:100]}")
            if debug:
                log_message(f"   搜索文本中是否包含【风险评分】或【问题风险评估】...")
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


def main(debug=False):
    # 🔧 设置随机种子以保证可复现性（可选）
    # random.seed(42)  # 取消注释以获得确定性结果
    
    if debug:
        log_message("🔍 调试模式已启用：将显示所有解析细节")
    log_message("🚀 多人格决策系统启动")
    
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
    # 🧠 第一轮（初始决策）
    # =========================
    results_round1 = []
    log_message("\n🎬 第一轮：初始决策开始")

    for p in personalities:
        result = call_api(build_prompt(p, question, personalities))
        log_message(f"✅ {p.name} 完成第一轮决策")
        print(f"\n🧠 {p.name} 第一轮：\n")
        print(result)
        print("\n====================\n")
        results_round1.append(result)

    # =========================
    # ⚔️ 第二轮（人格博弈）
    # =========================
    results_round2 = []
    log_message("\n⚔️ 第二轮：人格博弈开始")

    # 开始循环
    for i, p in enumerate(personalities):
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
        decision, weight, confidence, risk_score = parse_result(result, debug=debug)

        # 🔥 展示增强（比赛加分点）
        print(f"👉 解析：决策={decision} | 权重={weight:.2f} | 信心={confidence} | 风险={risk_score}")
        log_message(f"📊 {p.name}: 决策={decision}, 权重={weight:.2f}, 信心={confidence}, 风险={risk_score}")

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
    log_message(f"📊 投票结果 - 支持做: {round(score_do, 2)}, 支持不做: {round(score_not, 2)}")

    # =========================
    # 🔥 冲突指数（比赛亮点）
    # =========================
    total = score_do + score_not
    if total > 0:
        conflict = 1 - abs(score_do - score_not) / total
        conflict_pct = round(conflict * 100)
        print(f"⚔️ 人格冲突指数：{conflict_pct}%")
        log_message(f"⚔️ 人格冲突指数: {conflict_pct}%")

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
    
    # =========================
    # 💾 保存决策记录
    # =========================
    decision_record = {
        "timestamp": datetime.now().isoformat(),
        "question": question,
        "round1_results": results_round1,
        "round2_results": results_round2,
        "scores": {"支持做": round(score_do, 2), "支持不做": round(score_not, 2)},
        "conflict_index": round(conflict * 100) if total > 0 else 0,
        "final_judgment": final_result
    }
    
    filename = os.path.join(LOG_DIR, f"decision_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(decision_record, f, ensure_ascii=False, indent=2)
    
    log_message(f"💾 决策记录已保存到: {filename}")

# =========================
# 🚀 启动脚本
# =========================
if __name__ == "__main__":
    # 调试模式：设置为 True 可以看到详细的解析日志
    main(debug=True)
    