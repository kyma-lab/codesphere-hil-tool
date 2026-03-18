`# HIL Backend (work in progress)

## Setup
- clone this repository
- put trained model into `./shared/base-models` folder
    - expected folder name per default is `bilstm-crf`, so it looks like this in the end: `shared/base-models/bilstm-crf/final-model.pt` (the other content of the zip is also required)
    - option 1: download [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.14213139.svg)](https://doi.org/10.5281/zenodo.14213139)
- put model for semantic search in base-folder
    - option 1: direct model download [here](https://mega.nz/file/BNIUwQDL#JjezCmjy5yTj4FLTVwQLskebMj2izcdkg0ksOon-FaA) (nextcloud always failed)
    - option 2: clone [this](https://huggingface.co/sentence-transformers/distiluse-base-multilingual-cased-v1/) repo with git lfs
    - should look like this in the end: `shared/base-model/distiluse...cased-v1/pytorch_model.bin` (the other content of the zip/repo is also required)
    - 
    - [Troubleshooting: git lfs is not a git command](https://stackoverflow.com/questions/48734119/git-lfs-is-not-a-git-command-unclear)
    - download legal norms: cd backend, `python tool_crawler.py`
    - create vectorized norms for semantic search from backend folder: `python server-container/handlers/database/wordembedding.py`
    - index both legal norms and vectorized norms: `python server-container/handlers/database/esearch.py` 
- cd backend, `sudo docker-compose up` (this can take up to 20min)
- wait for about 10 seconds, until the application is ready to be used
- use `sudo docker-compose up --build` if you changed a file to force rebuild of containers

## Testing

> Note: These tests are just testing the backend (`server.py` and its endpoints)

- for testing, `pytest` is being used (install with pip)
- before running the tests, start the backend docker-compose
- run all tests by typing `pytest` in the terminal while in the `/tests` folder

## Setup & Usage without Docker 

> Note: this has not been used in a long time, might be out of date. but is probably still useful.

- recommended: use conda (miniconda)
- we need python 3.8, so: `conda create -n hil38 python=3.8`
- activate environment: `conda activate hil38`
- install requirements: `pip install -r backend/requirements.txt`
- (install docker, if not installed already)
- cd backend, `sudo docker-compose up`
- install tesseract (for pdf processing):
    - `conda install -c conda-forge pytesseract` (the pip install did not work for me)
    - change to directory `/usr/share/tesseract-ocr/4.00/tessdata`
    - execute `sudo wget https://github.com/tesseract-ocr/tessdata/raw/main/deu.traineddata`
    - or: use `sudo apt-get install tesseract-ocr-deu`
- run `server.py`, `worker_predict.py`, `worker_train.py`
- running predictions requires at least one trained model available
    - store "xlm-roberta-large" model in `backend/base-models`
    - train a bilstm-model, and put it in `backend/bilstm-crf` (or contribute enough)
- contributions for bilstm are always possible, for xlm-roberta the base-model is required
- which model is used for prediction/training is hard-coded currently
- maybe: reset environment by running wipe.py (resets all queues, wipes mongodb, wipes user-data)
- you can now make requests to the server 🙃


## GPU Support

By default, the GPU is not used. To use the GPU, a Nvidia GPU is required (CUDA support).

To enable GPU support, perform the following steps:
- install cuda on the host (test success with `nvidia-smi` and check cuda version)
- install the nvidia-container-toolkit
    - `sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit`
- restart docker afterwards
    - `sudo systemctl restart docker`   
- for the training-container and prediction-container Dockerfiles ending in `_gpu`, replace the base image with a base image version that matches the cuda version installed on the host
- un-comment lines 43-47 and 66-70 in the `HIL_prototype/backend/docker-compose.yaml` and/or in the `HIL_prototype/docker-compose.yaml`, depending on which you want to use
    - list of available images [here](https://hub.docker.com/r/nvidia/cuda/tags)
- if you run into issues, uninstall and reinstall all nvidia drivers (ubuntu guide)
    - `sudo apt-get purge nvidia* bumblebee* nouveau`
    - `sudo apt-get --purge remove '*nvidia*'`
    - `sudo apt-get --purge remove '*cuda*'`
    - `sudo apt-get autoremove`
    - find gpu driver version with `sudo ubuntu-drivers install`
    - install it with `sudo apt install nvidia-driver-<version>`
    - sudo reboot
    - test with: `nvidia-smi`

- once the `nvidia-smi` command is working within the containers and shows the GPU, pytorch should also recognize the gpu, and you can use the Dockerfiles ending in `_gpu` (uncomment them, and comment the ones ending in `_nogpu`)
    - for testing the `nvidia-smi` command within containers, there is a container prepared in `backend/tests/gpu_support_container` 

