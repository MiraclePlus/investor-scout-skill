# Investor Scout — Founder 融资准备 AI 参谋

帮 Founder 搞清楚"该见谁、怎么准备、怎么应对"。

## 功能

| 功能 | 输入 | 输出 |
|------|------|------|
| 投资人筛选 | 赛道 + 阶段 + 金额 | 5-10 个匹配推荐，C/B/A 分级 |
| 投资人背调 | 机构或投资人姓名 | 结构化画像（偏好/案例/风格/口碑） |
| 会议准备 | "我要见 XX" | 定制化准备清单（预判问题 + 建议回答） |
| 融资策略 | 深层问题 | 框架性分析 + 建议确认方向 |

## 使用方法

安装到你的 Claude Code workspace（放入 `.claude/skills/investor-scout/` 目录），然后直接对话：

```
帮我找适合 AI 应用赛道 Pre-A 阶段的投资人
背调真格基金
我下周要见线性资本，帮我准备
我该什么时候开始融资？
```

## 目录结构

```
investor-scout/
├── SKILL.md                    # Skill 定义（触发词、行为规则、执行流程）
├── README.md                   # 本文件
├── references/                 # 融资方法论（面向 founder 的通识知识）
│   ├── fundraising-playbook.md   # 核心框架：Promise→Proof、Ready Scorecard
│   ├── fundraising-faq.md        # 融资常见问题应答策略
│   └── fundraising-methodology.md # 融资 OS：排/聊/推/谈
└── knowledge-base/             # 投资人/机构数据
    ├── INDEX.md                  # 快速筛选索引
    ├── institutions/             # 机构详情（每家一个文件）
    ├── investors/                # 个人投资人详情
    └── signals/                  # 脱敏 founder 口碑
```

## 在线阅读（飞书文档）

以下资料已上传为飞书公开文档，可直接在线浏览：

| 文档 | 飞书链接 |
|------|---------|
| 融资圆桌 Q&A（5 位校友实战经验） | [在线阅读](https://miracleplus.feishu.cn/docx/XJngdjSQaorhIQxqX9pcZXwBncg) |
| pre-PP 路演 PPT 制作指南 | [在线阅读](https://miracleplus.feishu.cn/docx/Kl0MdUcP0o7FajxEh11cKr1GnLg) |
| S26 融资指南 — 如何融第二笔钱 Playbook | [在线阅读](https://miracleplus.feishu.cn/wiki/NGdlwoLcBiM4WukTt5VcSwAEnNd) |

## 方法论来源

本 skill 的融资方法论基于以下公开资料提炼：

1. **《奇绩创坛 S26 融资指南 — 如何融第二笔钱 Playbook》**
   - 核心模型：Promise → Proof 的状态转移
   - Ready Scorecard（融资准备度 5 维自检）
   - 融资方案设计公式（Burn × Runway + Buffer）
   - Demo Day 前/中/后 Playbook
   - 融资 OS（排/聊/推/谈四步法）
   - 2026 资本地图（财务 VC / 国资 / CVC / 海外 / 并购型）

2. **融资 FAQ**（30+ 高频问题）
   - 与投资人对话技巧
   - 找谁融资的选择框架
   - 投资条款和流程应对

## 知识库 Schema

如果你想扩展自己的投资人数据，参考 `knowledge-base/institutions/template.md`：

```yaml
机构名称:
基金规模:
币种: 美元/人民币/双币
投资阶段: [天使, 种子, Pre-A, A, B]
赛道偏好: [AI, 硬科技, 消费, 企服, 医疗, ...]
Check Size: $XM-$YM
决策风格: 快刀斩乱麻/深度尽调型/委员会制
代表Portfolio: [{项目, 赛道, 轮次, 年份}]
红旗信号: (如有)
```

## 行为准则

- 基于知识库真实信息回答，不编造
- 信息不确定时明确标注"待确认"
- 负面信息如实呈现，不替投资人洗白
- 不替 founder 做决策，给框架和参考
- 不透露其他项目信息

## 数据脱敏原则

- 公开信息（portfolio、基金规模）：直接使用
- Founder 反馈：蒸馏为风格描述，不保留原文
- 红旗信号：中性描述，不暴露来源
- 内部关系：仅标注"有合作历史"级别

## 贡献

欢迎补充投资人数据：
1. 在 `knowledge-base/institutions/` 或 `investors/` 下新建 md 文件
2. 按模板填写信息
3. 在 `INDEX.md` 中添加索引条目

---

> 本 Skill 由 MiraclePlus CC 团队维护，融资方法论部分基于奇绩创坛公开课程内容。
