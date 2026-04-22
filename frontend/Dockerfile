FROM node:22

WORKDIR /app

COPY package.json yarn.lock ./

RUN yarn install

COPY app.js .

COPY views ./views

RUN useradd app

USER app

# check if the web service responds
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
CMD wget --no-verbose --tries=1 --spider http://localhost:3000 || exit 1

EXPOSE 3000

CMD ["yarn", "start"]