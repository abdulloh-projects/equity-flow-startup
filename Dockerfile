FROM python:3.13-slim AS builder

WORKDIR /app

COPY equity-flow-startup/src ./src
COPY equity-flow-startup-grpc/protos/ src/external/equity-flow-startup/protos/

RUN pip install --no-cache-dir grpcio-tools

RUN bash src/scripts/generate_protos.sh


FROM python:3.13-slim

WORKDIR /app

COPY equity-flow-startup/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY --from=builder /app/src .

CMD [ "python", "main.py" ]
