#!/bin/bash

app_dir=/home/jaspr/jaspr_cdc/app
temp_dir=/home/jaspr/frunk

run_string="docker run -i -t -v $app_dir:/app -p 5000:5000 -w /app -e FLASK_APP=jaspr -e FLASK_DEBUG=True -e FLASK_ENV=development --rm cdcflu/jaspr:v1 /bin/bash -i -c \"pip install -e . ; flask run -h 0.0.0.0\""
cmd_string="docker run -i -t -v $app_dir:/app -p 5000:5000 -w /app -e FLASK_APP=jaspr -e FLASK_DEBUG=True -e FLASK_ENV=development --rm cdcflu/jaspr:v1 /bin/bash -i -c \"pip install -e . ; /bin/bash\""
jupyter_string="docker run -i -t  -v $temp_dir:/frunk -p 8888:8888 continuumio/anaconda3 /bin/bash -c \"/opt/conda/bin/conda install jupyter -y --quiet && mkdir /opt/notebooks && /opt/conda/bin/jupyter notebook --notebook-dir=/opt/notebooks --ip=*  --no-browser --allow-root\""

run=
cmdline=
jupyter=
build=

while [ "$1" != "" ]; do
    case $1 in
        -b | --build )   build=1
                         ;;
        -c | --cmdline ) cmdline=1
                         ;;
        -j | --jupyter ) jupyter=1
                         ;;
        -r | --run )     run=1
                         ;;
    esac
    shift
done

if [ "$build" = "1" ]; then
    cd $local_app_dir/DockerBuild && docker-compose build && cd ..
elif [ "$cmdline" = "1" ]; then
    eval $cmd_string
elif [ "$jupyter" = "1" ]; then
    eval $jupyter_string
elif [ "$run" = "1" ]; then
    eval $run_string
else
    echo "-----------------------------------------------------------"
    echo " This supports development of jaspr software within"
    echo " a docker container."
    echo
    echo "  -b | --build     build the container"
    echo "  -c | --cmdline   run the container and provide a command line"
    echo "  -j | --jupyter   run jupyter in the container"
    echo "  -r | --run       run the flask app in the container"
    echo
    echo "-----------------------------------------------------------"
fi
