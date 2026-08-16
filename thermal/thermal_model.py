import numpy as np
import pandas as pd


class TransformerThermalModel:
    """
    Simplified IEEE C57.91-based thermal model
    for an oil-immersed distribution transformer.
    """

    def __init__(
        self,
        tau_oil=3.0,
        delta_theta_or=55.0,
        y=0.8,
        H=1.3,
        g=23.0,
        rated_capacity=500.0,
    ):
        self.tau_oil = tau_oil
        self.delta_theta_or = delta_theta_or
        self.y = y
        self.H = H
        self.g = g
        self.rated_capacity = rated_capacity

    def simulate(self, load_profile, ambient_profile, dt_hours=1.0):
        """
        Simulate transformer thermal behavior.

        Parameters
        ----------
        load_profile : array-like
            Load ratio K = actual load / rated load.
        ambient_profile : array-like
            Ambient temperature in °C.
        dt_hours : float
            Simulation time step in hours.

        Returns
        -------
        pandas.DataFrame
            Ambient, load, top-oil, hotspot and aging factor.
        """

        load_profile = np.asarray(load_profile, dtype=float)
        ambient_profile = np.asarray(ambient_profile, dtype=float)

        if len(load_profile) != len(ambient_profile):
            raise ValueError(
                "load_profile and ambient_profile must have the same length."
            )

        if len(load_profile) == 0:
            raise ValueError("Profiles cannot be empty.")

        if np.any(load_profile < 0):
            raise ValueError("Load ratio cannot be negative.")

        n = len(load_profile)

        # Top-oil temperature
        theta_to = np.zeros(n)

        # Initial top-oil temperature
        theta_to[0] = (
            ambient_profile[0])

        # Time-domain thermal response
        for i in range(1, n):
            K = load_profile[i - 1]
            theta_a = ambient_profile[i - 1]

            dtheta_dt = (
                self.delta_theta_or * K**self.y
                - (theta_to[i - 1] - theta_a)
            ) / self.tau_oil

            theta_to[i] = theta_to[i - 1] + dtheta_dt * dt_hours

        # Hotspot temperature
        theta_hs = (
            theta_to
            + self.H * self.g * load_profile**self.y
        )

        # Arrhenius aging acceleration factor
        aging_factor = np.exp(
            (15000 / 383)
            - (15000 / (theta_hs + 273))
        )

        return pd.DataFrame(
            {
                "time_hr": np.arange(n) * dt_hours,
                "ambient_C": ambient_profile,
                "load_pu": load_profile,
                "top_oil_C": theta_to,
                "hotspot_C": theta_hs,
                "aging_factor": aging_factor,
            }
        )


if __name__ == "__main__":

    # First validation case from the project plan:
    # 30°C ambient, 1.0 pu load, 24 hours.

    model = TransformerThermalModel()

    load = np.ones(25)
    ambient = np.full(25, 30.0)

    result = model.simulate(
        load_profile=load,
        ambient_profile=ambient,
        dt_hours=1.0,
    )

    print("\nTHERMOGRID THERMAL ENGINE")
    print("-" * 35)

    print(f"Ambient temperature : {ambient[0]:.1f} °C")
    print(f"Load                : {load[0]:.2f} pu")
    print(f"Final top-oil       : {result['top_oil_C'].iloc[-1]:.2f} °C")
    print(f"Peak top-oil        : {result['top_oil_C'].max():.2f} °C")
    print(f"Peak hotspot        : {result['hotspot_C'].max():.2f} °C")
    print(f"Peak aging factor   : {result['aging_factor'].max():.2f}×")
    print("\nThermal response:")
for hour in [0, 1, 3, 6, 12, 24]:
    row = result.iloc[hour]
    print(
        f"Hour {hour:2d}: "
        f"Top-oil = {row['top_oil_C']:.2f} °C, "
        f"Hotspot = {row['hotspot_C']:.2f} °C"
    )