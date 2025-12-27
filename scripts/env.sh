#!/usr/bin/env bash

export SERVER_ROLE=main.py
export SERVER_TIMEOUT=4000
export PORT=9896
#export API_KEYS=123456wer12wegfqwtg24t2462f
#export OPEN_API_TOKEN=sk-test123
export DATABASE_URL=postgres://userStrategy:123@localhost:5432/strategy?sslmode=disable

#envconfig:"DATABASE_URL_MAIN" default:"postgres://userStrategy:123@localhost:5432/strategy?sslmode=disable"