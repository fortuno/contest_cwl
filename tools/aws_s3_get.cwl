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

inputs:
  - id: aws_config
    type: File

  - id: aws_shared_credentials
    type: File

  - id: endpoint_json
    type: File
    inputBinding:
      loadContents: true
      valueFrom: null

  - id: s3url
    type: string

  - id: s3cfg_section
    type: string
    inputBinding:
      prefix: --profile
      position: 1  

outputs:
  - id: output
    type: File
    outputBinding:
      glob: $(inputs.s3url.split('/').slice(-1)[0])

arguments:
  - valueFrom: $(inputs.s3url)
    position: 98

  - valueFrom: .
    position: 99

  - valueFrom: |
      ${
      var endpoint_json = JSON.parse(inputs.endpoint_json.contents);
      var endpoint_url = String(endpoint_json[inputs.s3cfg_section]);
      return endpoint_url
      }
    prefix: --endpoint-url
    position: 0    

baseCommand: [aws, s3, cp]
