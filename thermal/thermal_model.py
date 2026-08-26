import numpy as np
import pandas as pd


class TransformerThermalModel:
    """
    IEEE C57.91-based transformer thermal model.

    Calculates:
        - Per-unit loading
        - Ultimate top-oil temperature rise
        - Transient top-oil temperature
        - Transient winding hot-spot rise
        - Hot-spot temperature
        - Aging acceleration factor
        - Equivalent aging hours
        - Average aging acceleration factor
        - Approximate loss-of-life percentage

    Temperatures are in degrees Celsius.
    Time is in hours.
    Load is expressed in per-unit (pu).
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
        normal_insulation_life_hours=180000.0,
    ):
        self.tau_oil = float(tau_oil)
        self.tau_winding = float(tau_winding)

        self.delta_theta_or = float(delta_theta_or)
        self.delta_theta_hr = float(delta_theta_hr)

        self.R = float(R)
        self.n = float(n)
        self.m = float(m)

        self.rated_capacity = float(rated_capacity)
        self.normal_insulation_life_hours = float(
            normal_insulation_life_hours
        )

        self._validate_parameters()

    # ------------------------------------------------------------------
    # Parameter validation
    # ------------------------------------------------------------------

    def _validate_parameters(self):
        if self.tau_oil <= 0:
            raise ValueError("tau_oil must be greater than zero.")

        if self.tau_winding <= 0:
            raise ValueError(
                "tau_winding must be greater than zero."
            )

        if self.delta_theta_or < 0:
            raise ValueError(
                "delta_theta_or cannot be negative."
            )

        if self.delta_theta_hr < 0:
            raise ValueError(
                "delta_theta_hr cannot be negative."
            )

        if self.R < 0:
            raise ValueError("R cannot be negative.")

        if self.n <= 0:
            raise ValueError("n must be greater than zero.")

        if self.m <= 0:
            raise ValueError("m must be greater than zero.")

        if self.rated_capacity <= 0:
            raise ValueError(
                "rated_capacity must be greater than zero."
            )

        if self.normal_insulation_life_hours <= 0:
            raise ValueError(
                "normal_insulation_life_hours must be "
                "greater than zero."
            )

    # ------------------------------------------------------------------
    # Per-unit loading
    # ------------------------------------------------------------------

    def per_unit_load(self, load):
        """
        Return load in per-unit form.

        The public simulation API already expects per-unit loading,
        so this method mainly provides a clear engineering interface.
        """
        load = np.asarray(load, dtype=float)

        if not np.all(np.isfinite(load)):
            raise ValueError("Load contains invalid values.")

        if np.any(load < 0):
            raise ValueError("Load ratio cannot be negative.")

        return load

    # ------------------------------------------------------------------
    # Ultimate top-oil temperature rise
    # ------------------------------------------------------------------

    def ultimate_top_oil_rise(self, K):
        """
        Calculate ultimate top-oil rise above ambient.

        Δθ_TO,U =
            Δθ_TO,R *
            [(K²R + 1) / (R + 1)]^n
        """

        K = np.asarray(K, dtype=float)

        if np.any(~np.isfinite(K)):
            raise ValueError("K contains invalid values.")

        if np.any(K < 0):
            raise ValueError("K cannot be negative.")

        loss_ratio = (
            (K**2 * self.R + 1.0)
            / (self.R + 1.0)
        )

        return (
            self.delta_theta_or
            * loss_ratio**self.n
        )

    # ------------------------------------------------------------------
    # Transient top-oil response
    # ------------------------------------------------------------------

    def top_oil_transient(
        self,
        initial_rise,
        ultimate_rise,
        dt_hours,
    ):
        """
        Calculate the next top-oil temperature rise.

        Δθ_TO(t) =
            Δθ_TO,U
            +
            (Δθ_TO,i - Δθ_TO,U)
            exp(-t / τ_TO)
        """

        if dt_hours <= 0:
            raise ValueError(
                "dt_hours must be greater than zero."
            )

        response = np.exp(
            -dt_hours / self.tau_oil
        )

        return (
            ultimate_rise
            + (
                initial_rise
                - ultimate_rise
            )
            * response
        )

    # ------------------------------------------------------------------
    # Ultimate winding hot-spot rise
    # ------------------------------------------------------------------

    def ultimate_hotspot_rise(self, K):
        """
        Calculate ultimate winding hot-spot rise above top oil.

        Δθ_H,U = Δθ_H,R * K^(2m)
        """

        K = np.asarray(K, dtype=float)

        if np.any(~np.isfinite(K)):
            raise ValueError("K contains invalid values.")

        if np.any(K < 0):
            raise ValueError("K cannot be negative.")

        return (
            self.delta_theta_hr
            * K ** (2.0 * self.m)
        )

    # ------------------------------------------------------------------
    # Transient winding response
    # ------------------------------------------------------------------

    def winding_transient(
        self,
        initial_rise,
        ultimate_rise,
        dt_hours,
    ):
        """
        Calculate the next winding hot-spot rise.

        Δθ_H(t) =
            Δθ_H,U
            +
            (Δθ_H,i - Δθ_H,U)
            exp(-t / τ_W)
        """

        if dt_hours <= 0:
            raise ValueError(
                "dt_hours must be greater than zero."
            )

        response = np.exp(
            -dt_hours / self.tau_winding
        )

        return (
            ultimate_rise
            + (
                initial_rise
                - ultimate_rise
            )
            * response
        )

    # ------------------------------------------------------------------
    # Aging acceleration factor
    # ------------------------------------------------------------------

    @staticmethod
    def aging_acceleration(hotspot_c):
        """
        Calculate Arrhenius aging acceleration factor.

        F_AA =
            exp[
                15000/383
                -
                15000/(θ_H + 273)
            ]
        """

        hotspot_c = np.asarray(
            hotspot_c,
            dtype=float,
        )

        if np.any(~np.isfinite(hotspot_c)):
            raise ValueError(
                "Hotspot temperature contains invalid values."
            )

        kelvin = hotspot_c + 273.0

        if np.any(kelvin <= 0):
            raise ValueError(
                "Hotspot temperature is physically invalid."
            )

        return np.exp(
            (15000.0 / 383.0)
            - (
                15000.0 / kelvin
            )
        )

    # ------------------------------------------------------------------
    # Main simulation
    # ------------------------------------------------------------------

    def simulate(
        self,
        load_profile,
        ambient_profile,
        dt_hours=1.0,
    ):
        """
        Simulate transformer thermal behavior.

        Parameters
        ----------
        load_profile:
            Per-unit transformer load profile.

        ambient_profile:
            Ambient temperature profile in °C.

        dt_hours:
            Simulation timestep in hours.

        Returns
        -------
        pandas.DataFrame
            Thermal response including:
                time_hr
                ambient_C
                load_pu
                top_oil_rise_C
                top_oil_C
                hotspot_rise_C
                hotspot_C
                aging_factor
                equivalent_aging_hours
        """

        load_profile = np.asarray(
            load_profile,
            dtype=float,
        )

        ambient_profile = np.asarray(
            ambient_profile,
            dtype=float,
        )

        # --------------------------------------------------------------
        # Input validation
        # --------------------------------------------------------------

        if load_profile.ndim != 1:
            raise ValueError(
                "load_profile must be one-dimensional."
            )

        if ambient_profile.ndim != 1:
            raise ValueError(
                "ambient_profile must be one-dimensional."
            )

        if len(load_profile) != len(ambient_profile):
            raise ValueError(
                "load_profile and ambient_profile must "
                "have the same length."
            )

        if len(load_profile) == 0:
            raise ValueError(
                "Profiles cannot be empty."
            )

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

        n_points = len(load_profile)

        # --------------------------------------------------------------
        # Allocate arrays
        # --------------------------------------------------------------

        top_oil_rise = np.zeros(n_points)
        top_oil = np.zeros(n_points)

        hotspot_rise = np.zeros(n_points)
        hotspot = np.zeros(n_points)

        aging_factor = np.zeros(n_points)
        equivalent_aging = np.zeros(n_points)

        # --------------------------------------------------------------
        # Initial condition
        # --------------------------------------------------------------

        top_oil[0] = ambient_profile[0]

        hotspot_rise[0] = 0.0

        hotspot[0] = (
            top_oil[0]
            + hotspot_rise[0]
        )

        aging_factor[0] = (
            self.aging_acceleration(
                hotspot[0]
            )
        )

        equivalent_aging[0] = 0.0

        # --------------------------------------------------------------
        # Thermal simulation
        # --------------------------------------------------------------

        for i in range(1, n_points):

            # Previous timestep load drives the thermal response
            K = load_profile[i - 1]

            theta_ambient = ambient_profile[i]

            # ----------------------------------------------------------
            # Top-oil
            # ----------------------------------------------------------

            ultimate_to_rise = (
                self.ultimate_top_oil_rise(K)
            )

            current_to_rise = (
                top_oil[i - 1]
                - ambient_profile[i - 1]
            )

            top_oil_rise[i] = (
                self.top_oil_transient(
                    initial_rise=current_to_rise,
                    ultimate_rise=ultimate_to_rise,
                    dt_hours=dt_hours,
                )
            )

            top_oil[i] = (
                theta_ambient
                + top_oil_rise[i]
            )

            # ----------------------------------------------------------
            # Winding hotspot
            # ----------------------------------------------------------

            ultimate_hs_rise = (
                self.ultimate_hotspot_rise(
                    load_profile[i]
                )
            )

            hotspot_rise[i] = (
                self.winding_transient(
                    initial_rise=hotspot_rise[i - 1],
                    ultimate_rise=ultimate_hs_rise,
                    dt_hours=dt_hours,
                )
            )

            hotspot[i] = (
                top_oil[i]
                + hotspot_rise[i]
            )

            # ----------------------------------------------------------
            # Aging
            # ----------------------------------------------------------

            aging_factor[i] = (
                self.aging_acceleration(
                    hotspot[i]
                )
            )

            equivalent_aging[i] = (
                equivalent_aging[i - 1]
                + aging_factor[i]
                * dt_hours
            )

        # --------------------------------------------------------------
        # Average aging acceleration
        # --------------------------------------------------------------

        total_time = (
            (n_points - 1)
            * dt_hours
        )

        if total_time > 0:
            average_aging = (
                equivalent_aging[-1]
                / total_time
            )
        else:
            average_aging = aging_factor[0]

        # --------------------------------------------------------------
        # Percentage loss of life
        # --------------------------------------------------------------

        loss_of_life_percent = (
            equivalent_aging[-1]
            / self.normal_insulation_life_hours
            * 100.0
        )

        # --------------------------------------------------------------
        # Result
        # --------------------------------------------------------------

        result = pd.DataFrame(
            {
                "time_hr":
                    np.arange(n_points)
                    * dt_hours,

                "ambient_C":
                    ambient_profile,

                "load_pu":
                    load_profile,

                "top_oil_rise_C":
                    top_oil_rise,

                "top_oil_C":
                    top_oil,

                "hotspot_rise_C":
                    hotspot_rise,

                "hotspot_C":
                    hotspot,

                "aging_factor":
                    aging_factor,

                "equivalent_aging_hours":
                    equivalent_aging,
            }
        )

        # Useful metadata for API/dashboard layer
        result.attrs["average_aging_factor"] = (
            float(average_aging)
        )

        result.attrs["loss_of_life_percent"] = (
            float(loss_of_life_percent)
        )

        result.attrs["peak_top_oil_C"] = (
            float(top_oil.max())
        )

        result.attrs["peak_hotspot_C"] = (
            float(hotspot.max())
        )

        return result


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
    print("-" * 45)

    print(
        f"Peak top-oil       : "
        f"{result['top_oil_C'].max():.2f} °C"
    )

    print(
        f"Peak hotspot       : "
        f"{result['hotspot_C'].max():.2f} °C"
    )

    print(
        f"Peak aging factor  : "
        f"{result['aging_factor'].max():.3f}×"
    )

    print(
        f"Equivalent aging   : "
        f"{result.attrs['loss_of_life_percent']:.6f}% "
        f"of reference life"
    )

    print("\nThermal response:")
    print(result.to_string(index=False))