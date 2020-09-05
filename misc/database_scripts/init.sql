CREATE EXTENSION pg_trgm WITH SCHEMA pg_catalog;
CREATE EXTENSION fuzzystrmatch;

CREATE USER test WITH PASSWORD 'test';
CREATE DATABASE pricepickertest;
GRANT ALL PRIVILEGES ON DATABASE pricepickertest TO test;

\c pricepickertest

CREATE EXTENSION pg_trgm WITH SCHEMA pg_catalog;
CREATE EXTENSION fuzzystrmatch;