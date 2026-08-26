from thermal.thermal_model import TransformerThermalModel


def test_higher_load_produces_higher_hotspot():
    model = TransformerThermalModel()

    ambient = [30.0] * 8

    low_load = [0.5] * 8
    high_load = [1.0] * 8

    low_result = model.simulate(
        low_load,
        ambient,
        dt_hours=1.0,
    )

    high_result = model.simulate(
        high_load,
        ambient,
        dt_hours=1.0,
    )

    assert (
        high_result["hotspot_C"].iloc[-1]
        > low_result["hotspot_C"].iloc[-1]
    )


def test_overload_produces_higher_hotspot():
    model = TransformerThermalModel()

    ambient = [30.0] * 8

    rated_load = [1.0] * 8
    overload = [1.2] * 8

    rated_result = model.simulate(
        rated_load,
        ambient,
        dt_hours=1.0,
    )

    overload_result = model.simulate(
        overload,
        ambient,
        dt_hours=1.0,
    )

    assert (
        overload_result["hotspot_C"].iloc[-1]
        > rated_result["hotspot_C"].iloc[-1]
    )


def test_higher_ambient_produces_higher_hotspot():
    model = TransformerThermalModel()

    load = [1.0] * 8

    normal_ambient = [30.0] * 8
    hot_ambient = [40.0] * 8

    normal_result = model.simulate(
        load,
        normal_ambient,
        dt_hours=1.0,
    )

    hot_result = model.simulate(
        load,
        hot_ambient,
        dt_hours=1.0,
    )

    assert (
        hot_result["hotspot_C"].iloc[-1]
        > normal_result["hotspot_C"].iloc[-1]
    )


def test_aging_increases_with_hotspot():
    model = TransformerThermalModel()

    cool = model.aging_acceleration(80.0)
    hot = model.aging_acceleration(120.0)

    assert hot > cool


def test_thermal_response_has_inertia():
    model = TransformerThermalModel()

    result = model.simulate(
        load_profile=[0.5, 1.0, 1.0, 1.0],
        ambient_profile=[30.0, 30.0, 30.0, 30.0],
        dt_hours=1.0,
    )

    # Hotspot should evolve rather than instantly
    # jumping directly to the final equilibrium.
    assert result["hotspot_C"].iloc[1] < result["hotspot_C"].iloc[-1]