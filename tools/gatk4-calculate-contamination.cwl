#!/usr/bin/env cwl-runner

cwlVersion: v1.0

requirements:
  - class: DockerRequirement
    dockerPull: broadinstitute/gatk:latest
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

baseCommand: [/gatk/gatk-launch, --javaOptions, -Xmx4g, CalculateContamination]
