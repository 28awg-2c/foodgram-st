# build env
FROM node:21.7.1-alpine
WORKDIR /work_dir
COPY package*.json ./
RUN npm install
COPY . ./
RUN npm run build
# CMD cp -r build result_build
