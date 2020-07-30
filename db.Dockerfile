FROM postgres:12-alpine

COPY ./project/data/init.sql ./

CMD ./