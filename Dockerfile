# Stage 1: Build Angular app
FROM node:20-alpine as build

WORKDIR /app
COPY . .
RUN npm install
RUN npm run build --prod

# Stage 2: Serve with NGINX
FROM nginx:alpine

COPY --from=build /app/dist/ /usr/share/nginx/html
EXPOSE 80
