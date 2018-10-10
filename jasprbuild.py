#!/usr/bin/python
#coding: utf-8
import glob, subprocess, argparse, sys

RUN_STRING="docker run -i -t -v c:/Projects/jaspr/app:/app -p 5000:5000 -w /app -e FLASK_APP=jaspr -e FLASK_DEBUG=True --rm cdcflu/jaspr:v1 /bin/bash -i -c \"pip install -e . ; flask run -h 0.0.0.0\""
CMD_STRING="docker run -i -t -v c:/Projects/jaspr/app:/app -p 5000:5000 -w /app -e FLASK_APP=jaspr -e FLASK_DEBUG=True --rm cdcflu/jaspr:v1 /bin/bash -i -c \"pip install -e . ; /bin/bash\""
JUPYTER_STRING="docker run -i -t  -v c:/frunk:/frunk -p 8888:8888 continuumio/anaconda3 /bin/bash -c \"/opt/conda/bin/conda install jupyter -y --quiet && mkdir /opt/notebooks && /opt/conda/bin/jupyter notebook --notebook-dir=/opt/notebooks --ip=*  --no-browser --allow-root\""

BUILD_STRING="cd DockerBuild && docker-compose build && cd .."

def completeTask( taskCommandLine):
    print(taskCommandLine)
    subprocess.call(taskCommandLine, shell=True)
    return

def main():
    parser = argparse.ArgumentParser(description="build and run jaspr in a container")
    parser.add_argument('-b','--build', help="", action="store_true")
    parser.add_argument('-r','--run', help="", action="store_true")
    parser.add_argument('-c','--command', help="", action="store_true")
    parser.add_argument('-j','--jupyter', help="", action="store_true")

    args = parser.parse_args()
    print("--------------------------------------------------------")
    print(" This will build and run the jaspr software within     ")
    print(" a docker container                                     ")
    print("                                                        ")
    print(" -b(--build) to build the container                     ")
    print(" -r(--run) to run the container                         ")
    print(" -c(--command) command prompt                           ")
    print(" -j(--jupyter) run jupyter evironment                   ")
    print("--------------------------------------------------------")
    if (args.build):
        completeTask(BUILD_STRING)
    if (args.run):
         completeTask(RUN_STRING)
    else:
         if (args.command):
             completeTask(CMD_STRING)
         else:
             if (args.jupyter):
                 completeTask(JUPYTER_STRING)

if __name__ == '__main__':
        main()
