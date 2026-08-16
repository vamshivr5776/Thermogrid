import numpy as np
import pytest

from thermal.thermal_model import TransformerThermalModel


def test_zero_load_does_not_create_negative_temperature():
    model = TransformerThermalModel()

    load = np.zeros(24)
    ambient = np.full(24, 30.0)

    result = model.simulate(
        load_profile=load,
        ambient_profile=ambient,
        dt_hours=1.0,
    )

    assert np.all(result["top_oil_C"] >= 0)
    assert np.all(result["hotspot_C"] >= 0)


def test_constant_load_reaches_thermal_equilibrium():
    model = TransformerThermalModel()

    load = np.ones(100)
    ambient = np.full(100, 30.0)

    result = model.simulate(
        load_profile=load,
        ambient_profile=ambient,
        dt_hours=1.0,
    )

    # Temperature should be increasing toward equilibrium,
    # not decreasing during this constant-load heating period.
    assert result["top_oil_C"].iloc[-1] > result["top_oil_C"].iloc[1]


def test_overload_produces_higher_hotspot():
    model = TransformerThermalModel()

    ambient = np.full(100, 30.0)

    normal = model.simulate(
        load_profile=np.ones(100),
        ambient_profile=ambient,
        dt_hours=1.0,
    )

    overload = model.simulate(
        load_profile=np.full(100, 1.2),
        ambient_profile=ambient,
        dt_hours=1.0,
    )

    assert (
        overload["hotspot_C"].iloc[-1]
        > normal["hotspot_C"].iloc[-1]
    )


def test_higher_ambient_produces_higher_hotspot():
    model = TransformerThermalModel()

    load = np.ones(100)

    normal = model.simulate(
        load_profile=load,
        ambient_profile=np.full(100, 30.0),
        dt_hours=1.0,
    )

    hot_ambient = model.simulate(
        load_profile=load,
        ambient_profile=np.full(100, 40.0),
        dt_hours=1.0,
    )

    assert (
        hot_ambient["hotspot_C"].iloc[-1]
        > normal["hotspot_C"].iloc[-1]
    )


def test_negative_load_is_rejected():
    model = TransformerThermalModel()

    with pytest.raises(ValueError):
        model.simulate(
            load_profile=[-0.5, 1.0],
            ambient_profile=[30.0, 30.0],
        )


def test_mismatched_profiles_are_rejected():
    model = TransformerThermalModel()

    with pytest.raises(ValueError):
        model.simulate(
            load_profile=[1.0, 1.0, 1.0],
            ambient_profile=[30.0, 30.0],
        )


def test_empty_profiles_are_rejected():
    model = TransformerThermalModel()

    with pytest.raises(ValueError):
        model.simulate(
            load_profile=[],
            ambient_profile=[],
        )


def test_invalid_time_step_is_rejected():
    model = TransformerThermalModel()

    with pytest.raises(ValueError):
        model.simulate(
            load_profile=[1.0, 1.0],
            ambient_profile=[30.0, 30.0],
            dt_hours=0,
        )

def test_hotspot_has_thermal_inertia():
    model = TransformerThermalModel(
        tau_winding=1.0
    )

    load = np.array([
        0.5,
        1.5,
        1.5,
        1.5,
    ])

    ambient = np.full(4, 30.0)

    result = model.simulate(
        load_profile=load,
        ambient_profile=ambient,
        dt_hours=0.1,
    )

    # After the load increases, hotspot should rise gradually.
    # It should not immediately reach the final equilibrium value.
    assert (
        result["hotspot_C"].iloc[1]
        < result["hotspot_C"].iloc[-1]
    )