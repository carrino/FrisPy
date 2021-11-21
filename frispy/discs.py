#  Copyright (c) 2021 John Carrino

from frispy.model import Model

# constants come from wind tunnel testing done by
# check out "DYNAMICS AND PERFORMANCE OF FLYING DISCS" page 111
class Discs:
    @staticmethod
    def from_string(name: str) -> Model:
        if name == "wraith":
            return Discs.wraith
        elif name == "roc":
            return Discs.roc
        elif name == "flick":
            return Discs.flick
        elif name == "stable_wraith":
            return Discs.stable_wraith
        elif name == "destroyer":
            return Discs.destroyer
        else:
            raise ValueError("name not found")

    @staticmethod
    def from_flight_numbers(speed: float, glide: float, turn: float, fade: float) -> Model:
        # TODO: return model based on flight numbers
        return Model()

    # condor I_xx is 4-5% higher than 1/2 I_zz
    # I suspect most discs are somewhere around 3-5% off (maybe less for drivers).
    # However, for a known mold we may be able to assume I_xx/I_zz is constant
    # and can be used for calibration.
    # for condor the rotation frequency is 13/12 times the wobble frequency.
    # While in flight accel.x average is about -2.5 m/s^2
    # This corresponds to the rotational spindown
    # accel.x is a sine wave +/- 5 m/s^2  This is equal to the drag on the disc


    ultrastar: Model = Model()

    wraith: Model = Model(**{
        "PL0": 0.143,  # lift factor at 0 AoA (depends on glide)
        "PLa": 2.29,  # lift factor linear with AoA (0.04 deg -> 2.29 rad) (constant)
        "CD0": 0.055,  # drag at 0 AoA  (based on disc speed)
        # (.055 at speed 11, .061 speed 5, .067 speed 4, .083 speed 2)
        "PDa": 1.67,  # quadratic with AoA from zero lift point (constant)
        "PTxwz": 0,  # rolling moment related to spin precession?
        "PTy0": -0.02,
        # pitching moment from disc stability at 0 AoA (based on turn of disc, also based on cavity of disc)
        # -0.02 turn -1, -0.007 turn 1, -0.033 turn -2, -0.015 turn 0  (per degree not per rad)
        "PTya": 0.343,
        # pitching moment from disc stability linear in AoA (0.006 / deg -> 0.343) (based on fade of disc)
        # fade 0 0.002, fade 1 0.004, fade 3  0.006, fade 5 0.008  (per degree not per rad)
        "PTywy": -1.3e-2,  # dampening factor for pitch (constant)
        "PTxwx": -1.3e-2,  # dampening factor for roll (constant)
        "PTzwz": -3.4e-5,  # spin down (constant)
        "I_xx": 6.183E-04,
        "I_zz": 1.231E-03,
        "mass": 0.175,
        "diameter": 0.211,
        "rim_depth": 0.012,
        "rim_width": 0.021,
        "height": 0.014,
    })

    stable_wraith: Model = Model(**{
        "PL0": 0.143,  # lift factor at 0 AoA (depends on glide)
        "PLa": 2.29,  # lift factor linear with AoA (0.04 deg -> 2.29 rad) (constant)
        "CD0": 0.055,  # drag at 0 AoA  (based on disc speed)
        # (.055 at speed 11, .061 speed 5, .067 speed 4, .083 speed 2)
        "PDa": 1.67,  # quadratic with AoA from zero lift point (constant)
        "PTxwz": 0,  # rolling moment related to spin precession?
        "PTy0": -0.01, # pitching moment from disc stability at 0 AoA (based on turn of disc, also based on cavity of disc)
        # -0.02 turn -1, -0.007 turn 1, -0.033 turn -2, -0.015 turn 0  (per degree not per rad)
        "PTya": 0.2,
        # pitching moment from disc stability linear in AoA (0.006 / deg -> 0.343 / rad) (based on fade of disc)
        # fade 0 0.002, fade 1 0.004, fade 3  0.006, fade 5 0.008  (per degree not per rad)
        "PTxwx": -1.3e-2,  # dampening factor for roll (constant)
        "PTzwz": -3.4e-5,  # spin down (constant)
        "I_xx": 6.183E-04,
        "I_zz": 1.231E-03,
        "mass": 0.175,
        "diameter": 0.211,
        "rim_depth": 0.012,
        "rim_width": 0.021,
        "height": 0.014,
    })

    destroyer: Model = Model(**{
        "PL0": 0.16,  # lift factor at 0 AoA (depends on glide) 2 deg Aoa at 58 mph lift was about 8m/s^2   0.8g
        "PLa": 2.29,  # lift factor linear with AoA (0.04 deg -> 2.29 rad) (constant)
        "PD0": 0.035, # keep dropping drag until destroyer can go 520ft at 70 mph
        #"CD0": 0.042,  # drag at 0 AoA  (based on disc speed)  2 deg AoA at 58mph was about 21m/s^2 with wobble, but only 5 after wobble subsides
        # (.055 at speed 11, .061 speed 5, .067 speed 4, .083 speed 2)
        "PDa": 1.67,  # quadratic with AoA from zero lift point (constant)
        "PTxwz": 0,  # rolling moment related to spin precession?
        "PTy0": -0.01, # pitching moment from disc stability at 0 AoA (based on turn of disc, also based on cavity of disc)
        # -0.02 turn -1, -0.007 turn 1, -0.033 turn -2, -0.015 turn 0  (per degree not per rad)
        "PTya": 0.3, # pitching moment from disc stability linear in AoA (0.006 / deg -> 0.343 / rad) (based on fade of disc)
        # fade 0 0.002, fade 1 0.004, fade 3  0.006, fade 5 0.008  (per degree not per rad)
        "PTxwx": -6.0e-4,  # dampening factor for wobble (constant) 21.5 -> 3.3 over 1s
        "PTzwz": -2.1e-5,  # spin down (constant) at 58mph spindown is about 24m/s^2 (3.5% (118.5 -> 114.5) over .82s)
        "I_xx": 6.263E-04, # I_xx is much closer to 1/2 on the destroyer than the condor, height is 2.2 vs 1.4
        # frequency of wobble for destroyer is .98 the rate of rotation.
        # this means that I_xx is about 1.01 * I_zz / 2
        # this means if we analyze the
        "I_zz": 1.231E-03,
        "mass": 0.175,
        "diameter": 0.211,
        "rim_depth": 0.012,
        "rim_width": 0.0229,
        "height": 0.014,
    })


    roc: Model = Model(**{
        "PL0": 0.053,  # lift factor at 0 AoA (depends on glide)
        # roc 0.053 glide 4, buzzz .1 glide 4, wraith .143 glide 5, aviar .152 glide 3, flick
        "PLa": 2.35,  # lift factor linear with AoA (0.04 deg -> 2.29 rad) (mostly constant, maybe dependent on glide)
        "CD0": 0.067,  # drag at 0 angle of attack  (based on disc speed)
        # (.055 at speed 11, .061 speed 5, .067 speed 4, .083 speed 2)
        "PDa": 1.67,  # quadratic with AoA from zero lift point (constant)
        "PTxwz": 0,  # rolling moment related to spin precession?
        "PTy0": -0.01,  # pitching from disc stability at 0 AoA (based on turn of disc, also based on cavity of disc)
        # -0.02 turn -1, -0.007 turn 1, -0.033 turn -2, -0.015 turn 0  (per degree not per rad)
        "PTya": 0.172,
        # pitching moment from disc stability linear in AoA (0.008 / deg -> 0.172) (based on fade of disc)
        # fade 0 0.002, fade 1 0.004, fade 3  0.006, fade 5 0.008  (per degree not per rad)
        "I_xx": 7.086E-04,
        "I_zz": 1.408E-03,
        "mass": 0.180,
        "diameter": 0.217,
        "rim_depth": 0.013,
        "rim_width": 0.012,
        "height": 0.020,
    })

    flick: Model = Model(**{
        "PL0": 0.1,  # lift factor at 0 AoA (depends on glide)
        # roc 0.053 glide 4, buzzz .1 glide 4, wraith .143 glide 5, aviar .152 glide 3, flick
        "PLa": 2.18,  # lift factor linear with AoA (0.038 deg -> 2.18 rad) (mostly constant, maybe dependent on glide)
        "PD0": 0.06,  # drag at 0 lift
        # (.055 at speed 11, .061 speed 5, .067 speed 4, .083 speed 2)
        "PDa": 1.67,  # quadratic with AoA from zero lift point (constant)
        "PTxwz": 0,  # rolling moment related to spin precession?
        "PTy0": -0.007,  # pitching from disc stability at 0 AoA (based on turn of disc, also based on cavity of disc)
        # -0.02 turn -1, -0.007 turn 1, -0.033 turn -2, -0.015 turn 0  (per degree not per rad)
        "PTya": 0.458,
        # pitching moment from disc stability linear in AoA (0.008 / deg -> 0.172) (based on fade of disc)
        # fade 0 0.002, fade 1 0.004, fade 3  0.006, fade 5 0.008  (per degree not per rad)
        "I_xx": 6.183E-04,
        "I_zz": 1.231E-03,
        "mass": 0.175,
        "diameter": 0.211,
        "rim_depth": 0.012,
        "rim_width": 0.023,
        "height": 0.013,
    })
