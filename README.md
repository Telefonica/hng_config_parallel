# Dockers used in the configuration of PW HNG

We work with different, containerized and splitted pieces of code to maintain an atomic workflow that helps us to know where the problem appeared in case we have any.

The splitted and containerized configuration also allow us to run this pieces in different worflows and the host machine just need to have installed docker in order to run this containers.

The container we have at this momment:
- Terraform. Container with the terraform binary to deploy infrastructure as code
- Ansible. Container with ansible binary to configure and provision other machines
- HNG-config-gen. Container with the code that allow us to input an hng.yml with the configuration we want on the HNG and it output is an HNG configuration file that we can inject on the VNF
- HNG-provisioner. Container that inject the HNG config file and apply it
- TestInfra. Container with the code to test infrastructure, such us IPs, NICs, etc.

# Workflow

We have added the hng_functional.groovy, the declarative job we use to run all the code to provision, configure and test the HNG. You have all the code that is run in this file and the order it is execute..

If you see any discordance with the path on this file, pls note that we usually have this files in different repos.

