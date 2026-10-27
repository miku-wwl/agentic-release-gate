# Both base images are pinned to verified linux/amd64 manifest digests.
FROM python:3.12.15-slim-bookworm@sha256:57d96f71de145a98e7ceca18ee4ade77bba4103a33a72dfaea026b23625c6bf0 AS build

WORKDIR /src
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY frontend/build_console.py frontend/build_console.py
COPY frontend/assets/console.css frontend/assets/console.css
COPY frontend/assets/console.js frontend/assets/console.js
COPY frontend/assets/mark.svg frontend/assets/mark.svg
COPY frontend/data/checkpoint.json frontend/data/checkpoint.json
COPY docs/phase4/duo-advisory.json docs/phase4/duo-advisory.json
COPY docs/phase4/evidence/artifact-manifest.json docs/phase4/evidence/artifact-manifest.json
COPY docs/phase4/evidence/research-results.json docs/phase4/evidence/research-results.json
COPY docs/phase4/examples/complete/report.json docs/phase4/examples/complete/report.json
COPY docs/phase4/examples/high_security/report.json docs/phase4/examples/high_security/report.json
COPY tests/required-tests.json tests/required-tests.json

RUN python frontend/build_console.py --output-dir /site

FROM nginxinc/nginx-unprivileged:1.31.7-alpine3.24@sha256:c3bcf3d1a53a027bfa515b9fe4fbbe7bf6b791476a5af853de439ad494b145bd

ARG SOURCE_SHA
LABEL org.opencontainers.image.title="ReleaseGate read-only Decision Console" \
      org.opencontainers.image.source="https://github.com/miku-wwl/agentic-release-gate" \
      org.opencontainers.image.revision="${SOURCE_SHA}" \
      org.opencontainers.image.licenses="MIT" \
      com.releasegate.deployment-mode="READ_ONLY_SHOWCASE"

COPY --chown=101:101 deploy/azure/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build --chown=101:101 /site/ /usr/share/nginx/html/

USER 0
RUN rm -f /usr/share/nginx/html/50x.html \
    && test "$(find /usr/share/nginx/html -type f | wc -l)" -eq 12 \
    && printf '%s\n' "$SOURCE_SHA" | grep -Eq '^[0-9a-f]{40}$'
USER 101
EXPOSE 8080
CMD ["nginx", "-g", "daemon off;"]
