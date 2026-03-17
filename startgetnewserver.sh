#!/bin/sh
if tmux has-session -t getnew 2>/dev/null; then
  tmux attach -t getnew
else
  tmux new-session -s getnew "node getnewserver.cjs; exec $SHELL"
fi
