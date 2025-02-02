#!/bin/zsh

# Number of parallel jobs allowed
MAX_JOBS=3



# Function to check the number of active background jobs
function wait_for_jobsgpt() {
  while true; do
    # Count only active background jobs
    active_jobs=$(jobs -rp | wc -l)
    echo $active_jobs
    if (( active_jobs < MAX_JOBS )); then
      break
    fi

    sleep 1  # Avoid excessive CPU usage
  done
}

wait_for_jobsclaude() {
    local max_jobs=3
    while true; do
        local current_jobs=$(jobs -p | wc -l | tr -d ' ')
        if [ $current_jobs -lt $max_jobs ]; then
            break
        fi
        sleep 1
    done
}

# Example loop with tasks
for i in {1..10}; do
  wait_for_jobsgpt  # Ensure job count doesn't exceed limit
  {
    echo "Starting job $i"
    sleep 3  # Simulate work
    echo "Job $i done"
  } &  # Run in background
done

# Wait for all background jobs to finish
wait
echo "All jobs completed"