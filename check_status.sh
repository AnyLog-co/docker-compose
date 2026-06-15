#!/usr/bin/env bash

for ID in 0 1 2 3 4 5 ; do
  echo "ID: ${ID}"
  for CMD in "get operator" "get streaming" ; do
    if [[ ${ID} -gt 0 ]] ; then
      CMD="helper psql ${ID} ${CMD}"
    fi
    echo "Running: ${CMD}"
    curl -X POST http://127.0.0.1:32149 \
      -H "Content-Type: application/json" \
      -d "{\"command\": \"${CMD}\", \"AnyLog-Agent\": \"AnyLog/1.23\"}" -w "\n"
  done
done