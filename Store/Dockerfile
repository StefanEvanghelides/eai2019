FROM node

RUN mkdir /app
COPY . /app
WORKDIR /app

RUN npm install

RUN mkdir store-NL
RUN mv .env-nl .env
RUN npx webpack
RUN cp dist/bundle.js store-NL/bundle.js
RUN cp index.html store-NL/index.html
RUN sed -i 's|src="bundle"|src="store-nl/bundle"|g' store-NL/index.html

RUN mkdir store-GB
RUN mv .env-gb .env
RUN npx webpack 
RUN cp dist/bundle.js store-GB/bundle.js
RUN cp index.html store-GB/index.html
RUN sed -i 's|src="bundle"|src="store-gb/bundle"/|g' store-GB/index.html

FROM nginx
RUN mkdir /app
COPY nginx.conf /etc/nginx/nginx.conf
COPY --from=0 /app /app
CMD ["nginx", "-g", "daemon off;"]