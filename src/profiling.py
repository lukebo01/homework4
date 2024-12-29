import json
import os

def profiling(input_dir:str):
    table_claims = os.listdir(input_dir)

    name_specification = []
    value_specification = []
    metrics = []

    for table_claim in table_claims:
        json_claim:dict = json.load(open(f"{input_dir}/{table_claim}"))
        for claim_id in json_claim.keys():
            claim:dict = json_claim[claim_id]
            
            specifications:dict = claim["specifications"]
            measure:str = claim["Measure"]
            outcome:str = claim["Outcome"]

            for specification_id in specifications.keys():
                specification = specifications[specification_id]

                name_specification.append(specification["name"])
                value_specification.append(specification["value"])

            metrics.append(measure)


    print(name_specification)
    print(value_specification)
    print(metrics)
                