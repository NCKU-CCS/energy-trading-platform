FROM python:3.6.8

# Install Pipenv
RUN pip install pipenv==2018.11.26
ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8

# Install dependencies
COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock

RUN pipenv install --deploy --system
RUN pip install gunicorn==19.9.0

COPY ./pt /pt
WORKDIR /pt

RUN useradd -ms /bin/bash pt
RUN chown -R pt:pt /pt
USER pt

EXPOSE 5000

CMD ["gunicorn", "--certfile=/pt/certificate/fullchain.pem", "--keyfile=/pt/certificate/privkey.pem", "-c", "gunicorn.ini", "wsgi:app"]
