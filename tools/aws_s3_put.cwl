#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool
requirements:
  - class: DockerRequirement
    dockerPull: quay.io/ncigdc/awscli:1
  - class: EnvVarRequirement
    envDef:
      - envName: "AWS_CONFIG_FILE"
        envValue: $(inputs.aws_config.path)
      - envName: "AWS_SHARED_CREDENTIALS_FILE"
        envValue: $(inputs.aws_shared_credentials.path)
  - class: InlineJavascriptRequirement
  - class: ShellCommandRequirement

inputs:
  - id: aws_config
    type: File

  - id: aws_shared_credentials
    type: File

  - id: s3cfg_section
    type: string
    inputBinding:
      position: 1
      prefix: --profile

  - id: input
    type: File
    inputBinding:
      position: 98

  - id: s3uri
    type: string
    inputBinding:
      position: 99

outputs:
  - id: output
    type: File
    outputBinding:
      glob: "output"

arguments:
  - valueFrom: |
      ${
      function include(arr,obj) {
        return (arr.indexOf(obj) != -1)
      }

      if (include(inputs.s3cfg_section,"ceph")) {
        var endpoint_url = "http://gdc-cephb-objstore.osdc.io/";
      } else {
        var endpoint_url = "http://gdc-accessors.osdc.io/";
      } 
      
      return endpoint_url
      }
    prefix: --endpoint-url
    position: 0

stdout: "output"
    
baseCommand: [aws, s3, cp]