#!/usr/bin/env cwl-runner

cwlVersion: v1.0

requirements:
  - class: DockerRequirement
    dockerPull: quay.io/ncigdc/cocleaning-tool:latest
  - class: InlineJavascriptRequirement
  - class: MultipleInputFeatureRequirement

class: CommandLineTool

inputs:
 
  - id: genotypes
    type: ['null', File]
    format: "edam:format_3016"
    inputBinding:
      prefix: --genotypes

  - id: INPUT
    type: ['null', File]
    format: "edam:format_2572"
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

  - id: outname
    type: string
    inputBinding:
      prefix: --out

  - id: popfile
    type: File
    format: "edam:format_3016"
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
    type: ['null', string]
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
    type: ['null', File]
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
    type: ['null', string]
    inputBinding:
      prefix: --population

  - id: precision
    type: float   
    default: 0.1  
    inputBinding:
      prefix: --precision

  - id: sample_name
    type: string
    default: "null"
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
    type: ['null', string]
    inputBinding:
      prefix: -isr

  - id: interval
    type: ['null', string]
    inputBinding:
      prefix: -L

  - id: min_genotype_depth
    type: ['null', int]
    inputBinding:
      prefix: --min_genotype_depth

  - id: min_site_depth
    type: ['null', int]
    inputBinding:
      prefix: --min_site_depth

outputs:
  - id: output
    type: File
    outputBinding:
      glob: $(inputs.outname)

baseCommand: [java, -XX:ParallelGCThreads=8, -jar, /usr/local/bin/GenomeAnalysisTK.jar, -T, ContEst]

