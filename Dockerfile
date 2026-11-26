FROM python:3.12
WORKDIR /app
COPY app.py .
USER 65532:65532
EXPOSE 8080
CMD ["python", "-u", "app.py"]