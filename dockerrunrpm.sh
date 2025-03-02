docker stop /transpod
docker rm /transpod
docker run --name transpod -d -p 8014:8014 -v /volume1/data/languages/japanese/podcasts/content:/app/content transpod
