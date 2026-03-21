# 🚀 完整的 Agent 决策系统集成（主文件）

from agent_engine import AgentDecisionEngine
from agent_reflection import AgentReflectionSystem, AgentDialogueSystem
from hybrid_system import HybridDecisionSystem
from personality import Personality
from test import call_api, parse_result, log_message
import os
from prompt import build_prompt, build_judge_prompt, build_debate_prompt
import json
from datetime import datetime

# 🔧 配置
LOG_DIR = "agent_workflows"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# ============================================
# 🎯 新的主工作流：Agent + LLM 混合模式
# ============================================

def hybrid_multi_round_decision(question: str, personalities: list, 
                               use_local_only: bool = False,
                               use_full_workflow: bool = True,
                               depth: str = "standard") -> dict:
    """
    完整的混合决策系统
    
    参数：
    - use_local_only: 只使用本地 Agent 决策（完全不用 LLM）
    - use_full_workflow: 使用完整的 5 阶段工作流
    - depth: 反思深度 (quick, standard, deep, expert)
    """
    
    print("\n" + "="*80)
    print("🤖 智能 Agent 决策系统启动")
    print("="*80)
    
    # ============================================
    # 🔄 阶段 0：问题分析
    # ============================================
    print("\n📊 阶段 0：问题分析")
    agent_engine = AgentDecisionEngine()
    risk_level = agent_engine._analyze_question_risk(question, "")
    print(f"问题风险等级：{risk_level:.2f}/1.0")
    
    all_results = {
        "question": question,
        "timestamp": datetime.now().isoformat(),
        "use_local_only": use_local_only,
        "depth": depth,
        "stages": {}
    }
    
    # ============================================
    # 选择工作流模式
    # ============================================
    
    if use_full_workflow:
        # 使用完整的混合工作流（推荐）
        log_message("✨ 启动完整混合工作流（5阶段）")
        
        hybrid_system = HybridDecisionSystem(
            llm_call_func=call_api if not use_local_only else None
        )
        
        workflow = hybrid_system.full_decision_workflow(
            personalities=personalities,
            question=question,
            depth=depth,
            use_llm=not use_local_only
        )
        
        all_results["workflow"] = workflow
        all_results["final_decision"] = workflow["stages"]["5_synthesis"]["final_decision"]
        
        # 保存工作流
        workflow_file = os.path.join(LOG_DIR, f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(workflow_file, 'w', encoding='utf-8') as f:
            json.dump(workflow, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 工作流已保存：{workflow_file}")
    
    else:
        # 使用简化的两轮模式（原始）
        log_message("📌 启动简化两轮模式（支持向后兼容）")
        
        all_results["stages"]["round1"] = []
        all_results["stages"]["round2"] = []
        
        # =========================
        # ROUND 1: 本地快速决策
        # =========================
        print("\n🧠 ROUND 1：本地快速决策")
        print("-" * 60)
        
        round1_decisions = []
        for p in personalities:
            local_decision = agent_engine.quick_decision(p, question, "")
            round1_decisions.append(local_decision)
            print(f"✓ {p.name}：{local_decision['decision']} "
                  f"（信心 {local_decision['confidence']}/10，权重 {local_decision['weight']}）")
            all_results["stages"]["round1"].append(local_decision)
        
        # =========================
        # ROUND 2: LLM 强化 + 反思
        # =========================
        if not use_local_only:
            print("\n🧠 ROUND 2：LLM 强化决策")
            print("-" * 60)
            
            reflection_system = AgentReflectionSystem()
            
            score_do = 0
            score_not = 0
            
            for i, p in enumerate(personalities):
                local_decision = round1_decisions[i]
                
                # 用 LLM 强化决策
                llm_prompt = build_prompt(p, question, personalities)
                llm_response = call_api(llm_prompt)
                
                decision, weight, confidence, risk_score = parse_result(llm_response, debug=False)
                
                # 使用反思系统进行深度分析
                reflection = reflection_system.multi_round_reflection(
                    personality=p,
                    initial_decision=decision or local_decision['decision'],
                    question=question,
                    risk_level=risk_level,
                    depth=depth,
                    local_reasoning=local_decision['reasoning']
                )
                
                final_decision = reflection['final_verdict']
                
                print(f"✓ {p.name}：{final_decision} "
                      f"（信心 {reflection['confidence_evolution'][-1]}/10）")
                
                # 加权计分
                if final_decision == "做":
                    score_do += weight
                else:
                    score_not += weight
                
                all_results["stages"]["round2"].append({
                    "personality": p.name,
                    "llm_response": llm_response[:200],
                    "final_decision": final_decision,
                    "reflection_stability": reflection.get('confidence_evolution', [])
                })
            
            all_results["stages"]["round2_scores"] = {
                "支持做": round(score_do, 2),
                "支持不做": round(score_not, 2)
            }
            all_results["final_decision"] = "做" if score_do > score_not else "不做"
        
        else:
            # 纯本地模式：只用本地 Agent
            print("\n✨ 纯本地模式（不使用 LLM）")
            print("-" * 60)
            
            score_do = 0
            score_not = 0
            
            for i, p in enumerate(personalities):
                local_decision = round1_decisions[i]
                
                if local_decision['decision'] == "做":
                    score_do += local_decision['weight']
                else:
                    score_not += local_decision['weight']
            
            all_results["stages"]["local_scores"] = {
                "支持做": round(score_do, 2),
                "支持不做": round(score_not, 2)
            }
            all_results["final_decision"] = "做" if score_do > score_not else "不做"
    
    # ============================================
    # 📊 最终总结
    # ============================================
    print("\n" + "="*80)
    print("🏁 决策完成")
    print("="*80)
    print(f"\n🎯 最终建议：{all_results['final_decision']}")
    
    # 保存记录
    record_file = os.path.join(LOG_DIR, f"decision_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(record_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    
    print(f"💾 决策记录已保存：{record_file}\n")
    
    return all_results


# ============================================
# 🎯 使用示例
# ============================================

def main(use_full_workflow: bool = True, use_local_only: bool = False):
    """
    主函数
    
    use_full_workflow: 是否使用完整的 5 阶段工作流
    use_local_only: 是否只使用本地 Agent（不调用 LLM）
    """
    
    log_message("🚀 Agent 决策系统启动")
    
    # 创建人格
    personalities = [
        Personality(
            "夜神月", 0.6, 0.3, 1.0,
            "世界是一个可以被优化的系统",
            "追求最优解，可以牺牲他人以达成目标",
            "冷静、压迫感强、优越感"
        ),
        Personality(
            "蜡笔小新", 0.8, 1.0, 0.2,
            "世界是用来享受的",
            "凭感觉行动，只要开心就做",
            "随便、调侃、不严肃"
        ),
        Personality(
            "炭治郎", 0.3, 0.8, 0.6,
            "世界需要被善意对待",
            "优先道德，不伤害他人",
            "温和、真诚、坚定"
        ),
        Personality(
            "章鱼哥", 0.1, 0.4, 0.7,
            "世界大多无意义",
            "倾向否定行动，避免麻烦",
            "冷淡、讽刺、不耐烦"
        )
    ]
    
    # 获取问题
    question = input("\n👉 请输入你的问题：\n> ")
    
    if not question.strip():
        question = "我该不该辞职创业？"
        print(f"使用默认问题：{question}")
    
    # 运行决策系统
    result = hybrid_multi_round_decision(
        question=question,
        personalities=personalities,
        use_local_only=use_local_only,
        use_full_workflow=use_full_workflow,
        depth="deep"  # 深度思考
    )
    
    return result


# ============================================
# 📊 分析工具
# ============================================

def analyze_decision_logs(log_dir: str = LOG_DIR):
    """分析所有决策日志，显示统计信息"""
    
    import os
    
    logs = [f for f in os.listdir(log_dir) if f.endswith('.json')]
    
    if not logs:
        print("❌ 没有决策日志")
        return
    
    print(f"\n📊 决策日志分析 (共 {len(logs)} 条)")
    print("=" * 60)
    
    total_decisions = {"做": 0, "不做": 0}
    
    for log_file in sorted(logs):
        with open(os.path.join(log_dir, log_file), 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            final = data.get('final_decision', '未知')
            timestamp = data.get('timestamp', '未知')
            
            total_decisions[final] = total_decisions.get(final, 0) + 1
            
            print(f"✓ {log_file}: {final} ({timestamp})")
    
    print("\n📈 统计：")
    print(f"  支持『做』：{total_decisions.get('做', 0)} 次")
    print(f"  支持『不做』：{total_decisions.get('不做', 0)} 次")


# ============================================
# 🚀 启动脚本
# ============================================

if __name__ == "__main__":
    import sys
    
    # 检查命令行参数
    use_full_workflow = True
    use_local_only = False
    
    if len(sys.argv) > 1:
        if "--local-only" in sys.argv:
            use_local_only = True
            print("🔒 使用纯本地模式（不调用 LLM）")
        
        if "--simple" in sys.argv:
            use_full_workflow = False
            print("📌 使用简化两轮模式")
        
        if "--analyze" in sys.argv:
            analyze_decision_logs()
            sys.exit(0)
    
    # 启动主程序
    main(use_full_workflow=use_full_workflow, use_local_only=use_local_only)
