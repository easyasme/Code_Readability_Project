"""
Innen lehet elérni azokat a változók, amik nem változnak a program futása során.
"""
from traffic.consts.independent import *
from traffic.bash_scripts import *
from traffic.imports.builtins import dirname, join_path
from traffic import __name__ as PROJECT_NAME
from traffic import __file__ as TRAFFIC_PATH
from traffic.main import __file__ as MAIN_PATH

CONTAINER_ROOT_PATH = join_path("/", PROJECT_NAME)
CONTAINER_LANE_PATH = join_path(CONTAINER_ROOT_PATH, LANE)
HOST_ROOT_PATH = dirname(dirname(TRAFFIC_PATH))
CUSTOM_IMAGE_NAME = "{}/{}:{}".format(PROJECT_NAME, PROJECT_NAME, TENSORFLOW_VERSION)
ENABLE_DISPLAY_CONTAINER = "--env DISPLAY=$DISPLAY --mount type=bind,source={},destination={},readonly".format(
    X11_PATH, X11_PATH
)
MOUNT_PROJECT = "--mount type=bind,source={},destination={}".format(HOST_ROOT_PATH, CONTAINER_ROOT_PATH)
MOUNT_LANE = "--mount type=bind,source={},destination={}".format(HOST_LANE_PATH, CONTAINER_LANE_PATH)
NAME_CONTAINER = "--name {}".format(CONTAINER_NAME)
TENSORFLOW_IMAGE_NAME = "tensorflow/tensorflow:{}-gpu-py3".format(TENSORFLOW_VERSION)
IMAGE_WORKDIR = '--change "WORKDIR {}"'.format(CONTAINER_ROOT_PATH)
BUILD_PATH = join_path(HOST_ROOT_PATH, "build")
EGG_PATH = join_path(HOST_ROOT_PATH, PROJECT_NAME + ".egg-info")
DIST_PATH = join_path(HOST_ROOT_PATH, "dist")
DOCS_PATH = join_path(HOST_ROOT_PATH, "docs")
PYTEST_CACHE_PATH = join_path(HOST_ROOT_PATH, ".pytest_cache")
VENV_PATH = join_path(HOST_ROOT_PATH, "venv")
DOCS_BUILD_PATH = join_path(DOCS_PATH, "_build")
