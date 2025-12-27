# Use an official Python base image
FROM python:3.11-slim

# Set the working directory
ARG APP_HOME=/app
WORKDIR ${APP_HOME}

RUN addgroup --system django \
    && adduser --system --ingroup django django


# Copy requirements.txt into the container
COPY --chown=django:django requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Copy the rest of the application code into the container
COPY manage.py .

ADD --chown=django:django config ./config
ADD --chown=django:django genie ./genie

COPY --chown=django:django ./scripts/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint

RUN chown django:django ${APP_HOME}


# Run the command to start Streamlit
ENTRYPOINT ["/entrypoint"]
