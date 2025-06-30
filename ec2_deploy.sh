#!/bin/bash

set -e

# Load environment variables from .env file
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
else
    echo ".env file not found. Exiting."
    exit 1
fi

# Check required env vars
if [[ -z "$AWS_ACCESS_KEY_ID" || -z "$AWS_SECRET_ACCESS_KEY" || -z "$AWS_SESSION_TOKEN" || -z "$KEY_NAME" ]]; then
    echo "Missing one or more required environment variables."
    exit 1
fi

# Export AWS credentials
export AWS_ACCESS_KEY_ID
export AWS_SECRET_ACCESS_KEY
export AWS_SESSION_TOKEN

TF_DIR="./terraform/ec2"        # Directory containing Terraform files
CONFIG_SCRIPT="ec2_config.sh" # script path on script on local machine
REMOTE_SCRIPT="/home/ubuntu/ec2_config.sh" # script path on ec2 instance
PEM_PATH="~/.ssh/demo-finops.pem"

# Check for Terraform installation
if ! command -v terraform &> /dev/null; then
    echo "Terraform is not installed. Please install it and retry."
    exit 1
fi

# Set up the working directory
if [ ! -d "$TF_DIR" ]; then
    echo "Terraform directory '$TF_DIR' not found."
    exit 1
fi

cd "$TF_DIR"

echo "Initializing Terraform..."
terraform init -input=false

echo "Planning infrastructure..."
terraform plan -var="key_name=$KEY_NAME"

echo "Applying infrastructure..."
terraform apply -auto-approve -var="key_name=$KEY_NAME"

echo "Fetching public IP from Terraform output..."
PUBLIC_IP=$(terraform output -raw instance_public_ip)
cd - > /dev/null

echo "EC2 instance public IP: $PUBLIC_IP"

# Wait for SSH to be ready
echo "Waiting for EC2 instance to become available over SSH..."
until ssh -o StrictHostKeyChecking=no -i "$PEM_PATH" ubuntu@$PUBLIC_IP 'echo SSH is ready'; do
    sleep 5
done

echo "SSH is ready. Proceeding with remote setup..."

# Copy the setup script to the instance
scp -i "$PEM_PATH" -o StrictHostKeyChecking=no "$CONFIG_SCRIPT" ubuntu@$PUBLIC_IP:$REMOTE_SCRIPT

# Run the setup script on the EC2 instance
ssh -i "$PEM_PATH" -o StrictHostKeyChecking=no ubuntu@$PUBLIC_IP "chmod +x $REMOTE_SCRIPT && sudo bash $REMOTE_SCRIPT"
