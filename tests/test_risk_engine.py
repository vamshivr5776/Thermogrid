from thermal.risk_engine import ThermalRiskEngine


def test_safe_temperature():

    engine = ThermalRiskEngine()

    result = engine.evaluate(
        hotspot_temperature=80,
        aging_factor=0.5,
    )

    assert result.level == "SAFE"


def test_warning_temperature():

    engine = ThermalRiskEngine()

    result = engine.evaluate(
        hotspot_temperature=110,
        aging_factor=1.0,
    )

    assert result.level == "WARNING"


def test_critical_temperature():

    engine = ThermalRiskEngine()

    result = engine.evaluate(
        hotspot_temperature=120,
        aging_factor=2.0,
    )

    assert result.level == "CRITICAL"


def test_emergency_temperature():

    engine = ThermalRiskEngine()

    result = engine.evaluate(
        hotspot_temperature=130,
        aging_factor=5.0,
    )

    assert result.level == "EMERGENCY"