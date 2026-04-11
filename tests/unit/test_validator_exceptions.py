import pytest
from src.logic.talismans import add_talisman
from src.logic.equipment_box import add_equipment
from src.logic.equipment import register_upgrade
from src.logic.restoration_tracker import register_tracker
from src.utils.exceptions import LogicValidationError

def test_add_talisman_validation_fail():
    # Invalid rarity
    with pytest.raises(LogicValidationError) as excinfo:
        add_talisman(rarity=99, skills=[], slots=[0, 0, 0, 0])
    assert "Invalid rarity: 99" in str(excinfo.value)

def test_add_equipment_validation_fail():
    # Invalid weapon type
    with pytest.raises(LogicValidationError) as excinfo:
        add_equipment(
            weapon_name="Test", weapon_type="InvalidWeapon", element="火",
            current_series_skill="なし", current_group_skill="なし",
            enhancement_type="なし", p_bonuses=["なし"]*3, restoration_bonuses=[]
        )
    assert "無効な武器種です" in str(excinfo.value)

def test_register_upgrade_validation_fail():
    # Invalid count
    with pytest.raises(LogicValidationError) as excinfo:
        register_upgrade(weapon_type="大剣", element="火", series_skill="なし", group_skill="なし", count=0)
    assert "残り回数は1以上である必要があります" in str(excinfo.value)

def test_register_tracker_validation_fail():
    # Invalid restoration bonuses (3+ repeats)
    invalid_rbs = [
        {"type": "攻撃", "level": "Ⅰ"},
        {"type": "攻撃", "level": "Ⅰ"},
        {"type": "攻撃", "level": "Ⅰ"}
    ]
    with pytest.raises(LogicValidationError) as excinfo:
        register_tracker(weapon_id="dummy", remaining_count=1, target_bonuses=invalid_rbs)
    assert "Bonus 攻撃[Ⅰ] repeated 3+ times" in str(excinfo.value)
