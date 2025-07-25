FROM node:alpine

WORKDIR /app

COPY package.json .

RUN npm install

COPY podserver.cjs .
# Cache bust
COPY views views
COPY manifest.json .
COPY public public 

EXPOSE 8014

CMD ["node", "podserver.cjs"]
