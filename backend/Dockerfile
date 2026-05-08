FROM public.ecr.aws/lambda/python:3.13

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY pyproject.toml uv.lock /tmp/build/
RUN cd /tmp/build && \
    uv export --frozen --no-dev --no-emit-project --no-hashes -o requirements.txt && \
    pip install --no-cache-dir --target ${LAMBDA_TASK_ROOT} -r requirements.txt && \
    rm -rf /tmp/build

COPY src/ ${LAMBDA_TASK_ROOT}/src/

CMD ["src.main.handler"]
