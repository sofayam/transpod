docker stop /transpod
docker rm /transpod
docker run --restart=unless-stopped --name transpod -d -p 8014:8014 -v /mnt/appdata/transpod/content:/app/content transpod
