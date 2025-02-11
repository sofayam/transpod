#!/bin/zsh

MAX_JOBS=3  # Max parallel jobs
PIDS=()  # Array to store PIDs

wait_for_jobs() {
  while (( ${#PIDS[@]} >= MAX_JOBS )); do
    NEW_PIDS=()
    for pid in "${PIDS[@]}"; do
      if kill -0 "$pid" 2>/dev/null; then
        NEW_PIDS+=("$pid")  # Keep running jobs
      fi
    done
    PIDS=("${NEW_PIDS[@]}")  # Update the tracked jobs
    sleep 1
  done
}

for i in {1..10}; do
  wait_for_jobs  # Wait if too many jobs are running
  foo=$RANDOM
  {
 
    echo "Starting job $i"


    bar=$(( foo % 15 + 1))
    echo "delay is" $bar
    sleep $bar  # Simulate work
    # sleep $(($(od -An -N2 -i /dev/urandom | tr -d ' ' | awk '{print $1 % 5 + 1}')))
    echo "Job $i done"
  } &

  PIDS+=($!)  # Store the PID of the background job
done
