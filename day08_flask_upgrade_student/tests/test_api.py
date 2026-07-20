"""第8天Flask接口测试：覆盖/health、登录拦截、指标API、品类筛选与统一错误响应。"""

import sys
from pathlib import Path

import pytest

# 让测试可以直接从项目根目录导入app.py。
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import app as flask_app  # noqa: E402


@pytest.fixture()
def client():
    flask_app.config.update(TESTING=True)
    return flask_app.test_client()


def login(client):
    """使用演示账号完成登录。"""
    return client.post("/login", data={"username": "student", "password": "day07"})


def test_health_returns_200(client):
    """/health 无需登录，返回200且ok为True。"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json()["ok"] is True


def test_metrics_requires_login(client):
    """未登录访问/api/metrics会被拦截并重定向到登录页。"""
    response = client.get("/api/metrics")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_metrics_after_login(client):
    """登录后/api/metrics返回ok和四张指标卡，数值来自数据服务。"""
    login(client)
    response = client.get("/api/metrics")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["ok"] is True
    assert len(payload["metrics"]) == 4
    for card in payload["metrics"]:
        assert set(card.keys()) == {"label", "value", "note"}
    # 数值来自overall_metrics.csv：用户数5630 -> "5,630"
    assert payload["metrics"][0] == {"label": "总用户数", "value": "5,630", "note": "人"}


def test_categories_filter(client):
    """category参数真正进入筛选逻辑：Fashion只返回1行，全部返回5行。"""
    login(client)
    all_payload = client.get("/api/categories").get_json()
    fashion_payload = client.get("/api/categories?category=Fashion").get_json()

    assert all_payload["ok"] is True
    assert len(all_payload["rows"]) == 5

    assert fashion_payload["ok"] is True
    assert fashion_payload["category"] == "Fashion"
    assert len(fashion_payload["rows"]) == 1
    assert fashion_payload["rows"][0]["偏好品类"] == "Fashion"
    # 筛选结果与全量结果有可解释的差异
    assert fashion_payload["rows"] != all_payload["rows"]


def test_invalid_category_returns_400_json(client):
    """不存在的品类返回统一的400错误JSON，不用200伪装失败。"""
    login(client)
    response = client.get("/api/categories?category=不存在的品类")
    assert response.status_code == 400
    payload = response.get_json()
    assert payload["ok"] is False
    assert payload["error"] == "请求格式不正确。"