#!/usr/bin/env groovy

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
            mode: 0555
    tty: true
"""
    }
  }

node('pypi') {
  stage('Build python package') {
    container('pypi') {
      checkout scm
      sh 'python setup.py sdist upload -r local'
      stash(name: "build")
    }
  }
}


node('docker-build') {
  def dockerImage = 'docker.jamf.one/sam-kube-cli'
  def tag = 'latest'

  stage('Build Docker image') {
    container('docker-build') {
      unstash("build")
      sh "docker build -t ${dockerImage}:${tag} ."
    }
  }
  stage('Push Fleet Docker Image') {
    container('docker-build') {
      sh "docker push ${dockerImage}:${tag}"
    }
  }
}


