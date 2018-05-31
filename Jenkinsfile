#!/usr/bin/env groovy

pipeline {

 agent {
    kubernetes {
      label 'pypi'
      defaultContainer 'jnlp'
      yaml """
apiVersion: v1
kind: Pod
metadata:
  labels:
    jenkins-job: pypi
spec:
  containers:
  - name: pypi
    image: docker.jamf.build/python:2
    tty: true
    command:
    - cat
    volumeMounts:
      - mountPath: /root/.pypirc
        name: config-pypi
        subPath: .pypirc
  volumes:
    - name: config-pypi
      configMap:
        name: pypi-config
        items:
          - key: .pypirc
            path: .pypirc
"""
    }
  }

   stages {
    stage('Build python package') {
      steps {
        container('pypi') {
          checkout scm
          sh 'python setup.py sdist upload -r local'
          stash(name: "build")
        }
      }
    }

    stage('Build Docker image') {

      environment {
        dockerImage = "docker.jamf.one/sam-kube-cli"
        tag = 'latest'
      }

      agent { node { label 'docker-build' } }

      steps {
        container('docker-build') {
          unstash("build")
          sh "docker build -t ${dockerImage}:${tag} ."
        }
        container('docker-build') {
          sh "docker push ${dockerImage}:${tag}"
        }
      }
    }
  }
}


