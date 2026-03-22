import streamlit as st
import base64
from test import call_api
from personality import Personality
from hybrid_system import HybridDecisionSystem

# =========================
# 🎨 页面配置
# =========================
st.set_page_config(page_title="AI决策系统", layout="wide")

# =========================
# 🎨 背景加载
# =========================
def get_base64(file):
    with open(file, "rb") as f:
        return base64.b64encode(f.read()).decode()

bg = get_base64("bg.jpg")

# =========================
# 🎨 顶级UI样式
# =========================
st.markdown(f"""
<style>

:root {{
    --narrow-width: 860px;
}}

/* 🌄 背景：清晰 + 微暗 */
.stApp {{
    background-image: url("data:image/jpg;base64,{bg}");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}}

/* 🔥 全局暗层（提升高级感） */
.stApp::before {{
    content: "";
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0,0,0,0.2);
    z-index: 0;
}}

/* 🧱 内容区域（不再玻璃！） */
.block-container {{
    position: relative;
    z-index: 1;
    padding-top: 2rem;
    max-width: 1200px;
    margin: 0 auto;
    text-align: center;
}}

/* 输入区与按钮居中 */
div[data-testid="stTextArea"], div[data-testid="stTextInput"] {{
    max-width: var(--narrow-width);
    margin: 0 auto;
}}

div[data-testid="stTextArea"] textarea {{
    text-align: left;
}}

div[data-testid="stButton"] {{
    display: flex;
    justify-content: center;
}}

div[data-testid="stButton"] > button {{
    margin: 0 auto;
    display: block;
}}

/* 隐藏输入框右下角英文提示（如 Press Ctrl+Enter to apply） */
div[data-testid="InputInstructions"] {{
    display: none !important;
}}

/* 全局文字居中 */
h1, h2, h3, h4, h5, h6, p, label, .stMarkdown, .stCaption {{
    text-align: center !important;
}}

/* 💎 卡片统一风格 */
.card {{
    background: white;
    padding: 20px;
    border-radius: 16px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.15);
    margin-bottom: 20px;
}}

/* 标题 */
h1 {{
    font-size: 36px;
    font-weight: 700;
    color: white;
}}

/* 副标题 */
span {{
    color: rgba(255,255,255,0.8);
}}

/* 按钮 */
.stButton>button {{
    border-radius: 12px;
    background: #111;
    color: white;
    font-weight: 600;
}}

.stButton>button:hover {{
    background: #333;
}}

</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>

/* 🔥 干掉顶部所有东西 */
header {visibility: hidden;}
.stAppToolbar {display: none;}
.stDecoration {display: none;}

/* 有些版本还需要这个 */
[data-testid="stHeader"] {display: none;}
[data-testid="stToolbar"] {display: none;}

/* 全局字体白色 */
body {
    color: white;
}

/* Streamlit组件文字 */
.stMarkdown, .stText, .stSubheader, .stCaption {
    color: white !important;
}

/* Spinner文字 */
.stSpinner > div {
    color: white !important;
}

/* 顶部间距修复 */
.block-container {
    padding-top: 0rem;
}

</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>

/* =========================
   💥 黑色半透明卡片系统（核心）
   ========================= */

/* 👤 人格卡片 */
.stExpander {
    background: rgba(0, 0, 0, 0.6) !important;
    border-radius: 16px !important;
    padding: 12px !important;
    margin-bottom: 12px !important;
    backdrop-filter: blur(8px);
    border: 1px solid rgba(255,255,255,0.1);
}

/* 展开内容 */
.stExpanderContent {
    background: rgba(0, 0, 0, 0.65) !important;
    border-radius: 12px !important;
}

/* expander 标题 */
.stExpander summary {
    color: white !important;
    font-weight: 600;
}

/* expander 内容文字 */
.stExpander p,
.stExpander div,
.stExpander span {
    color: white !important;
}

/* =========================
   🧠 裁判卡片（重点）
   ========================= */

[data-testid="stExpander"] {
    border: none !important;
    max-width: var(--narrow-width) !important;
    margin-left: auto !important;
    margin-right: auto !important;
}

/* =========================
   🏁 最终建议（你HTML卡片 already OK）
   ========================= */

/* 如果你还用 st.success / st.error */
.stAlert {
    background: rgba(0,0,0,0.6) !important;
    color: white !important;
    border-radius: 12px !important;
}

/* =========================
   📈 Stage 4.5 / Stage 5 可读性增强
   ========================= */

/* metric 卡片（支持『做』/评分等） */
[data-testid="stMetric"] {
    background: rgba(0, 0, 0, 0.62) !important;
    border: 1px solid rgba(255, 255, 255, 0.14) !important;
    border-radius: 14px !important;
    padding: 14px 12px !important;
}

[data-testid="stMetricLabel"] p,
[data-testid="stMetricValue"] {
    color: #ffffff !important;
}

/* 表格容器和单元格 */
[data-testid="stTable"] table {
    background: rgba(0, 0, 0, 0.62) !important;
    color: #ffffff !important;
    border-radius: 12px !important;
    overflow: hidden !important;
}

[data-testid="stTable"] th,
[data-testid="stTable"] td {
    color: #ffffff !important;
    background: rgba(0, 0, 0, 0.52) !important;
    border-color: rgba(255, 255, 255, 0.14) !important;
}

/* dataframe（用于隐藏索引后的评估表） */
[data-testid="stDataFrame"] {
    background: rgba(0, 0, 0, 0.62) !important;
    border: 1px solid rgba(255, 255, 255, 0.14) !important;
    border-radius: 12px !important;
}

[data-testid="stDataFrame"] * {
    color: #ffffff !important;
}

/* 最佳/最差人格卡片 */
.judge-card {
    background: rgba(0, 0, 0, 0.62);
    border: 1px solid rgba(255, 255, 255, 0.14);
    border-radius: 14px;
    padding: 14px 16px;
    margin-bottom: 10px;
}

.judge-card-title {
    font-size: 18px;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 8px;
}

.judge-card-main {
    font-size: 20px;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 6px;
}

.judge-card-line {
    font-size: 14px;
    color: rgba(255, 255, 255, 0.95);
    margin: 3px 0;
}

/* info/success/error 提示块统一高对比 */
[data-testid="stAlert"] {
    background: rgba(0, 0, 0, 0.62) !important;
    color: #ffffff !important;
    border: 1px solid rgba(255,255,255,0.14) !important;
}

[data-testid="stAlert"] * {
    color: #ffffff !important;
}

</style>
""", unsafe_allow_html=True)

