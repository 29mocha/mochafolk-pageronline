# Gunakan image Python yang ramping
FROM python:3.11-slim

# Atur environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Atur direktori kerja di dalam container
WORKDIR /app

# Salin file requirements dan instal dependensi
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Salin seluruh proyek ke dalam direktori kerja
COPY . /app/

# Kita tidak lagi menggunakan ENTRYPOINT di sini
