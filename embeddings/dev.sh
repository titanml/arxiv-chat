docker build . -t embed && docker run --name embed --gpus all -v $PWD/app:/code/app -v $PWD/data:/code/data  -p 7000:80 -it --rm embed
