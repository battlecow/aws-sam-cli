import logging
import time
from os import path
import yaml
from dateutil.tz import tzutc
import datetime
from kubernetes import client, config

LOG = logging.getLogger(__name__)


class Pod(object):

    def __init__(self,
                 image,
                 cmd,
                 working_dir,
                 host_dir,
                 memory_limit_mb=None,
                 exposed_ports=None,
                 entrypoint=None,
                 env_vars=None,
                 docker_client=None,
                 namespace="default"):
        self._image = image
        self._cmd = cmd
        self._working_dir = working_dir
        self._host_dir = host_dir
        self._exposed_ports = exposed_ports
        self._entrypoint = entrypoint
        self._env_vars = env_vars
        self._memory_limit_mb = memory_limit_mb
        self._network_id = None
        self._pod_name = None
        self._namespace = namespace

        # Runtime properties of the container. They won't have value until container is created or started
        self.id = None

    def create(self):
        LOG.debug("Kubernetes create called")
        try:
            try:
                LOG.debug("Trying to load Kubernetes config from inside of cluster")
                config.load_incluster_config()
            except:
                LOG.debug("Trying to load Kubernetes config from outside of cluster")
                config.load_kube_config()
        except:
            LOG.error("Unable to load Kubernetes config from anyplace, everything fails now")
        LOG.debug("Kubernetes initialized")

        try:
            with open(path.join(path.dirname(__file__), "pod.yaml")) as f:
                kube_pod = yaml.load(f)
            LOG.debug("Loaded pod template")
        except:
            LOG.error("Unable to open pod yaml template")

        kube_client = client.CoreV1Api()

        kubeenv = []
        for key, value in self._env_vars.iteritems():
            kubeenv.append({'name': key, 'value': value})

        kube_pod['spec']['containers'][0]['image'] = self._image

        kube_pod['spec']['containers'][0]['env'] = kubeenv

        kube_pod['spec']['containers'][0]['args'] = self._cmd

        kube_pod['metadata']['namespace'] = self._namespace

        kube_pod['metadata']['name'] += "-%s" % str(int(time.time()))

        resp = kube_client.create_namespaced_pod(
            body=kube_pod, namespace=self._namespace)

        self._pod_name = resp.metadata.name
        LOG.debug("Pod created: %s" % self._pod_name)

        LOG.debug("Pod created. status='%s'" % str(resp.status))

        return self._pod_name

    def start(self, input_data=None):
        LOG.debug("Kubernetes start called")
        LOG.debug(input_data)
        time.sleep(5)
        pass

    def delete(self):
        LOG.debug("Kuberenetes delete called")
        kube_client = client.CoreV1Api()
        deleteOptions = {
            'kind': 'DeleteOptions',
            'apiVersion': 'v1',
            'propagationPolicy': 'Foreground'
        }
        resp = kube_client.delete_namespaced_pod(
            name=self._pod_name, namespace=self._namespace, body=deleteOptions)
        LOG.debug("Pod deleted. status='%s'" % str(resp.status))
        pass

    def wait_for_logs(self, stdout=None, stderr=None):
        # Return instantly if we don't have to fetch any logs
        if not stdout and not stderr:
            return
        logClient = client.CoreV1Api()
        logs_itr = logClient.read_namespaced_pod_log(name=self._pod_name, namespace=self._namespace, follow=True)
        self._write_container_output(logs_itr, stdout=stdout, stderr=stderr)

    @staticmethod
    def _write_container_output(output_itr, stdout=None, stderr=None):
        """
        Based on the data returned from the Container output, via the iterator, write it to the appropriate streams

        Parameters
        ----------
        output_itr: Iterator
            Iterator returned by the Docker Attach command
        stdout: io.BaseIO, optional
            Stream to write stdout data from Container into
        stderr: io.BaseIO, optional
            Stream to write stderr data from the Container into
        """
        for data in output_itr:
            stdout.write(data)

    @property
    def network_id(self):
        """
        Gets the ID of the network this container connects to
        :return string: ID of the network
        """
        return self._network_id

    @network_id.setter
    def network_id(self, value):
        """
        Set the ID of network that this container should connect to

        :param string value: Value of the network ID
        """
        self._network_id = value

    @property
    def image(self):
        """
        Returns the image used by this container

        :return string: Name of the container image
        """
        return self._image

    def is_created(self):
        """
        Checks if a container exists?

        :return bool: True if the container was created
        """
        return self.id is not None
