from fuzzconfig import FuzzConfig
import nonrouting
import pytrellis
import fuzzloops
import interconnect

jobs = [
    {
        "loc": "EXTREF0",
        "bel": (71, 42),
        "tiles": [
            "MIB_R71C42:DCU0", "MIB_R71C43:DCU1", "MIB_R71C44:DCU2", "MIB_R71C45:DCU3",
			"MIB_R71C46:DCU4", "MIB_R71C47:DCU5", "MIB_R71C48:DCU6", "MIB_R71C49:DCU7",
			"MIB_R71C50:DCU8"
        ],
        "nets": [
			"R71C42_REFCLKP_EXTREF",
			"R71C42_INPUT_REFP_APIO",
			"R71C42_OUTPUT_REFP_APIO",
			"R71C42_CLK_REFP_APIO",
			"R71C42_REFCLKN_EXTREF",
			"R71C42_INPUT_REFN_APIO",
			"R71C42_OUTPUT_REFN_APIO",
			"R71C42_CLK_REFN_APIO",
			"R71C42_JREFCLKO_EXTREF",
			"R71C42_EXTREFCLK",
			"R71C42_JTXREFCLKCIB",
			"R71C42_JCH1RXREFCLKCIB",
			"R71C42_JCH0RXREFCLKCIB",
			"R71C42_CH0_RX_REFCLK",
			"R71C42_CH1_RX_REFCLK",
			"R71C42_D_REFCLKI",
			"R71C42_RXREFCLK0",
			"R71C42_RXREFCLK1",
			"R71C42_JTXREFCLK",
        ]
    },
    {
        "loc": "EXTREF1",
        "bel": (71, 69),
        "tiles": [
            "MIB_R71C69:DCU0", "MIB_R71C70:DCU1", "MIB_R71C71:DCU2", "MIB_R71C72:DCU3",
			"MIB_R71C73:DCU4", "MIB_R71C74:DCU5", "MIB_R71C75:DCU6", "MIB_R71C76:DCU7",
			"MIB_R71C77:DCU8"
        ],
        "nets": [
			"R71C69_REFCLKP_EXTREF",
			"R71C69_INPUT_REFP_APIO",
			"R71C69_OUTPUT_REFP_APIO",
			"R71C69_CLK_REFP_APIO",
			"R71C69_REFCLKN_EXTREF",
			"R71C69_INPUT_REFN_APIO",
			"R71C69_OUTPUT_REFN_APIO",
			"R71C69_CLK_REFN_APIO",
			"R71C69_JREFCLKO_EXTREF",
			"R71C69_EXTREFCLK",
			"R71C69_JTXREFCLKCIB",
			"R71C69_JCH1RXREFCLKCIB",
			"R71C69_JCH0RXREFCLKCIB",
			"R71C69_CH0_RX_REFCLK",
			"R71C69_CH1_RX_REFCLK",
			"R71C69_D_REFCLKI",
			"R71C69_RXREFCLK0",
			"R71C69_RXREFCLK1",
			"R71C69_JTXREFCLK",
        ]
    }
]

def get_substs(mode="EXTREFB", loc=None, program=None):
    if mode == "NONE":
        comment = "//"
    else:
        comment = ""
    if program is not None:
        program = ":::" + ",".join(["{}={}".format(k, v) for k, v in program.items()])
    else:
        program = ":#ON"

    return dict(comment=comment, program=program, loc=loc)


def tobinstr(x, size):
    return "0b" + "".join(reversed(["1" if x else "0" for x in x]))


def main():
    pytrellis.load_database("../../../database")

    def nn_filter(net, netnames):
         return "DCU" in net or "PCS" in net or "EXTREF" in net or "REFCLK" in net

    def fuzz_job(job: dict[str, str | list[str]]):
        job_name = f"{job['loc']}ROUTING"

        if job.get("bidir", False):
            job_name += "_BIDIR"

        cfg = FuzzConfig(
            job=job_name,
            family="ECP5",
            device="LFE5UM5G-45F",
            ncl="empty.ncl",
            tiles=job["tiles"]
        )

        cfg.setup()
        empty_bitfile = cfg.build_design(cfg.ncl, {})
        cfg.ncl = "extref.ncl"

        # We Don't want to fuzz the attributes in bi-dir mode
        if job.get("bidir", False):
            nonrouting.fuzz_enum_setting(
                cfg,
                "EXTREF.MODE", ["NONE", "EXTREFB"],
                lambda x: get_substs(
                    mode=x,
                    loc = job["loc"],
                    program={"REFCK_PWDNB": "0b0", "REFCK_RTERM": "0b0", "REFCK_DCBIAS_EN": "0b0"}
                ),
                empty_bitfile,
                False
            )

            # XXX(aki):
            # Commented out because uh, well:
            #
            #   bit EXTREF.REFCK_PWDNB[0] already in DB, but config bits
            #   F3B1 F4B1 F5B1 F6B1 don't match existing DB bits F4B1
            #
            # nonrouting.fuzz_word_setting(
            #     cfg,
            #     "EXTREF.REFCK_PWDNB", 1,
            #     lambda x: get_substs(
            #         loc = job["loc"],
            #         program={"REFCK_PWDNB": tobinstr(x, 1)}
            #     ),
            #     empty_bitfile
            # )

            nonrouting.fuzz_word_setting(
                cfg,
                "EXTREF.REFCK_RTERM", 1,
                lambda x: get_substs(
                    loc = job["loc"],
                    program={"REFCK_RTERM": tobinstr(x, 1)}
                ),
                empty_bitfile
            )

            nonrouting.fuzz_word_setting(
                cfg, "EXTREF.REFCK_DCBIAS_EN", 1,
                lambda x: get_substs(
                    loc = job["loc"],
                    program={"REFCK_DCBIAS_EN": tobinstr(x, 1)}
                ),
                empty_bitfile
            )

        if job.get("bidir", False):
            cfg.ncl = "extref0.ncl" if job["loc"] == "EXTREF0" else "extref1.ncl"

            interconnect.fuzz_interconnect(
                config=cfg,
                location=job["bel"],
                netname_predicate=nn_filter,
                netname_filter_union=False,
                func_cib=True
            )
        else:
            cfg.ncl = "extref_routing.ncl"
            interconnect.fuzz_interconnect_with_netnames(
                cfg, job["nets"], bidir=True
            )

    # XXX(aki):
    # The two other jobs here are for finding the TO/FROM connections between the EXTREFs
    # as seen in section 9 of FPGA-TN-02206
    all_jobs = [
        *jobs,
        {
            "loc": jobs[0]["loc"],
            "bel": jobs[0]["bel"],
            "tiles": jobs[0]["tiles"] + jobs[1]["tiles"],
            "nets": jobs[0]["nets"] + jobs[1]["nets"],
            "bidir": True
        },
        {
            "loc": jobs[1]["loc"],
            "bel": jobs[1]["bel"],
            "tiles": jobs[0]["tiles"] + jobs[1]["tiles"],
            "nets": jobs[0]["nets"] + jobs[1]["nets"],
            "bidir": True
        }
    ]

    fuzzloops.parallel_foreach(all_jobs, fuzz_job)

if __name__ == "__main__":
    main()
