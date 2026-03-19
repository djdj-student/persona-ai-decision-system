class Personality:
    def __init__(self, name, risk, emotion, logic, worldview, decision_style, tone):
        self.name = name                # 名字
        self.risk = risk                # 风险偏好
        self.emotion = emotion          # 情绪强度
        self.logic = logic              # 理性程度
        
        # 🔥 新增（核心）
        self.worldview = worldview      # 世界观（怎么看世界）
        self.decision_style = decision_style  # 决策方式（怎么做决定）
        self.tone = tone                # 说话风格（怎么表达）