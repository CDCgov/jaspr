ECHO OFF
SET LOCAL_APP_DIR=c:/Projects/jaspr_cdc
SET TEMP_DIRECTORY=c:/frunk

SET RUN_STRING=docker run -i -t -v %LOCAL_APP_DIR%/app:/app -p 5000:5000 -w /app -e FLASK_APP=jaspr -e FLASK_DEBUG=True -e FLASK_ENV=development --rm cdcflu/jaspr:v1 /bin/bash -i -c ^"pip install -e . ; flask run -h 0.0.0.0^"
SET JUPYTER_STRING=docker run -i -t  -v %TEMP_DIRECTORY%:/frunk -p 8888:8888 continuumio/anaconda3 /bin/bash -c ^"/opt/conda/bin/conda install jupyter -y --quiet ^&^& mkdir /opt/notebooks ^&^& /opt/conda/bin/jupyter notebook --notebook-dir=/opt/notebooks --ip=*  --no-browser --allow-root^"
SET CMD_STRING=docker run -i -t -v %LOCAL_APP_DIR%/app:/app -p 5000:5000 -w /app -e FLASK_APP=jaspr -e FLASK_DEBUG=True -e FLASK_ENV=development --rm cdcflu/jaspr:v1 /bin/bash -i -c ^"pip install -e . ; /bin/bash^"

ECHO --------------------------------------------------------
ECHO This supports development of jaspr software within
ECHO a docker container.  Switches are:
ECHO  /b build Jaspr container
ECHO  /r run Jaspr in container
ECHO  /c open command prompt in Jaspr container
ECHO  /j run jupyter evironment in container
ECHO --------------------------------------------------------

SET RUN=
SET COMMANDLINE=
SET JUPYTER=
SET BUILD=

FOR %%i IN (%*) DO (
  IF [%%i]==[/r] SET RUN=1
  IF [%%i]==[/c] SET COMMANDLINE=1
  IF [%%i]==[/j] SET JUPYTER=1
  IF [%%i]==[/b] SET BUILD=1
)
IF [1]==[%BUILD%] (
    ECHO ON
    CD DockerBuild
    docker-compose build
    CD ..
    ECHO OFF
    ECHO Back to DOS
  )
IF [1]==[%RUN%] (
  ECHO ON
  %RUN_STRING%
  ECHO Back to DOS
)
IF [1]==[%COMMANDLINE%] (
  ECHO ON
  %CMD_STRING%
  ECHO OFF
  ECHO Back to DOS
)
IF [1]==[%JUPYTER%] (
  ECHO ON
  ECHO %JUPYTER_STRING%
  %JUPYTER_STRING%
  ECHO OFF
  ECHO Back to DOS
)
