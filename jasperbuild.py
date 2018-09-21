#!/usr/bin/python
#coding: utf-8 
import glob, subprocess, argparse, sys

RUN_STRING="docker run -i -t -v c:/Projects/jasper/app:/app -p 5000:5000 -e FLASK_APP=hello.py -w /app  --rm cdcflu/jasper:v1 "

BUILD_STRING="cd DockerBuild && docker-compose build && cd .."

def completeTask( taskCommandLine):
    print(taskCommandLine)
    subprocess.call(taskCommandLine, shell=True)
    return

def main():
    parser = argparse.ArgumentParser(description="build and run jasper in a container")
    parser.add_argument('-b','--build', help="", action="store_true")
    parser.add_argument('-r','--run', help="", action="store_true")

    args = parser.parse_args()
    print("--------------------------------------------------------")
    print(" This will build and run the Jasper software within     ")   
    print(" a docker container                                     ")
    print("                                                        ")
    print(" -b(--build) to build the container                     ")
    print(" -r(--run) to run the container                                     ")
    print("--------------------------------------------------------")
    if (args.build):
        completeTask(BUILD_STRING)
    if (args.run):
         completeTask(RUN_STRING)

if __name__ == '__main__':
        main()
