FROM ubuntu:latest
LABEL authors="azik"

ENTRYPOINT ["top", "-b"]