FROM python:3.9.20-slim-bookworm

ENTRYPOINT /bin/bash

# Install preequisites.
RUN apt-get update -y && apt-get install -y curl

# Add $HOME/.local/bin to the PATH.
RUN echo "export PATH=\"\$HOME/.local/bin:\$PATH\"" >> "$HOME/.bashrc"

# Download Pants builder.
RUN curl --proto '=https' --tlsv1.2 -fsSLO https://static.pantsbuild.org/setup/get-pants.sh && \
    chmod +x get-pants.sh && \
    ./get-pants.sh && \
    rm get-pants.sh
ENV PATH="/root/.local/bin:$PATH"

# Force download and venv setup for Pants version to be used by the project.
RUN mkdir /setup-pants
WORKDIR /setup-pants
ADD ./pants.toml .
RUN pants --version

WORKDIR /root
RUN rm -rf /setup-pants
