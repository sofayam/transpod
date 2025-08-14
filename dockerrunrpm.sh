docker stop /transpod
docker rm /transpod
docker run --restart=unless-stopped --name transpod -d -p 8014:8014 -v /volume2/transpodcontent/content:/app/content transpod
