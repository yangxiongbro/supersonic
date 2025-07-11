
FROM nginx

RUN mkdir -p /usr/share/nginx/html
ADD supersonic-webapp.tar.gz /usr/share/nginx/html/

# COPY supersonic/webapp/nginx.conf /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 9000
