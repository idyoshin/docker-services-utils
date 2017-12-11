FROM library/python
MAINTAINER Ilya Dyoshin

RUN pip3 install Flask aiohttp docker

EXPOSE 6000

ADD service_create_update.py /service/service_utils.py

ENTRYPOINT ["/usr/bin/python3",  "/service/service_utils.py"]