# =========================
# 🧠 标题
# =========================
st.markdown("""
# 🧠 多人格AI决策系统
<span style='color:gray'>模拟不同人格博弈，生成更接近真实世界的决策</span>
""", unsafe_allow_html=True)

# =========================
# 🧠 人格定义
# =========================
personalities = [
    Personality(
        "夜神月", 0.9, 0.3, 0.95,
        "世界可以被我控制和优化",
        "追求最优解，不惜代价达成目标",
        "冷静、压迫感、优越感"
    ),
    Personality(
        "蜡笔小新", 0.8, 0.9, 0.2,
        "世界就是用来开心的",
        "凭感觉做决定，开心就做",
        "随便、搞笑、不严肃"
    ),
    Personality(
        "炭治郎", 0.4, 0.7, 0.8,
        "善恶分明，他人很重要",
        "优先道德，不伤害别人",
        "温和但坚定、真诚"
    ),
    Personality(
        "章鱼哥", 0.2, 0.3, 0.6,
        "世界没有意义，大多数事情没价值",
        "倾向否定行动，避免麻烦",
        "讽刺、冷淡、不耐烦"
    ),
]

# =========================
# 🧱 布局（单列）
# =========================
col1 = st.container()
col2 = st.container()

# =========================
# 📝 左侧
# =========================
with col1:
    st.subheader("📝 输入问题")

    if "question" not in st.session_state:
        st.session_state.question = ""

    question = st.text_area(
        "请输入你的问题",
        value=st.session_state.question,
        height=150,
        placeholder="例如：我该不该辞职创业？"
    )

    depth = "deep"

    _, center_btn_col, _ = st.columns([1, 1, 1])
    with center_btn_col:
        run_clicked = st.button("🚀 开始决策", use_container_width=True)

    if run_clicked:
        st.session_state.run = True
        st.session_state.question = question

    st.markdown("---")

