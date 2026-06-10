#!/usr/bin/env python3
"""
大力点评 CSV → investor-scout 知识库蒸馏脚本
将原始 founder 评价聚合、脱敏、委婉化后写入 knowledge-base/

用法: python3 scripts/distill_reviews.py [--csv PATH] [--output-dir PATH]

脱敏规则:
- 不保留 founder 原文
- S/A 级评价 → 提取优点模式
- B/C 级评价 → 委婉化为风格提示（绝不出现攻击性措辞）
- 评分分布作为可信度信号
"""

import csv
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

# 默认路径
SCRIPT_DIR = Path(__file__).parent
SKILL_DIR = SCRIPT_DIR.parent
DEFAULT_CSV = SKILL_DIR.parent.parent.parent / "大力点评合订本.csv"
DEFAULT_OUTPUT = SKILL_DIR / "knowledge-base"


def load_csv(csv_path):
    rows = []
    with open(csv_path, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("姓名") and row.get("投资机构"):
                rows.append(row)
    return rows


def score_label(score):
    return {"S": "极佳", "A": "良好", "B": "中等", "C": "较差"}.get(score, "未评")


def euphemize_negative(texts, scores_pro, scores_help, scores_friendly):
    """将 B/C 级评价蒸馏为委婉风格描述"""
    patterns = []

    negative_keywords = {
        "傲慢": "沟通风格偏强势",
        "拽": "态度较为直接",
        "不礼貌": "沟通方式较为直率",
        "pua": "交流中可能施加较大压力",
        "PUA": "交流中可能施加较大压力",
        "不懂装懂": "对部分领域理解深度有限",
        "泄密": "信息保密意识需关注",
        "套信息": "可能更关注行业信息收集",
        "学习": "可能处于行业学习阶段",
        "浪费时间": "会议效率反馈不一",
        "拖": "决策节奏偏慢",
        "没回复": "跟进响应速度较慢",
        "不回": "跟进响应速度较慢",
        "敷衍": "深度参与程度有限",
        "看不懂": "对该方向理解可能有限",
        "自大": "自信度较高，沟通风格强势",
        "戾气": "沟通氛围偏紧张",
        "rude": "直接程度较高",
        "刁难": "提问风格偏尖锐",
    }

    for text in texts:
        if not text:
            continue
        for keyword, euphemism in negative_keywords.items():
            if keyword in text and euphemism not in patterns:
                patterns.append(euphemism)

    # 从打分维度补充
    c_count_pro = sum(1 for s in scores_pro if s == "C")
    c_count_help = sum(1 for s in scores_help if s == "C")
    c_count_friendly = sum(1 for s in scores_friendly if s == "C")

    if c_count_pro > len(scores_pro) * 0.4 and "对部分领域理解深度有限" not in patterns:
        patterns.append("专业深度评价分化")
    if c_count_friendly > len(scores_friendly) * 0.4 and "沟通风格偏强势" not in patterns:
        patterns.append("沟通友好度评价分化")

    return patterns[:4]


def extract_positives(texts):
    """从 S/A 级评价提取优点模式"""
    patterns = []
    positive_keywords = {
        "专业": "专业度高，能深入理解技术和业务",
        "nice": "态度友好，沟通体验好",
        "认真": "认真倾听，关注细节",
        "快": "决策效率高",
        "帮忙": "愿意提供实质帮助和资源",
        "介绍": "愿意帮忙做行业引荐",
        "资源": "能提供实际资源对接",
        "深": "对行业有深度理解",
        "sharp": "思维敏锐，提问有深度",
        "鼓励": "对创始人有正向激励",
        "honest": "反馈坦诚直接",
        "坦诚": "反馈坦诚直接",
        "有价值": "交流能带来实际收获",
        "建议": "能给出有建设性的建议",
        "懂": "对赛道有真实认知",
    }

    for text in texts:
        if not text:
            continue
        for keyword, desc in positive_keywords.items():
            if keyword in text and desc not in patterns:
                patterns.append(desc)

    return patterns[:5]


def generate_institution_md(org_name, reviews):
    """生成机构级蒸馏文件"""
    total = len(reviews)
    score_dist = defaultdict(int)
    for r in reviews:
        score_dist[r["评分"]] += 1

    s_pct = round(score_dist.get("S", 0) / total * 100)
    a_pct = round(score_dist.get("A", 0) / total * 100)
    b_pct = round(score_dist.get("B", 0) / total * 100)
    c_pct = round(score_dist.get("C", 0) / total * 100)

    # 正面评价
    positive_texts = [r["文本评价"] for r in reviews if r["评分"] in ("S", "A")]
    positives = extract_positives(positive_texts)

    # 负面评价委婉化
    negative_texts = [r["文本评价"] for r in reviews if r["评分"] in ("C",)]
    scores_pro = [r["专业程度"] for r in reviews if r["评分"] == "C"]
    scores_help = [r["帮助程度"] for r in reviews if r["评分"] == "C"]
    scores_friendly = [r["友好程度"] for r in reviews if r["评分"] == "C"]
    cautions = euphemize_negative(negative_texts, scores_pro, scores_help, scores_friendly)

    # 汇总个人
    investors = defaultdict(list)
    for r in reviews:
        investors[r["姓名"]].append(r)

    md = f"""# {org_name}

## Founder 口碑摘要

> 基于 {total} 位 founder 的匿名反馈（{min(r['创建时间'] for r in reviews if r['创建时间'])} ~ {max(r['创建时间'] for r in reviews if r['创建时间'])}）

**评分分布**：S {s_pct}% · A {a_pct}% · B {b_pct}% · C {c_pct}%

"""

    if positives:
        md += "**亮点**：\n"
        for p in positives:
            md += f"- {p}\n"
        md += "\n"

    if cautions:
        md += "**需注意**：\n"
        for c in cautions:
            md += f"- {c}\n"
        md += "\n"

    # 投资人列表
    if len(investors) > 1:
        md += "## 团队成员口碑\n\n"
        md += "| 投资人 | 评价数 | 评分分布 | 风格关键词 |\n"
        md += "|--------|--------|---------|----------|\n"

        for name, revs in sorted(investors.items(), key=lambda x: -len(x[1])):
            n = len(revs)
            dist = defaultdict(int)
            for r in revs:
                dist[r["评分"]] += 1
            dist_str = "/".join(f"{k}{v}" for k, v in sorted(dist.items()) if v > 0)

            # 简短风格关键词
            pos_texts = [r["文本评价"] for r in revs if r["评分"] in ("S", "A")]
            neg_texts = [r["文本评价"] for r in revs if r["评分"] == "C"]
            keywords = []
            if pos_texts:
                kw = extract_positives(pos_texts)[:2]
                keywords.extend(kw)
            if neg_texts:
                kw = euphemize_negative(neg_texts, [], [], [])[:1]
                keywords.extend(kw)

            kw_str = "；".join(keywords[:2]) if keywords else "—"
            md += f"| {name} | {n} | {dist_str} | {kw_str} |\n"

    return md


def generate_investor_md(name, org, reviews):
    """生成个人投资人蒸馏文件"""
    total = len(reviews)
    score_dist = defaultdict(int)
    for r in reviews:
        score_dist[r["评分"]] += 1

    positive_texts = [r["文本评价"] for r in reviews if r["评分"] in ("S", "A")]
    negative_texts = [r["文本评价"] for r in reviews if r["评分"] in ("C",)]
    scores_pro = [r["专业程度"] for r in reviews]
    scores_help = [r["帮助程度"] for r in reviews]
    scores_friendly = [r["友好程度"] for r in reviews]

    positives = extract_positives(positive_texts)
    cautions = euphemize_negative(negative_texts, scores_pro, scores_help, scores_friendly)

    # 综合评级
    avg_score = (score_dist.get("S", 0) * 4 + score_dist.get("A", 0) * 3 +
                 score_dist.get("B", 0) * 2 + score_dist.get("C", 0) * 1) / total
    if avg_score >= 3.5:
        overall = "口碑优秀"
    elif avg_score >= 2.5:
        overall = "口碑良好"
    elif avg_score >= 1.8:
        overall = "口碑中等"
    else:
        overall = "需谨慎评估"

    dist_str = " · ".join(f"{k} {v}条" for k, v in sorted(score_dist.items()) if v > 0)

    md = f"""# {name}

**所在机构**：{org}
**Founder 评价数**：{total} 条（{dist_str}）
**综合口碑**：{overall}

"""

    if positives:
        md += "## 亮点\n\n"
        for p in positives:
            md += f"- {p}\n"
        md += "\n"

    if cautions:
        md += "## 需注意\n\n"
        for c in cautions:
            md += f"- {c}\n"
        md += "\n"

    # 维度评分
    pro_a = sum(1 for s in scores_pro if s in ("S", "A"))
    help_a = sum(1 for s in scores_help if s in ("S", "A"))
    friend_a = sum(1 for s in scores_friendly if s in ("S", "A"))

    md += "## 维度评分\n\n"
    md += f"| 维度 | 好评率 |\n"
    md += f"|------|--------|\n"
    md += f"| 专业程度 | {round(pro_a/total*100)}% |\n"
    md += f"| 帮助程度 | {round(help_a/total*100)}% |\n"
    md += f"| 友好程度 | {round(friend_a/total*100)}% |\n"

    return md


def sanitize_filename(name):
    return re.sub(r'[<>:"/\\|?*\s]', '_', name).strip('_')


def main():
    csv_path = sys.argv[1] if len(sys.argv) > 1 else str(DEFAULT_CSV)
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_OUTPUT

    if not os.path.exists(csv_path):
        print(f"[!] CSV 文件不存在: {csv_path}")
        print(f"    请将 大力点评合订本.csv 放到 skill 上级目录，或指定路径:")
        print(f"    python3 {sys.argv[0]} /path/to/大力点评合订本.csv")
        sys.exit(1)

    print(f"[+] 读取: {csv_path}")
    rows = load_csv(csv_path)
    print(f"[+] 共 {len(rows)} 条评价")

    # 按机构分组
    by_org = defaultdict(list)
    for r in rows:
        by_org[r["投资机构"]].append(r)

    # 按投资人分组
    by_person = defaultdict(list)
    for r in rows:
        key = (r["姓名"], r["投资机构"])
        by_person[key].append(r)

    # 生成机构文件（≥5 条评价）
    inst_dir = output_dir / "institutions"
    inst_dir.mkdir(parents=True, exist_ok=True)

    inst_count = 0
    for org, revs in sorted(by_org.items(), key=lambda x: -len(x[1])):
        if len(revs) < 5:
            continue
        filename = sanitize_filename(org) + ".md"
        md = generate_institution_md(org, revs)
        (inst_dir / filename).write_text(md, encoding="utf-8")
        inst_count += 1

    print(f"[+] 生成机构文件: {inst_count} 个 → {inst_dir}/")

    # 生成投资人文件（≥3 条评价）
    inv_dir = output_dir / "investors"
    inv_dir.mkdir(parents=True, exist_ok=True)

    inv_count = 0
    for (name, org), revs in sorted(by_person.items(), key=lambda x: -len(x[1])):
        if len(revs) < 3:
            continue
        filename = sanitize_filename(f"{name}_{org}") + ".md"
        md = generate_investor_md(name, org, revs)
        (inv_dir / filename).write_text(md, encoding="utf-8")
        inv_count += 1

    print(f"[+] 生成投资人文件: {inv_count} 个 → {inv_dir}/")
    print(f"\n=== 蒸馏完成 ===")
    print(f"机构: {inst_count} 个 | 投资人: {inv_count} 个")
    print(f"所有输出已脱敏，不含 founder 原文。")


if __name__ == "__main__":
    main()
