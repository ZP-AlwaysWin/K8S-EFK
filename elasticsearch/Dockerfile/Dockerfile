FROM elasticsearch:5.6.4

COPY entrypoint.sh bin/

RUN chmod a+x bin/entrypoint.sh &&\
    ./bin/elasticsearch-plugin install x-pack &&\
    apt-get update &&\
    apt-get install -y cron &&\
    apt-get clean

EXPOSE 9200 9300

CMD ["bin/entrypoint.sh"]
