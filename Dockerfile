FROM python:3.8

WORKDIR /streamlit_app

COPY requirements.txt /streamlit_app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /streamlit_app/requirements.txt

COPY ./streamlit /streamlit_app/
COPY .env /streamlit_app

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
