import pytest
from src.logic.equipment_box import validate_restoration_bonuses, normalize_bonus

def test_validate_restoration_bonuses_valid():
    """正常系: 同一ボーナスが2つまでの場合"""
    bonuses = [
        {"type": "基礎攻撃力強化", "level": "Ⅱ"},
        {"type": "基礎攻撃力強化", "level": "Ⅱ"},
        {"type": "切れ味強化", "level": "Ⅰ"}
    ]
    is_valid, msg = validate_restoration_bonuses(bonuses)
    assert is_valid
    assert msg == ""

def test_validate_restoration_bonuses_invalid_triple():
    """異常系: 同一ボーナスが3つ以上の場合"""
    bonuses = [{"type": "基礎攻撃力強化", "level": "Ⅱ"}] * 3
    is_valid, msg = validate_restoration_bonuses(bonuses)
    assert not is_valid
    # エラーメッセージ内に該当のボーナス名が含まれているか（日本語）
    assert "Validation Error" in msg
    assert "攻撃[Ⅱ]" in msg 

def test_normalize_bonus_japanese_behavior():
    """日本語用語の正規化とタプル形式の検証"""
    # 基礎攻撃力強化 -> 基礎攻撃力強化 (is_restoration=True)
    nt, nl = normalize_bonus("基礎攻撃", "2.0", is_restoration=True)
    assert nt == "基礎攻撃力強化"
    assert nl == "Ⅱ"

    # 属性 -> 属性強化
    nt, nl = normalize_bonus("属性", "3")
    assert nt == "属性強化"
    assert nl == "Ⅲ"
