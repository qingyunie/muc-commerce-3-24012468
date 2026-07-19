from pathlib import Path

import pandas as pd


def answer_question(base_dir: Path, question: str) -> str:
    data_dir = base_dir / "data"
    metrics_df = pd.read_csv(data_dir / "overall_metrics.csv", encoding="utf-8-sig")
    metrics = dict(zip(metrics_df["指标"], metrics_df["数值"]))
    normalized = question.replace(" ", "").lower()

    # 1. 总体规模
    if any(word in normalized for word in ["多少用户", "用户数", "总用户"]):
        return f"数据集中共有{int(metrics['用户数']):,}名用户。"

    #  4-1：补充"流失率""偏好品类""生命周期风险"和"订单"四类问答。
    # 每个回答都必须引用data目录中已经计算的指标，不得编造数值。

    # 2. 流失情况
    if any(word in normalized for word in ["流失率", "流失情况", "流失比例", "多少流失"]):
        churn_rate = metrics['总体流失率']
        churn_count = int(metrics['流失人数'])
        return f"总体流失率为{churn_rate:.2%}，共有{churn_count:,}名用户流失。"

    # 3. 偏好品类
    if any(word in normalized for word in ["品类", "偏好品类", "哪个品类", "最多用户"]):
        category_df = pd.read_csv(data_dir / "category_analysis.csv", encoding="utf-8-sig")
        top_row = category_df.loc[category_df['用户数'].idxmax()]
        cat_name = top_row['PreferedOrderCat']
        cat_users = int(top_row['用户数'])
        return f"用户最多的偏好品类是「{cat_name}」，共有{cat_users:,}名用户。"

    # 4. 生命周期风险
    if any(word in normalized for word in ["生命周期", "风险最高", "哪个阶段", "阶段"]):
        segment_df = pd.read_csv(data_dir / "segment_analysis.csv", encoding="utf-8-sig")
        top_row = segment_df.loc[segment_df['流失率'].idxmax()]
        stage_name = top_row['生命周期阶段']
        stage_rate = top_row['流失率']
        return f"流失风险最高的生命周期阶段是「{stage_name}」，流失率为{stage_rate:.2%}。"

    # 5. 订单情况
    if any(word in normalized for word in ["订单", "平均订单", "订单数"]):
        avg_orders = metrics['平均订单数']
        median_orders = int(metrics['订单数中位数'])
        return f"用户平均订单数为{avg_orders:.2f}单，订单数中位数为{median_orders}单。"

    # 不支持的问题，返回友好提示
    return (
        "抱歉，我暂时无法回答这个问题。"
        "目前支持的问题类型包括：总体用户规模、流失率与流失人数、偏好品类用户数、"
        "生命周期阶段风险对比、平均订单数与订单中位数。请换一种更具体的问法试试。"
    )
