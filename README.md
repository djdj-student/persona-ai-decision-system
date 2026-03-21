# 多人格 Agent 决策系统

这是一个“本地 Agent + 可选 LLM 验证 + 多人格博弈”的决策系统，不是一次性问答机器人。

系统目标：
1. 让决策过程可解释（每个阶段可追踪）。
2. 让人格差异可落地（不是只写在提示词里）。
3. 支持纯本地运行（不依赖 LLM 也能完成完整流程）。

## 项目结构

```text
app.py                  # Streamlit Web UI（主入口）
personality.py          # 人格数据结构
prompt.py               # 第一轮/第二轮/裁判提示词

agent_engine.py         # Stage 1 本地决策引擎
agent_reflection.py     # Stage 3 反思 + Stage 4 对话
hybrid_system.py        # 工作流编排（Stage 1~5）

test.py                 # 原始 LLM 流程与 API 工具
test_hybrid.py          # CLI 入口（混合/本地模式）

decision_logs/          # 决策日志
agent_workflows/        # 工作流导出
```

## 工作流总览

当前实现的实际流程如下：

1. Stage 1：本地初始决策（每人格独立）
2. Stage 2：LLM 验证（可选）
3. Stage 3：多轮反思（按深度档位）
4. Stage 4：人格博弈对话（三轮）
5. Stage 4.5：裁判评估系统（质量评审）
6. Stage 5：最终合成（加权决策）

说明：
- `4.5` 是独立阶段，不是装饰展示。
- 纯本地模式会跳过 Stage 2，但 Stage 1/3/4/4.5/5 仍完整执行。

## 两种运行模式

### 1) 混合模式（默认）
- Stage 1 用本地引擎给出初判。
- Stage 2 用 LLM 做“验证者”，检查人格一致性和逻辑漏洞。
- 后续阶段继续本地执行。

### 2) 纯本地模式（推荐调试）
- 不调用 LLM。
- 依然保留反思、博弈、裁判、最终合成。
- 适合验证“Agent 逻辑本身是否成立”。

## 反思深度档位（真实差异）

不是仅标签差异，而是执行轮次和方法差异：

- `quick`: Round 1（质疑初始决策）
- `standard`: Round 1 + Round 2（深入分析）
- `deep`: Round 1 + Round 2 + Round 3（魔鬼代言人）
- `expert`: deep 全部 + Round 4（预演失败/补救策略）

## Stage 4 对话机制（已去模板化）

当前 Stage 4 不再是固定模板互喷，逻辑如下：

1. Round 1：人格 A 先陈述立场。
2. Round 2：人格 B 读取 A 的文本，抽取主张后定点反驳。
3. Round 3：人格 A 读取 B 的反驳，再做针对性回应。

新增机制：
- 对方观点抽取（控制/道德/快乐/虚无/风险）。
- 基于提取结果的人格化打击句生成。
- 反驳内容会引用“上一轮说了什么”，不是重复口号。

## Stage 4.5 裁判评估系统

裁判阶段会给出：
1. 投票统计（支持做/不做）。
2. 每人格评估项：
   - 逻辑一致性
   - 现实性
   - 偏见程度
   - 综合评分
3. 最佳人格与最差人格（含原因）。
4. 裁判建议（偏向做 / 偏向不做 / 意见分裂）。

## Stage 5 最终合成

最终决策不是“票数最多即通过”，而是加权合成：

- 每人格贡献由 `weight` 与 `confidence` 共同影响。
- 输出包含：
  - 最终建议（做/不做）
  - 冲突指数
  - 支持做/不做的加权分数

## 人格参数（核心）

每个人格由以下参数驱动：
- `risk`: 风险偏好
- `emotion`: 情绪强度
- `logic`: 理性程度
- `worldview`: 世界观
- `decision_style`: 决策风格
- `tone`: 语言气质

这些参数会进入本地决策、反思、博弈，不只是展示文本。

## 提示词系统（prompt.py）

当前提示词已强化：
1. 去 AI 口吻协议（禁止模型腔、分析腔）。
2. 人格锁定指令（禁止混人格）。
3. 四人格台词锚点与禁用偏离。
4. 第一轮/第二轮/裁判模板分离。
5. 数值约束（风险评分、信心、权重区间）。

## Web UI 说明（app.py）

页面主要区域：
1. 输入区：问题、纯本地开关、反思深度。
2. Stage 1-3：详细可追踪过程（已增强细节）。
3. Stage 4：多人格博弈竞技场（三线对决展示）。
4. Stage 4.5：裁判评估面板。
5. Stage 5：最终建议与加权分数。

UI 现已做深色高对比卡片样式：
- 指标卡、表格、裁判卡、最终建议块都统一可读性风格。

## 快速开始

## 1. 环境变量

在项目根目录创建 `.env`：

```env
DEEPSEEK_API_KEY=your_api_key
```

## 2. 安装依赖

```bash
pip install streamlit requests python-dotenv matplotlib
```

## 3. 启动 Web

```bash
streamlit run app.py --server.port 8501
```

## 4. CLI 运行

```bash
# 完整流程
python test_hybrid.py

# 纯本地模式
python test_hybrid.py --local-only

# 简化模式
python test_hybrid.py --simple

# 历史分析
python test_hybrid.py --analyze
```

## 常见问题

### Q1: 纯本地模式有意义吗？
有。纯本地模式会跳过 LLM 验证，但反思、博弈、裁判、合成都正常执行，用于验证 Agent 逻辑本体。

### Q2: 深度档位真的有差异吗？
有。`quick/standard/deep/expert` 对应不同反思轮数与方法，`expert` 额外执行预演失败。

### Q3: Stage 4 还会模板化吗？
已做上下文化反驳，第二轮和第三轮会读取上一轮文本后再反击，不再是纯套模板。

### Q4: 为什么有时混合和本地结果不同？
混合模式多了 Stage 2 验证信号，可能影响后续稳定性与最终权重合成。

## 版本备注

当前 README 对应“已落地版本”的实际行为，重点包括：
- Stage 4.5 裁判系统
- expert 第四轮反思
- Stage 4 上下文感知反驳
- Stage 4.5/5 高对比 UI
