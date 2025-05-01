FROM node:alpine

WORKDIR /app

COPY package.json .

RUN npm install

COPY podserver.cjs .
COPY views views

EXPOSE 8014

CMD ["node", "podserver.cjs"]
