#!/usr/bin/env cwl-runner

cwlVersion: v1.0

requirements:
  - class: DockerRequirement
    dockerPull: quay.io/ncigdc/cocleaning-tool
  - class: InlineJavascriptRequirement
  - class: MultipleInputFeatureRequirement

class: CommandLineTool

inputs:
 
  - id: genotypes
    type: File
    format: "edam:format_3016"
    default: null
    inputBinding:
      prefix: --genotypes

  - id: INPUT
    type: File
    format: "edam:format_2572"
    default: NULL
    inputBinding:
      prefix: -I
    secondaryFiles:
      - ^.bai

  - id: INPUT_TUMOR
    type: File
    format: "edam:format_2572"
    inputBinding:
      prefix: -I:eval
    secondaryFiles:
      - ^.bai

  - id: INPUT_NORMAL
    type: File
    format: "edam:format_2572"
    inputBinding:
      prefix: -I:genotype
    secondaryFiles:
      - ^.bai

  - id: output
    type: string
    inputBinding:
      prefix: --out

  - id: popfile
    type: File
    format: "edam:format_3016"
    default: null
    inputBinding:
      prefix: --popfile
    secondaryFiles:
      - .tbi
     
  - id: REFERENCE_SEQUENCE
    type: File
    format: "edam:format_1929"
    inputBinding:
      prefix: -R
    secondaryFiles:
      - .fai
      - ^.dict

  - id: base_report
    type: string
    default: null
    inputBinding:
      prefix: --base_report

  - id: beta_threshold
    type: double
    default: 0.95
    inputBinding:
      prefix: --beta_threshold

  - id: genotype_mode
    type: string
    default: HARD_THRESHOLD
    inputBinding:
      prefix: --genotype_mode

  - id: lane_level_contamination
    type:
      type: array
      items: string
      inputBinding:
        prefix: --lane_level_contamination

  - id: likelihood_file
    type: string
    default: null
    inputBinding:
      prefix: --likelihood_file

  - id: min_mapq
    type: int
    default: 20
    inputBinding:
      prefix: --min_mapq

  - id: min_qscoe
    type: int   
    default: 20  
    inputBinding:
      prefix: --min_qscore

  - id: minimum_base_count
    type: int   
    default: 500  
    inputBinding:
      prefix: --minimum_base_count

  - id: population
    type: string   
    default: null  
    inputBinding:
      prefix: --population

  - id: precision
    type: float   
    default: 0.1  
    inputBinding:
      prefix: --precision

  - id: sample_name
    type: string
    default: null
    inputBinding:
      prefix: --sample_name

  - id: trim_fraction
    type: float
    default: 0.01  
    inputBinding:
      prefix: --trim_fraction

  - id: verify_sample
    type: boolean
    default: false  
    inputBinding:
      prefix: --verify_sample

  - id: isr
    type: string
    default: null
    inputBinding:
      prefix: -isr

  - id: interval
    type: string
    default: null
    inputBinding:
      prefix: -L

outputs:
  - id: output
    type: File
    outputBinding:
      glob: $(inputs.output)

baseCommand: [java, -jar, /usr/local/bin/GenomeAnalysisTK.jar, -T, ContEst]

