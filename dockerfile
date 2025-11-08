#build data
FROM python::3.10-slim AS builder

#env
ENV PYTHONDONTWRITEBYTECODE=1 \ 
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_ROOT_USER_ACTION=ignore \ 
    PORT=8000

WORKDIR /app
#install linux dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      curl \
      ca-certificates \
      libopenblas3 \
      libsndfile1 \
      libgomp1 \
    && rm -rf /var/lib/apt/lists/*

#python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt 
COPY . . 
  #run code
EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "$PORT8000"]