#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool
requirements:
  - class: DockerRequirement
    dockerPull: quay.io/ncigdc/awscli:1
  - class: EnvVarRequirement
    envDef:
      - envName: "AWS_CONFIG_FILE"
        envValue: $(inputs.aws_config_file.path)
      - envName: "AWS_SHARED_CREDENTIALS_FILE"
        envValue: $(inputs.aws_shared_credentials_file.path)
  - class: InlineJavascriptRequirement
  - class: ShellCommandRequirement

inputs:
  - id: aws_config_file
    type: File

  - id: aws_shared_credentials_file
    type: File
      
  - id: s3uri
    type: string
    inputBinding:
      position: 98

outputs:
  - id: output
    type: File
    outputBinding:
      glob: $(inputs.s3uri.split('/').slice(-1)[0])

arguments:
  - valueFrom: |
      ${
      function include(arr,obj) {
        return (arr.indexOf(obj) != -1)
      }

      var s3_url = String(inputs.s3uri.slice(0));
      var s3_path = s3_url.slice(5);
      var s3_array = s3_path.split('/');
      var s3_root = s3_array[0];

      if (include(s3_root,"ceph")) {
        var endpoint_url = "http://gdc-cephb-objstore.osdc.io/";
      } else {
        var endpoint_url = "http://gdc-accessors.osdc.io/";
      } 
      return endpoint_url
      }
    prefix: --endpoint-url
    position: 0

  - valueFrom: |
      ${
      function include(arr,obj) {
        return (arr.indexOf(obj) != -1)
      }

      var s3_url = String(inputs.s3uri.slice(0));
      var s3_path = s3_url.slice(5);
      var s3_array = s3_path.split('/');
      var s3_root = s3_array[0];

      if (include(s3_root,"ceph")) {
        var profile = "ceph";
      } else {
        var profile = "cleversafe";
      } 
      return profile
      }
    prefix: --profile
    position: 1

  - valueFrom: .
    position: 99

baseCommand: [aws, s3, cp]