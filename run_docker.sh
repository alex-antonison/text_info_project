# docker run -v $HOME/docker/data/:data/ text-processing

# docker run text-processing

docker run -it  --mount type=bind,source=$PWD/test,target=/data text-processing