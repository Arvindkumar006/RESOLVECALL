# Use an official AWS Lambda Python runtime as a parent image
FROM public.ecr.aws/lambda/python:3.13

# Install system dependencies
RUN microdnf update -y && microdnf clean all

# Copy dependency definition
COPY requirements.txt ${LAMBDA_TASK_ROOT}

# Install python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files into the Lambda container
COPY core/ ${LAMBDA_TASK_ROOT}/core/
COPY tools/ ${LAMBDA_TASK_ROOT}/tools/
COPY agents/ ${LAMBDA_TASK_ROOT}/agents/
COPY hitl/ ${LAMBDA_TASK_ROOT}/hitl/
COPY bedrock_agentcore/ ${LAMBDA_TASK_ROOT}/bedrock_agentcore/

# Set the CMD to your Bedrock Agent handler
CMD [ "bedrock_agentcore.agentcore_app.lambda_handler" ]