# =========================
# 📊 右侧
# =========================
with col2:
    if st.session_state.get("run") and st.session_state.question:

        question = st.session_state.question
        depth = "deep"

        with st.spinner("🧠 AI正在深度思考中..."):
            system = HybridDecisionSystem(llm_call_func=call_api)
            result = system.full_decision_workflow(
                personalities=personalities,
                question=question,
                depth=depth,
                use_llm=True
            )

        st.caption(f"🔧 反思深度：{depth}")

        stages = result.get("stages", {})


        # 详细 Stage 1-3 工作流
        with st.expander("📊 工作流详情 (Stage 1-3)", expanded=True):
            # Stage 1 本地决策
            st.markdown("### 👤 Stage 1 - 各人格初始决策（本地引擎）")
            local_decisions = stages.get("1_local_decisions", {})
            for name, data in local_decisions.items():
                decision = data.get("decision", "?")
                confidence = data.get("confidence", 0)
                weight = data.get("weight", 0)
                risk_score = data.get("risk_score", 0)
                reasoning = data.get("reasoning", "")

                with st.expander(f"{name} | 初始决策：{decision}", expanded=False):
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        st.metric("置信度", f"{confidence}/10")
                    with c2:
                        st.metric("决策权重", f"{weight:.2f}")
                    with c3:
                        st.metric("风险评分", f"{risk_score}/10")

                    if reasoning:
                        st.markdown("**本地推理摘要：**")
                        st.write(reasoning)

            # Stage 2 LLM 验证
            st.markdown("### ✅ Stage 2 - LLM 验证（人格一致性检查）")
            validations = stages.get("2_llm_validations", {})
            if validations:
                for name, data in validations.items():
                    validated = data.get("validated", False)
                    status = "✅ 验证通过" if validated else "⚠️ 需要调整"
                    with st.expander(f"{name} | {status}", expanded=False):
                        full_response = data.get("full_response", "")

                        if full_response:
                            st.markdown("**LLM 详细反馈：**")
                            st.write(full_response)
            else:
                st.write("暂无 LLM 验证数据")

            # Stage 3 多轮反思
            st.markdown("### 🧠 Stage 3 - 多轮反思轨迹（Round by Round）")
            reflections = stages.get("3_reflections", {})
            for name, data in reflections.items():
                init = data.get("initial_decision", "?")
                final = data.get("final_verdict", "?")
                arrow = "→" if init != final else "═"
                confidence_evo = data.get("confidence_evolution", [])
                rounds = data.get("rounds", [])

                with st.expander(f"{name} | 决策演化：{init} {arrow} {final}", expanded=False):
                    if confidence_evo:
                        evo_text = " → ".join(str(v) for v in confidence_evo)
                        st.markdown(f"**置信度演化：** {evo_text}")

                    if rounds:
                        for round_data in rounds:
                            round_no = round_data.get("round", "?")
                            round_type = round_data.get("type", "未知类型")
                            recommendation = round_data.get("recommendation", "?")
                            conf_shift = round_data.get("confidence_shift", "?")
                            change_reason = round_data.get("change_reason", "")

                            st.markdown(f"#### Round {round_no} - {round_type}")
                            st.write(f"- 推荐决策：{recommendation}")
                            st.write(f"- 本轮置信度：{conf_shift}")

                            thought_process = round_data.get("thought_process", [])
                            if thought_process:
                                st.markdown("**思考过程：**")
                                for item in thought_process:
                                    st.write(f"- {item}")

                            potential_issues = round_data.get("potential_issues", [])
                            if potential_issues:
                                st.markdown("**发现问题：**")
                                for item in potential_issues:
                                    st.write(f"- {item}")

                            critical_questions = round_data.get("critical_questions", [])
                            if critical_questions:
                                st.markdown("**关键追问：**")
                                for item in critical_questions:
                                    st.write(f"- {item}")

                            analysis_items = round_data.get("analysis", [])
                            if analysis_items:
                                st.markdown("**深入分析：**")
                                for item in analysis_items:
                                    st.write(f"- {item}")

                            failure_simulation = round_data.get("failure_simulation", [])
                            if failure_simulation:
                                st.markdown("**失败预演：**")
                                for item in failure_simulation:
                                    st.write(f"- {item}")

                            mitigation = round_data.get("mitigation", [])
                            if mitigation:
                                st.markdown("**补救策略：**")
                                for item in mitigation:
                                    st.write(f"- {item}")

                            opposing_view = round_data.get("opposing_view", "")
                            counter_argument = round_data.get("counter_argument", "")
                            final_defense = round_data.get("final_defense", "")
                            if opposing_view:
                                st.markdown("**自我对抗（魔鬼代言人）：**")
                                st.write(f"- 反方观点：{opposing_view}")
                            if counter_argument:
                                st.write(f"- 质疑：{counter_argument}")
                            if final_defense:
                                st.write(f"- 最终辩护：{final_defense}")

                            if change_reason:
                                st.write(f"- 变化原因：{change_reason}")

                            st.divider()

        # Stage 4 多人格博弈 - 新结构：一个主决策者对其他三个人
        st.header("💬 Stage 4 - 多人格博弈竞技场")
        st.write("*每个人格都分别对阵其他三个人。展示一对一的完整对决过程。*")
        
        dialogues = stages.get("4_dialogues", {})
        
        if dialogues:
            # 提取所有独特的人格
            all_speakers = set()
            for pair in dialogues.keys():
                speakers = pair.split("_vs_")  # 改为正确的分隔符
                if len(speakers) == 2:
                    all_speakers.add(speakers[0])
                    all_speakers.add(speakers[1])
            
            all_speakers = sorted(list(all_speakers))
            
            # 为每个人格创建一个"主人公"视角
            for main_speaker in all_speakers:
                with st.expander(f"🎭 {main_speaker} 的三线对决", expanded=False):
                    st.write(f"**{main_speaker}** 同时与其他三个人格进行论战。展示其完整的论证过程。\n")
                    
                    # 找出这个主人公的所有对手
                    opponents_data = []
                    for pair, data in dialogues.items():
                        if main_speaker in pair:
                            speakers = pair.split("_vs_")  # 改为正确的分隔符
                            if len(speakers) == 2:
                                opponent = speakers[1] if speakers[0] == main_speaker else speakers[0]
                                opponents_data.append((opponent, data))
                    
                    # 按三个对手分别显示
                    for opponent, debate in opponents_data:
                        with st.expander(f"⚔️ {main_speaker} ⚔️ {opponent}", expanded=True):
                            exchanges = debate.get("exchanges", [])
                            intensity = debate.get("conflict_intensity", 0)
                            
                            # 显示冲突强度
                            if intensity > 0.7:
                                conflict_label = "⚔️🔥 强烈冲突"
                            elif intensity > 0.4:
                                conflict_label = "💢 中等冲突"
                            else:
                                conflict_label = "💬 温和讨论"
                            
                            st.write(f"**冲突强度：{conflict_label} ({intensity:.2f})**\n")
                            
                            if exchanges:
                                # 按轮次显示对话
                                for idx, exchange in enumerate(exchanges, 1):
                                    speaker = exchange.get("speaker", "未知")
                                    
                                    # 动态决定标题
                                    round_label = f"【第 {idx} 轮】"
                                    if "argument" in exchange:
                                        round_label += f"{speaker} 的初始论点"
                                        content = exchange.get("argument", "")
                                    elif "counter_argument" in exchange:
                                        other_speaker = opponent if speaker != opponent else main_speaker
                                        round_label += f"{speaker} 反驳 {other_speaker}"
                                        content = exchange.get("counter_argument", "")
                                    elif "rebuttal" in exchange:
                                        other_speaker = opponent if speaker != opponent else main_speaker
                                        round_label += f"{speaker} 的强硬回应"
                                        content = exchange.get("rebuttal", "")
                                    else:
                                        content = ""
                                    
                                    # 根据说话人着色
                                    if speaker == main_speaker:
                                        st.markdown(f"### 🟦 {round_label}")
                                        st.markdown(f"**【{speaker}】**")
                                    else:
                                        st.markdown(f"### 🟥 {round_label}")
                                        st.markdown(f"**【{speaker}】**")
                                    
                                    # 显示内容（支持多行）
                                    if isinstance(content, str) and len(content) > 200:
                                        st.markdown(content)
                                    else:
                                        st.markdown(f"> {content}")
                                    
                                    st.divider()
                            else:
                                st.write("暂无对话内容")
        else:
            st.write("暂无博弈数据")

        # Stage 4.5 裁判评估系统
        st.header("🏆 Stage 4.5 - 裁判评估系统")
        judge = stages.get("4.5_judge", {})
        
        if judge:
            # 投票统计
            col1, col2, col3 = st.columns(3)
            with col1:
                vote_do = len(judge.get("vote_summary", {}).get("做", []))
                st.metric("支持『做』", vote_do)
            with col2:
                vote_not = len(judge.get("vote_summary", {}).get("不做", []))
                st.metric("支持『不做』", vote_not)
            with col3:
                best_score = judge.get("best_personality_score", 0)
                st.metric("最佳评分", f"{best_score:.2f}/10")
            
            st.divider()
            
            # 人格质量评估表
            st.subheader("📊 个人格质量评估")
            evals = judge.get("personality_evaluations", {})
            
            # 创建评估表
            eval_data = []
            for name, eval_info in evals.items():
                eval_data.append({
                    "人格": name,
                    "决策": eval_info.get("decision", "?"),
                    "信心": f"{eval_info.get('confidence', 0)}/10",
                    "逻辑一致性": f"{eval_info.get('logic_consistency', 0):.2f}",
                    "现实性": f"{eval_info.get('realism', 0):.2f}",
                    "综合评分": f"{eval_info.get('composite_score', 0):.2f}/10"
                })
            
            st.dataframe(eval_data, use_container_width=True, hide_index=True)
            
            st.divider()
            
            # 最佳和最差
            best_col, worst_col = st.columns(2)
            
            with best_col:
                best_name = judge.get("best_personality", "未知")
                best_eval = evals.get(best_name, {})
                st.markdown(
                    f"""
                    <div class="judge-card">
                        <div class="judge-card-title">🏆 最佳人格</div>
                        <div class="judge-card-main">{best_name}</div>
                        <div class="judge-card-line">综合评分：{judge.get('best_personality_score', 0):.2f}/10</div>
                        <div class="judge-card-line">逻辑一致性：{best_eval.get('logic_consistency', 0):.2f}</div>
                        <div class="judge-card-line">决策现实性：{best_eval.get('realism', 0):.2f}</div>
                        <div class="judge-card-line">偏见程度：{best_eval.get('bias_level', 0):.2f}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            
            with worst_col:
                worst_name = judge.get("worst_personality", "未知")
                worst_eval = evals.get(worst_name, {})
                st.markdown(
                    f"""
                    <div class="judge-card">
                        <div class="judge-card-title">❌ 最差人格</div>
                        <div class="judge-card-main">{worst_name}</div>
                        <div class="judge-card-line">原因：{judge.get('worst_personality_reason', '未知')}</div>
                        <div class="judge-card-line">逻辑一致性：{worst_eval.get('logic_consistency', 0):.2f}</div>
                        <div class="judge-card-line">决策现实性：{worst_eval.get('realism', 0):.2f}</div>
                        <div class="judge-card-line">偏见程度：{worst_eval.get('bias_level', 0):.2f}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            
            st.divider()
            
            # 裁判建议
            st.info(f"🎯 **裁判建议**\n{judge.get('recommendation', '暂无建议')}")

        # Stage 5 最终合成
        st.header("🏁 Stage 5 - 最终合成")
        synthesis = stages.get("5_synthesis", {})
        final_decision = synthesis.get("final_decision", "未知")
        score_do = synthesis.get("score_do", 0)
        score_not = synthesis.get("score_not", 0)
        conflict_index = synthesis.get("conflict_index", 0)

        if final_decision == "做":
            st.success(f"🎯 最终建议：{final_decision}")
        elif final_decision == "不做":
            st.error(f"🎯 最终建议：{final_decision}")
        else:
            st.warning(f"🎯 最终建议：{final_decision}")

        st.write(f"冲突指数：{conflict_index:.1f}%")
        recommendation = synthesis.get("recommendation", "")
        if recommendation:
            st.info(recommendation)

        # 简洁的加权分数展示
        st.subheader("📊 最终加权分数")
        col_do, col_not = st.columns(2)
        with col_do:
            st.metric("支持『做』", f"{score_do:.2f}")
        with col_not:
            st.metric("支持『不做』", f"{score_not:.2f}")
