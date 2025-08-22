podman stop /transpod
podman rm /transpod

podman run --name transpod -d -p 8099:8014 -v ./content:/app/content transpod
