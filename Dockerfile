FROM node:alpine

WORKDIR /app

COPY podserver.cjs .
COPY views views
COPY package.json .

RUN npm install

EXPOSE 8014

CMD ["node", "podserver.cjs"]