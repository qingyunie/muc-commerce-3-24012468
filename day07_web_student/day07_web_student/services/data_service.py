from pathlib import Path

import pandas as pd


def _read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, encoding="utf-8-sig")


def load_dashboard_data(base_dir: Path, selected_category: str = "全部") -> dict:
    data_dir = base_dir / "data"
    metrics_df = _read_csv(data_dir / "overall_metrics.csv")
    category_df = _read_csv(data_dir / "category_analysis.csv")
    segment_df = _read_csv(data_dir / "segment_analysis.csv")

    metric_map = dict(zip(metrics_df["指标"], metrics_df["数值"]))
    # TODO 2-1：在已有两张指标卡基础上，增加"总体流失率"和"平均订单数"。
    metrics = [
        {"label": "总用户数", "value": f"{int(metric_map['用户数']):,}", "note": "人"},
        {"label": "流失用户", "value": f"{int(metric_map['流失人数']):,}", "note": "人"},
        {"label": "总体流失率", "value": f"{metric_map['总体流失率']:.1%}", "note": ""},
        {"label": "平均订单数", "value": f"{metric_map['平均订单数']:.2f}", "note": "单"},
    ]

    categories = ["全部", *category_df["PreferedOrderCat"].tolist()]
    table_df = category_df.copy()
    # TODO 3-1：选择具体品类后筛选table_df。
    # 提示：教师参考项目中使用布尔条件筛选。
    if selected_category != "全部":
        table_df = table_df[table_df["PreferedOrderCat"] == selected_category]

    table_df = table_df.rename(
        columns={
            "PreferedOrderCat": "偏好品类",
            "用户数": "用户数",
            "流失率": "流失率",
            "平均订单数": "平均订单数",
        }
    )[["偏好品类", "用户数", "流失率", "平均订单数"]]
    table_df["流失率"] = table_df["流失率"].map(lambda value: f"{value:.1%}")
    table_df["平均订单数"] = table_df["平均订单数"].map(lambda value: f"{value:.2f}")

    # TODO 2-2：找出流失率最高的生命周期阶段，并生成一句数据观察。
    max_churn_idx = segment_df["流失率"].idxmax()
    max_stage = segment_df.loc[max_churn_idx, "生命周期阶段"]
    max_churn_rate = segment_df.loc[max_churn_idx, "流失率"]
    insight = f"数据洞察：「{max_stage}」阶段的流失率最高，达到 {max_churn_rate:.1%}，建议重点关注该阶段的用户留存策略。"

    return {
        "metrics": metrics,
        "categories": categories,
        "category_rows": table_df.to_dict("records"),
        "insight": insight,
    }


def load_segment_data(base_dir: Path) -> dict:
    """拓展B：读取 segment_analysis.csv，为生命周期详情页准备表格和观察结论。"""
    data_dir = base_dir / "data"
    segment_df = _read_csv(data_dir / "segment_analysis.csv")

    total_users = int(segment_df["用户数"].sum())
    total_churned = int(segment_df["流失人数"].sum())

    segment_rows = []
    for _, row in segment_df.iterrows():
        segment_rows.append(
            {
                "阶段": row["生命周期阶段"],
                "用户数": f"{int(row['用户数']):,}",
                "流失人数": f"{int(row['流失人数']):,}",
                "流失率": f"{row['流失率']:.1%}",
                "流失率百分比": round(float(row["流失率"]) * 100, 1),
                "平均订单数": f"{row['平均订单数']:.2f}",
                "平均满意度": f"{row['平均满意度']:.2f}",
            }
        )

    max_row = segment_df.loc[segment_df["流失率"].idxmax()]
    min_row = segment_df.loc[segment_df["流失率"].idxmin()]
    segment_insight = (
        f"「{max_row['生命周期阶段']}」阶段流失率最高，达 {max_row['流失率']:.1%}"
        f"（{int(max_row['用户数']):,} 名用户中流失 {int(max_row['流失人数']):,} 人）；"
        f"「{min_row['生命周期阶段']}」阶段流失率仅为 {min_row['流失率']:.1%}"
        f"（{int(min_row['用户数']):,} 名用户中流失 {int(min_row['流失人数']):,} 人）。"
        "用户生命周期越长留存越稳定，留存干预应优先覆盖新用户阶段。"
    )

    return {
        "segment_rows": segment_rows,
        "segment_total_users": f"{total_users:,}",
        "segment_total_churned": f"{total_churned:,}",
        "segment_insight": segment_insight,
    }
