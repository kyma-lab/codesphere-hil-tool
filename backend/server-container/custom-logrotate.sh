#!/bin/bash

LOG_DIR="/app/shared/logs"
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")

# Rename and compress rotated logs
for log_file in ${LOG_DIR}/*.log.1; do
    if [ -f "$log_file" ]; then
        mv "$log_file" "${LOG_DIR}/$(basename $log_file .1)_${TIMESTAMP}.log"
        gzip "${LOG_DIR}/$(basename $log_file .1)_${TIMESTAMP}.log"
    fi
done
