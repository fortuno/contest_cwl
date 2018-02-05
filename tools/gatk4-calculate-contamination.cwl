#!/usr/bin/env cwl-runner

cwlVersion: v1.0

requirements:
  - class: DockerRequirement
    dockerPull: broadinstitute/gatk:4.0.0.0
  - class: InlineJavascriptRequirement
  - class: MultipleInputFeatureRequirement

class: CommandLineTool

inputs:
 
  - id: pileup_summary
    type: File
    format: "edam:format_2572"
    inputBinding:
      prefix: -I

  - id: outname
    type: string
    inputBinding:
      prefix: -O

outputs:
  - id: output
    type: File
    outputBinding:
      glob: $(inputs.outname)

baseCommand: [/gatk/gatk, --java-options, "-Xmx4g -XX:ParallelGCThreads=8", CalculateContamination]
