from fuzzconfig import FuzzConfig
import interconnect
import pytrellis
import fuzzloops

jobs = [
    {
        "loc": "DCU0",
        "bel": (71, 42),
        "tiles": [
            "MIB_R71C42:DCU0", "MIB_R71C43:DCU1", "MIB_R71C44:DCU2", "MIB_R71C45:DCU3",
            "MIB_R71C46:DCU4", "MIB_R71C47:DCU5", "MIB_R71C48:DCU6", "MIB_R71C49:DCU7",
            "MIB_R71C50:DCU8"
        ]
    },
     {
        "loc": "DCU1",
        "bel": (71, 69),
        "tiles": [
            "MIB_R71C69:DCU0", "MIB_R71C70:DCU1", "MIB_R71C71:DCU2", "MIB_R71C72:DCU3",
			"MIB_R71C73:DCU4", "MIB_R71C74:DCU5", "MIB_R71C75:DCU6", "MIB_R71C76:DCU7",
			"MIB_R71C77:DCU8"
        ]
    },
]


def main():
    pytrellis.load_database("../../../database")

    def fuzz_job(job: dict[str, str | list[str] | tuple[int, int]]):
        job_name = f"{job['loc']}ROUTE"

        if job.get("bidir", False):
            job_name += "_BIDIR"

        cfg = FuzzConfig(
            job=job_name,
            family="ECP5",
            device="LFE5UM5G-45F",
            ncl="dcuroute0.ncl" if job["loc"] == "DCU0" else "dcuroute1.ncl",
            tiles=job["tiles"]
        )

        cfg.setup()

        def nn_filter(net, netnames):
            return "DCU" in net or "PCS" in net

        interconnect.fuzz_interconnect(
            config=cfg,
            location=job["bel"],
            netname_predicate=nn_filter,
            netname_filter_union=False,
            func_cib=True
        )

    all_jobs = [
        *jobs,
        {
            "loc": jobs[0]["loc"],
            "bel": jobs[0]["bel"],
            "tiles": jobs[0]["tiles"] + jobs[1]["tiles"],
            "bidir": True
        },
        {
            "loc": jobs[1]["loc"],
            "bel": jobs[1]["bel"],
            "tiles": jobs[0]["tiles"] + jobs[1]["tiles"],
            "bidir": True
        }
    ]

    fuzzloops.parallel_foreach(all_jobs, fuzz_job)


if __name__ == "__main__":
    main()
