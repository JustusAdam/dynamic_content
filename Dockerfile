# use debian base image
FROM debian
# that's me, hello
MAINTAINER Justus Adam
# add a human readable name
USER dynamic_content_framework
# install python3
RUN apt-get update && apt-get install -y \
    python3 
# set working directory already
WORKDIR /dyc
# expose default ports for http and https
EXPOSE 9012 9443
CMD [""]
# call the main application
ENTRYPOINT ["python3", "application/main.py"]