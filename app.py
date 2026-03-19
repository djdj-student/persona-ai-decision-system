import streamlit as st
import matplotlib.pyplot as plt
import base64
from test import make_decision, parse_result, call_api
from prompt import build_judge_prompt
from personality import Personality

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
   📊 投票 & 图表卡片
   ========================= */

.block-container .stProgress,
.block-container canvas {
    background: rgba(0,0,0,0.4);
    border-radius: 12px;
    padding: 10px;
}

/* =========================
   🧠 裁判卡片（重点）
   ========================= */

[data-testid="stExpander"] {
    border: none !important;
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
# 🧱 布局
# =========================
col1, col2 = st.columns([1, 2])

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

    if st.button("🚀 开始决策"):
        st.session_state.run = True
        st.session_state.question = question

    st.markdown("---")

# =========================
# 📊 右侧
# =========================
with col2:
    if st.session_state.get("run") and st.session_state.question:

        question = st.session_state.question

        all_results = ""
        score_do = 0
        score_not = 0

        # =========================
        # 🧠 多人格执行
        # =========================
        with st.spinner("🧠 AI正在深度思考中..."):
            for p in personalities:
                result = make_decision(p, question, personalities)
                all_results += result + "\n\n"

                decision, weight, confidence, risk_score = parse_result(result)

                if risk_score >= 7 and decision == "做":
                    weight *= 0.6
                elif risk_score <= 3 and decision == "不做":
                    weight *= 0.7

                if decision == "做":
                    score_do += weight
                elif decision == "不做":
                    score_not += weight

                with st.expander(f"👤 {p.name}"):
                    st.write(result)
                    st.info(f"📊 权重: {round(weight,2)}")
                    st.success(f"💡 决策: {decision}")
                    st.warning(f"⚠️ 风险: {risk_score}")
                    st.metric("置信度", confidence)

        # =========================
        # 💥 顶部总结卡（核心）
        # =========================
        total = score_do + score_not + 0.0001
        conflict = 1 - abs(score_do - score_not) / total

        st.markdown(f"""
        <div style='
        background: linear-gradient(135deg, #111, #333);
        color: white;
        padding: 30px;
        border-radius: 20px;
        margin-bottom: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        '>
        <h1>🧠 决策结果</h1>
        <h2 style='color:#4ade80;'>👉 建议：{"做" if score_do > score_not else "不做"}</h2>
        <hr style='opacity:0.2'>
        <p>👍 做：{round(score_do,2)}</p >
        <p>👎 不做：{round(score_not,2)}</p >
        <p>⚔️ 冲突指数：{round(conflict*100)}%</p >
        </div>
        """, unsafe_allow_html=True)

        # =========================
        # 📊 投票结果
        # =========================
        st.subheader("📊 投票结果")

        st.progress(score_do / total)
        st.caption(f"👍 做：{round(score_do,2)}")

        st.progress(score_not / total)
        st.caption(f"👎 不做：{round(score_not,2)}")

        # =========================
        # 📊 图表
        # =========================
        st.subheader("📊 决策对比图")

        labels = ["DO", "NOT DO"]
        values = [score_do, score_not]

        fig, ax = plt.subplots()

        bars = ax.bar(range(len(values)), values)

# ✅ 手动设置x轴标签（解决方块问题）
        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels)

# 💥 上色
        colors = ["#4ade80", "#f87171"]
        for bar, color in zip(bars, colors):
            bar.set_color(color)

# 💥 防止看不到
        ax.set_ylim(0, max(values) + 1)

# 💥 显示数值
        for i, v in enumerate(values):
            ax.text(i, v + 0.05, f"{round(v,2)}", ha='center')

# 💥 干净UI
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        st.pyplot(fig)

        # =========================
        # 🧠 裁判系统
        # =========================
        st.subheader("🧠 最终裁判")

        with st.spinner("🧠 裁判分析中..."):
            summary = f"""
            加权结果如下：
            支持做：{round(score_do,2)}
            支持不做：{round(score_not,2)}
            
            请根据以上权重结果做出最终判断，不要使用投票人数表达
"""
            judge_prompt = build_judge_prompt(all_results + summary, question)
            judge_result = call_api(judge_prompt)

        with st.expander("📌 查看完整裁判分析"):
            st.write(judge_result)