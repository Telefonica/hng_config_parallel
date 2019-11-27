#!/usr/bin/env groovy
folder('core-networkcloud-infra/vnfs_test') {
    description('Folder for test vnfs')
}

job("core-networkcloud-infra/vnfs_test/hng_functional") {
	description("HNG functional test")
	label('pro-magne-slave-02')
	parameters {
		stringParam("GIT_BRANCH", "develop", "Rama del repo core-networkcloud-rgw")
		stringParam("AWS_DEFAULT_REGION", "eu-west-1", "")
		stringParam("AWS_DEFAULT_OUTPUT", "json", "")
		stringParam("ENVIRONMENT_NAME", "Network-Cloud", "")
		stringParam("AWS_KEY", "whitecloud.pem", "")
	}
	scm {
		git {
			remote {
				github("Telefonica/core-networkcloud-rgw", "https")
				credentials("github_cred")
			}
			branch("\${GIT_BRANCH}")
		}
	}
	wrappers {
		credentialsBinding {
			amazonWebServicesCredentialsBinding {
				accessKeyVariable("AWS_ACCESS_KEY_ID")
				secretKeyVariable("AWS_SECRET_ACCESS_KEY")
				credentialsId("94e5da4a-42c6-4ed8-9ddb-73f3bff48d68")
			}
		}
	}
	steps {
		shell(
"""
set -x
export AWS_ACCESS_KEY_ID=\${AWS_ACCESS_KEY_ID}
export AWS_SECRET_ACCESS_KEY=\${AWS_SECRET_ACCESS_KEY}
export AWS_DEFAULT_REGION=\${AWS_DEFAULT_REGION}
export AWS_DEFAULT_OUTPUT=\${AWS_DEFAULT_OUTPUT}

LAST_BOX_HNG_PATH=`aws s3 ls s3://networkcloud-packer-images-\${AWS_DEFAULT_REGION}/core-networkcloud-rgw/\${GIT_BRANCH}/ --recursive | grep '.box\$' | sort | tail -n 1 | awk '{print \$4}'`
LAST_BOX_HNG="\$(basename \$LAST_BOX_HNG_PATH)"

LAST_BOX_UBUNTU1804_PATH=`aws s3 ls s3://networkcloud-utils/ --recursive | grep 'ubuntu1804_vagrant_box_image' | sort | tail -n 1 | awk '{print \$4}'`
LAST_BOX_UBUNTU1804="\$(basename \$LAST_BOX_UBUNTU1804_PATH)"

aws s3 cp s3://networkcloud-packer-images-\${AWS_DEFAULT_REGION}/core-networkcloud-rgw/\${GIT_BRANCH}/\${LAST_BOX_HNG} \${WORKSPACE}/iac/bootstrap-image/vagrant/\${LAST_BOX_HNG}

sed -i "s+testhngyaml+\${LAST_BOX_HNG}+g" \${WORKSPACE}/iac/bootstrap-image/vagrant/Vagrantfile

docker pull dockerhub.hi.inet/networkcloud/vagrant
docker pull dockerhub.hi.inet/networkcloud/testinfra:3.2.0
docker pull dockerhub.hi.inet/networkcloud/ansible:2.9.0

#Deploy HNG 
docker run                                                            \\
       --rm                                                           \\
       -v \${WORKSPACE}/iac/bootstrap-image/vagrant:/srv               \\
       -v /var/run/libvirt/libvirt-sock:/var/run/libvirt/libvirt-sock \\
       -w /srv                                                        \\
       --net=host                                                     \\
       dockerhub.hi.inet/networkcloud/vagrant                         \\
       up

docker run                                                            \\
       --rm                                                           \\
       -v \${WORKSPACE}/iac/bootstrap-image/vagrant:/srv               \\
       -v /var/run/libvirt/libvirt-sock:/var/run/libvirt/libvirt-sock \\
       -w /srv                                                        \\
       --net=host                                                     \\
       dockerhub.hi.inet/networkcloud/vagrant                         \\
       ssh-config | grep HostName | awk '{print \$2}' | tr -d '\\r' > \${WORKSPACE}/iac/tests/onboarding-tests/testinfra/hng-vagrant-ip

docker run                                                            \\
       --rm                                                           \\
       -v \${WORKSPACE}/iac/bootstrap-image/vagrant:/srv               \\
       -v /var/run/libvirt/libvirt-sock:/var/run/libvirt/libvirt-sock \\
       -w /srv                                                        \\
       --net=host                                                     \\
       dockerhub.hi.inet/networkcloud/vagrant                         \\
       ssh-config | grep IdentityFile | awk '{print \$2}' | cut -f 3- -d '/' | tr -d '\\r' > \${WORKSPACE}/iac/bootstrap-image/vagrant/hng-vagrant-key-path

sudo cp \${WORKSPACE}/iac/bootstrap-image/vagrant/\$(cat \${WORKSPACE}/iac/bootstrap-image/vagrant/hng-vagrant-key-path) \${WORKSPACE}/iac/tests/onboarding-tests/testinfra/id_rsa
sudo cp \${WORKSPACE}/iac/bootstrap-image/vagrant/\$(cat \${WORKSPACE}/iac/bootstrap-image/vagrant/hng-vagrant-key-path) \${WORKSPACE}/iac/vnf-config/id_rsa 



#Test pre-config 
docker run                                                            \\
       --rm                                                           \\
       -v /var/run/libvirt/libvirt-sock:/var/run/libvirt/libvirt-sock \\
       -v \${WORKSPACE}/iac/tests/onboarding-tests/testinfra:/srv      \\
       -w /srv                                                        \\
       --net=host                                                     \\
       dockerhub.hi.inet/networkcloud/testinfra:3.2.0                 \\
       --ssh-config=/srv/ssh_config                                   \\
       --hosts="ssh://\$(cat \${WORKSPACE}/iac/tests/onboarding-tests/testinfra/hng-vagrant-ip)" \\
       /srv/unitary_test_preconfig.py

#Configure HNG

sed -i "s+hng_ip+\$(cat \${WORKSPACE}/iac/tests/onboarding-tests/testinfra/hng-vagrant-ip)+g" \${WORKSPACE}/iac/vnf-config/hng-inventory
sudo cp \${WORKSPACE}/iac/bootstrap-image/vagrant/\$(cat \${WORKSPACE}/iac/bootstrap-image/vagrant/hng-vagrant-key-path) \${WORKSPACE}/iac/vnf-config/id_rsa 

## Create hng config file

docker run                                                   \\
       --rm                                                  \\
       -v \${WORKSPACE}/iac/vnf-config/topology:/gen/topology \\
       -v \${WORKSPACE}/iac/vnf-config/data:/gen/data         \\
       -w /gen                                               \\
       dockerhub.hi.inet/networkcloud/hng-config-gen:5.0.1-1 \\
       data/hngv4.yml                                        \\
       -o topology/hngv4.txt

## Apply config to HNG

docker run                                 \\
       --rm                                \\
       -v /home/\${USER}/.aws/:/root/.aws/  \\
       -v \${WORKSPACE}/iac/vnf-config:/srv \\
       -w /srv                             \\
       --net=host                          \\
       dockerhub.hi.inet/networkcloud/hng-provisioner:5.0.1-5 playbook.yml -i hng-inventory



#Test post-config
docker run                                                                                     \\
       --rm                                                                                    \\
       -v \${WORKSPACE}/iac/tests/unit-tests/testinfra:/srv                                     \\
       -v \${WORKSPACE}/iac/tests/onboarding-tests/testinfra/id_rsa:/srv/id_rsa                 \\
       -v /var/run/libvirt/libvirt-sock:/var/run/libvirt/libvirt-sock                          \\
       -w /srv                                                                                 \\
       --net=host                                                                              \\
       dockerhub.hi.inet/networkcloud/testinfra:3.2.0                                          \\
       --ssh-config=/srv/ssh_config                                                            \\
       --hosts="ssh://\$(cat \${WORKSPACE}/iac/tests/onboarding-tests/testinfra/hng-vagrant-ip)" \\
       /srv/unitary_test_postconfig.py""")
		shell("""#Destroy HNG
docker run                                                            \\
       --rm                                                           \\
       -v \${WORKSPACE}/iac/bootstrap-image/vagrant:/srv               \\
       -v /var/run/libvirt/libvirt-sock:/var/run/libvirt/libvirt-sock \\
       -w /srv                                                        \\
       --net=host                                                     \\
       dockerhub.hi.inet/networkcloud/vagrant                         \\
       destroy -f""")	
	}
	publishers {
		wsCleanup {
			deleteDirectories(true)
		}
	}
}
