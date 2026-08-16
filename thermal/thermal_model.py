import numpy as np
import pandas as pd


class TransformerThermalModel:
    """
    Simplified IEEE C57.91-based thermal model
    for an oil-immersed distribution transformer.

    Calculates:
    - Top-oil temperature
    - Winding hot-spot temperature
    - Aging acceleration factor

    Temperatures: °C
    Load: per-unit (pu)
    """

    def __init__(
        self,
        tau_oil=3.0,
        tau_winding=0.25,
        delta_theta_or=55.0,
        delta_theta_hr=30.0,
        R=5.0,
        n=0.8,
        m=0.8,
        rated_capacity=500.0,
    ):
        self.tau_oil = tau_oil
        self.tau_winding = tau_winding
        self.delta_theta_or = delta_theta_or
        self.delta_theta_hr = delta_theta_hr
        self.R = R
        self.n = n
        self.m = m
        self.rated_capacity = rated_capacity

    def simulate(
        self,
        load_profile,
        ambient_profile,
        dt_hours=1.0,
    ):

        load_profile = np.asarray(load_profile, dtype=float)
        ambient_profile = np.asarray(ambient_profile, dtype=float)

        # -----------------------------
        # Input validation
        # -----------------------------

        if load_profile.ndim != 1:
            raise ValueError("load_profile must be one-dimensional.")

        if ambient_profile.ndim != 1:
            raise ValueError("ambient_profile must be one-dimensional.")

        if len(load_profile) != len(ambient_profile):
            raise ValueError(
                "load_profile and ambient_profile must have "
                "the same length."
            )

        if len(load_profile) == 0:
            raise ValueError("Profiles cannot be empty.")

        if not np.all(np.isfinite(load_profile)):
            raise ValueError(
                "load_profile contains invalid values."
            )

        if not np.all(np.isfinite(ambient_profile)):
            raise ValueError(
                "ambient_profile contains invalid values."
            )

        if np.any(load_profile < 0):
            raise ValueError(
                "Load ratio cannot be negative."
            )

        if dt_hours <= 0:
            raise ValueError(
                "dt_hours must be greater than zero."
            )

        if self.tau_oil <= 0:
            raise ValueError(
                "tau_oil must be greater than zero."
            )

        if self.tau_winding <= 0:
            raise ValueError(
                "tau_winding must be greater than zero."
            )

        n_points = len(load_profile)

        # -----------------------------
        # Top-oil temperature
        # -----------------------------

        top_oil = np.zeros(n_points)

        top_oil[0] = ambient_profile[0]

        oil_response = np.exp(
            -dt_hours / self.tau_oil
        )

        for i in range(1, n_points):

            K = load_profile[i - 1]
            theta_ambient = ambient_profile[i - 1]

            loss_ratio = (
                (K**2 * self.R + 1.0)
                / (self.R + 1.0)
            )

            delta_theta_to_u = (
                self.delta_theta_or
                * loss_ratio**self.n
            )

            delta_theta_to_i = (
                top_oil[i - 1]
                - theta_ambient
            )

            delta_theta_to = (
                delta_theta_to_u
                + (
                    delta_theta_to_i
                    - delta_theta_to_u
                )
                * oil_response
            )

            top_oil[i] = (
                theta_ambient
                + delta_theta_to
            )

        # -----------------------------
        # Winding hot-spot rise
        # -----------------------------

        hotspot_rise = np.zeros(n_points)

        winding_response = np.exp(
            -dt_hours / self.tau_winding
        )

        for i in range(1, n_points):

            K = load_profile[i]

            target_hotspot_rise = (
                self.delta_theta_hr
                * K ** (2 * self.m)
            )

            hotspot_rise[i] = (
                target_hotspot_rise
                + (
                    hotspot_rise[i - 1]
                    - target_hotspot_rise
                )
                * winding_response
            )

        # -----------------------------
        # Hotspot temperature
        # -----------------------------

        hotspot = top_oil + hotspot_rise

        # -----------------------------
        # Aging acceleration factor
        # -----------------------------

        aging_factor = np.exp(
            (15000.0 / 383.0)
            - (
                15000.0
                / (hotspot + 273.0)
            )
        )

        # -----------------------------
        # Result
        # -----------------------------

        return pd.DataFrame(
            {
                "time_hr": (
                    np.arange(n_points)
                    * dt_hours
                ),
                "ambient_C": ambient_profile,
                "load_pu": load_profile,
                "top_oil_C": top_oil,
                "hotspot_C": hotspot,
                "aging_factor": aging_factor,
            }
        )


if __name__ == "__main__":

    model = TransformerThermalModel()

    load = np.array(
        [
            0.4,
            0.6,
            0.8,
            1.0,
            1.2,
            1.0,
            0.7,
        ]
    )

    ambient = np.array(
        [
            30,
            30,
            31,
            31,
            32,
            32,
            31,
        ]
    )

    result = model.simulate(
        load_profile=load,
        ambient_profile=ambient,
        dt_hours=1.0,
    )

    print("\nTHERMOGRID THERMAL ENGINE")
    print("-" * 40)

    print(
        f"Peak top-oil     : "
        f"{result['top_oil_C'].max():.2f} °C"
    )

    print(
        f"Peak hotspot     : "
        f"{result['hotspot_C'].max():.2f} °C"
    )

    print(
        f"Peak aging factor: "
        f"{result['aging_factor'].max():.3f}×"
    )

    print("\nThermal response:")
    print(result.to_string(index=False))