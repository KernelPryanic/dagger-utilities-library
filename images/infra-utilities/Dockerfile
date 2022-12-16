FROM python:3.11-alpine

ARG TF_VERSION=1.3.5
ARG TF_DOCS_VERSION=0.16.0
ARG TF_SEC_VERSION=1.28.1

RUN apk add --update --no-cache git bash curl tar unzip docker openrc
RUN rc-update add docker boot

WORKDIR /tmp

RUN curl -sSLo ./terraform.zip https://releases.hashicorp.com/terraform/${TF_VERSION}/terraform_${TF_VERSION}_linux_amd64.zip && \
    unzip terraform.zip && \
    chmod +x terraform && \
    mv terraform /usr/bin/ && \
    rm -rf *

RUN curl -sSLo ./terraform-docs.tar.gz https://terraform-docs.io/dl/v${TF_DOCS_VERSION}/terraform-docs-v${TF_DOCS_VERSION}-$(uname)-amd64.tar.gz && \
    tar -xzf terraform-docs.tar.gz && \
    chmod +x terraform-docs && \
    mv terraform-docs /usr/local/bin/ && \
    rm -rf *

RUN curl -sSLo ./tfsec https://github.com/aquasecurity/tfsec/releases/download/v${TF_SEC_VERSION}/tfsec-$(uname)-amd64 && \
    chmod +x tfsec && \
    mv tfsec /usr/local/bin/ && \
    rm -rf *

RUN pip install --no-cache-dir "git+https://github.com/KernelPryanic/dagger-utilities-library.git@refactor#egg=dul[scripts]"

WORKDIR /opt
