FROM alpine:3.24

RUN apk add --no-cache autossh openssh-client netcat-openbsd curl

ENV AUTOSSH_GATETIME=0
ENV AUTOSSH_LOGFILE=/dev/stderr

COPY entrypoint.sh /usr/local/bin/tunnel-entrypoint.sh

# Supprime les fins de ligne Windows éventuelles.
RUN sed -i 's/\r$//' /usr/local/bin/tunnel-entrypoint.sh \
    && chmod 755 /usr/local/bin/tunnel-entrypoint.sh

ENTRYPOINT ["/usr/local/bin/tunnel-entrypoint.sh"]