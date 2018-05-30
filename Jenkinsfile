#!/usr/bin/env groovy

node('docker-build') {
  def dockerImage = 'docker.jamf.one/sam-kube-cli'
  def tag = 'latest'

  stage('Build Docker image') {
    container('docker-build') {
      checkout scm
      sh "docker build -t ${dockerImage}:${tag} ."
    }
  }
  stage('Push Fleet Docker Image') {
    container('docker-build') {
      sh "docker push ${dockerImage}:${tag}"
    }
  }
}


