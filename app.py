import re
import streamlit as st
import matplotlib.pyplot as plt
import base64
# 从 test.py 导入核心逻辑
from test import run_multi_round_decision, parse_result, call_api 
# 如果 app.py 也要用到这些函数，才需要在这里导入
from prompt import build_judge_prompt, build_debate_prompt 
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
    background: rgba(255, 255, 255, 0.85);
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

        with st.spinner("🧠 AI正在深度思考中..."):
            result = run_multi_round_decision(question, personalities)

        # =========================
        # 🧠 第一轮
        # =========================
        st.header("🧠 第一轮决策")

        for name, r in result["round1"]:
            decision, weight, confidence, risk_score = parse_result(r)

            with st.expander(f"👤 {name}（第一轮）"):
                st.write(r)
                st.info(f"📊 权重: {round(weight,2)}")
                st.success(f"💡 决策: {decision}")
                st.warning(f"⚠️ 风险: {risk_score}")
                st.metric("置信度", confidence)

        # =========================
        # ⚔️ 第二轮
        # =========================
        st.header("⚔️ 第二轮博弈")

        for name, r in result["round2"]:
            decision, weight, confidence, risk_score = parse_result(r)

            with st.expander(f"🔥 {name}（第二轮）"):
                st.write(r)
                st.info(f"📊 权重: {round(weight,2)}")
                st.success(f"💡 决策: {decision}")
                st.warning(f"⚠️ 风险: {risk_score}")
                st.metric("置信度", confidence)

   # =========================
        # 📊 投票结果
        # =========================
        st.subheader("📊 投票结果")
        summary_text = result.get("summary", "")
        st.text(summary_text)

        # --- 这里的解析逻辑也改为“关键词搜索”，防止 IndexError ---
        import re
        do_score = 0.0
        not_score = 0.0
        
        for line in summary_text.split("\n"):
            clean_line = line.replace("：", ":").strip()
            if "支持做:" in clean_line:
                nums = re.findall(r"\d+\.?\d*", clean_line) # 提取浮点数
                if nums: do_score = float(nums[0])
            elif "支持不做:" in clean_line:
                nums = re.findall(r"\d+\.?\d*", clean_line)
                if nums: not_score = float(nums[0])

        # =========================
        # 📊 图表展示 (加权分数)
        # =========================
        st.subheader("📊 决策加权对比图")
        
        labels = ["DO", "NOT DO"]
        values = [do_score, not_score]

        fig, ax = plt.subplots(figsize=(8, 4))
        # 使用更专业的颜色：绿色代表做，红色代表不做
        colors = ['#2ecc71', '#e74c3c']
        bars = ax.bar(labels, values, color=colors)

        # 在柱状图顶部标数字
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                    f'{height:.2f}', ha='center', va='bottom', fontweight='bold')

        ax.set_ylabel('weighted score')
        st.pyplot(fig)

        # =========================
        # 🧠 裁判系统 (人数统计)
        # =========================
        st.subheader("🧠 最终裁判")

        with st.spinner("🧠 裁判分析中..."):
            judge_result = result.get("final", "裁判未给出结论")

        # 健壮的裁判人数解析逻辑
        do_count = 0
        not_count = 0
        
        for line in judge_result.split("\n"):
            clean_line = line.replace("：", ":").strip()
            # 匹配“做: 3人”或者“做:3”
            if "做:" in clean_line and "不做" not in clean_line:
                nums = re.findall(r"\d+", clean_line)
                if nums: do_count = int(nums[0])
            elif "不做:" in clean_line:
                nums = re.findall(r"\d+", clean_line)
                if nums: not_count = int(nums[0])

        # 2. 详情展开
        with st.expander("📌 查看完整裁判分析手册"):
            st.info("📊 投票汇总对比")
            st.write(summary_text)
            st.divider()
            st.warning("⚖️ 最终裁决书")
            st.markdown(judge_result)
