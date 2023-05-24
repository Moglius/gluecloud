from __future__ import absolute_import, unicode_literals
import os, subprocess
from celery import Celery, shared_task
from django.conf import settings
from git import Repo
import shutil

repos_create = {
  "aws": "https://github.com/Moglius/aws-deploy.git",
  "azure": "https://github.com/Moglius/azure-deploy"
}

repos_destroy = {
  "aws": "https://github.com/Moglius/aws-destroy.git",
  "azure": "https://github.com/Moglius/azure-deploy"
}


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gluecloud.settings")
app = Celery("gluecloud")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

def get_repo_url(provider, create=True):
  if create:
    return repos_create[provider]
  return repos_destroy[provider]

def get_working_dir(task_id):
  return f"/tmp/{task_id}"

def clone_repo(instance_data, working_dir, create=True):
  repo_url = get_repo_url(instance_data['provider'], create)
  print(f"Clonning repo {repo_url} on {working_dir}.")
  Repo.clone_from(repo_url, working_dir)
  print(f"Repo {repo_url} cloned on {working_dir}.")

def clean_repo(working_dir):
  print(f"Removing working directory on {working_dir}.")
  shutil.rmtree(working_dir)
  print(f"Working directory {working_dir} removed.")

def aws_perform_create(working_dir, instance_data):
  try:
    print(f"Running terraform init command.")
    output = subprocess.check_output(f"terraform -chdir={working_dir} init", shell=True)
    print(f"Running terraform plan command.")
    output1 = subprocess.check_output(f"terraform -chdir={working_dir} plan -var=instance_tag_name='{instance_data['name']}' -var=ami_id='{instance_data['ami_id']}' -var=instance_type='{instance_data['instance_type']}' -var=availability_zone='{instance_data['availability_zone']}' -out=ec2.tfplan", shell=True)
    print(f"Running terraform apply command.")
    output2 = subprocess.check_output(f"terraform -chdir={working_dir} apply 'ec2.tfplan'", shell=True)
    print(f"Terraform executed successfully.")
    output2 = output2.decode("utf-8")
    print(output2)
    return output2
  except Exception as e:
    print(e)
    return 'failed inside terrablock'

def azure_perform_create(working_dir, instance_data):
  try:
    print(f"Running terraform init command.")
    output = subprocess.check_output(f"terraform -chdir={working_dir} init", shell=True)
    print(f"Running terraform plan command.")
    output1 = subprocess.check_output(f"terraform -chdir={working_dir} plan -var=instance_name='{instance_data['name']}' -out=ec2.tfplan", shell=True)
    print(f"Running terraform apply command.")
    output2 = subprocess.check_output(f"terraform -chdir={working_dir} apply 'ec2.tfplan'", shell=True)
    print(f"Terraform executed successfully.")
    output2 = output2.decode("utf-8")
    print(output2)
    return output2
  except Exception as e:
    print(e)
    return 'failed inside terrablock'

def terraform_new_server(working_dir, instance_data):
  if instance_data['provider'] == 'aws':
    aws_perform_create(working_dir, instance_data)
  else:
    azure_perform_create(working_dir, instance_data)

def aws_perform_destroy(working_dir, instance_data):
  try:
    print(f"Running terraform init command.")
    output = subprocess.check_output(f"terraform -chdir={working_dir} init", shell=True)
    print(f"Running terraform import command.")
    output1 = subprocess.check_output(f"terraform -chdir={working_dir} import aws_instance.myvm '{instance_data['instance_id']}'", shell=True)
    print(f"Running terraform destroy command.")
    output2 = subprocess.check_output(f"terraform -chdir={working_dir} apply -destroy -auto-approve", shell=True)
    print(f"Terraform executed successfully.")
    output2 = output2.decode("utf-8")
    print(output2)
    return output2
  except Exception as e:
    print(e)
    return 'failed inside terrablock'

def azure_perform_destroy(working_dir, instance_data):
  try:
    print(f"Running terraform init command.")
    output = subprocess.check_output(f"terraform -chdir={working_dir} init", shell=True)
    print(f"Running terraform plan command.")
    output1 = subprocess.check_output(f"terraform -chdir={working_dir} plan -var=instance_name='{instance_data['name']}'", shell=True)
    print(f"Running terraform import command.")
    output2 = subprocess.check_output(f"terraform -chdir={working_dir} import azurerm_linux_virtual_machine.main '{instance_data['instance_id']}'", shell=True)
    print(f"Running terraform destroy command.")
    output3 = subprocess.check_output(f"terraform -chdir={working_dir} apply -destroy -auto-approve", shell=True)
    print(f"Terraform executed successfully.")
    output3 = output3.decode("utf-8")
    print(output3)
    return output3
  except Exception as e:
    print(e)
    return 'failed inside terrablock'


def terraform_destroy_server(working_dir, instance_data):
  if instance_data['provider'] == 'aws':
    aws_perform_destroy(working_dir, instance_data)
  else:
    azure_perform_destroy(working_dir, instance_data)

    


@app.task(bind=True)
def async_create_instance(self, instance_data):
  working_dir = get_working_dir(self.request.id)
  clone_repo(instance_data, working_dir)

  terraform_new_server(working_dir, instance_data)

  clean_repo(working_dir)
  
  return ""

@app.task(bind=True)
def async_destroy_instance(self, instance_data):
  working_dir = get_working_dir(self.request.id)
  clone_repo(instance_data, working_dir, create=False)

  terraform_destroy_server(working_dir, instance_data)

  clean_repo(working_dir)
  
  return ""