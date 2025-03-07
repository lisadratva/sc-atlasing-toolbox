rule save_config:
    output:
        json='{images}_{target}/config.json'
    localrule: True
    run:
        # import json

        # with open(output.json,'w') as f:
        #     json.dump(config,f)

        import json
        from pathlib import Path

        # Convert all PosixPath objects in the config dictionary to strings
        # This is assuming that `config` is a dictionary that might contain `PosixPath` objects.
        # Adjust the dictionary comprehension below if the structure of `config` is more complex.
        config_converted = {k: str(v) if isinstance(v, Path) else v for k, v in config.items()}

        with open(output.json,'w') as f:
            json.dump(config_converted, f)


rule rulegraph:
    input: rules.save_config.output.json
    output: '{images}/rule_graphs/{target}.png'
    localrule: True
    shell:
        """
        snakemake {wildcards.target} --configfile {input} --rulegraph | \
            sed -ne '/digraph snakemake_dag/,/}}/p' | \
            dot -Tpng -Grankdir=TB > {output}
        """


rule dag:
    input: rules.save_config.output.json
    output: '{images}/job_graphs/{target}.png'
    localrule: True
    shell:
        """
        snakemake {wildcards.target} --configfile {input} --dag | \
            sed -ne '/digraph snakemake_dag/,/}}/p' | \
            dot -Tpng -Grankdir=LR > {output}
        """


rule dependency_graph:
    input:
        rules.rulegraph.output,
        rules.dag.output,
    localrule: True
