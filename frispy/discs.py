from frispy.model import Model

class Discs:
    @staticmethod
    def from_flight_numbers():
        return Model()

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
        "I_xx": 7.086E-04,
        "I_zz": 1.408E-03,
        "mass": 0.175,
        "diameter": 0.211,
        "rim_depth": 0.012,
        "rim_width": 0.023,
        "height": 0.013,
    })
