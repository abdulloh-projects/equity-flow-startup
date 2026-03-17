import os
import signal
from concurrent import futures

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

import grpc
from django.conf import settings

from app.generated import startup_pb2_grpc
from app.startupp.services.startup_service import StartupService


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    startup_pb2_grpc.add_StartupServiceServicer_to_server(StartupService(), server)
    server.add_insecure_port(f"{settings.HOST}:{settings.PORT}")
    server.start()
    print("🚀 gRPC server running on:", f"{settings.HOST}:{settings.PORT}")

    def handle_shutdown(signum, frame):
        print("🛑 Shutting down gRPC server...")
        server.stop(grace=5)

    signal.signal(signal.SIGTERM, handle_shutdown)
    signal.signal(signal.SIGINT, handle_shutdown)

    server.wait_for_termination()


if __name__ == "__main__":
    serve()
