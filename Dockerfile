FROM node:alpine

WORKDIR /app

COPY package.json .

RUN npm install

COPY podserver.cjs .
# Cache bust
COPY views views
COPY manifest.json .
COPY public public 
COPY transpod.config.json .
EXPOSE 8014

CMD ["node", "podserver.cjs"]
