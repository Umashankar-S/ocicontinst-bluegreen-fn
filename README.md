# ocicontinst-bluegreen-fn

- This  project helps updates perform  Scaling , Update Container Images , Switch between Blue-Green OCI Conatiner Instance
 
 NOTE : Import point is  this function uses the  repo : https://github.com/Umashankar-S/ocicontinst-bluegreen  as base ,

https://github.com/Umashankar-S/ocicontinst-bluegreen  -> Deploys the OCI Container Instance as blue green deployment

- This project has the OCI function's related files : 
  - func.py
  - requirements.txt

######## Prerequisites

1. Required IAM Policies and Group


Allow dynamic-group <identity_domain_name>/<group-name> to manage function-family in compartment id <comp_ocid>

Allow dynamic-group <identity_domain_name>/<group-name> to manage virtual-network-family in compartment id <comp_ocid>


### Function related  policies


allow service FAAS to use virtual-network-family in compartment id <comp_ocid>

allow service FAAS to manage repos in compartment id <comp_ocid>

Allow dynamic-group <identity_domain_name>/<dynamic-group-name> to manage function-family in compartment id <comp_ocid>

Allow dynamic-group <identity_domain_name>/<dynamic-group-name> to use virtual-network-family in compartment id <comp_ocid>

Allow dynamic-group <identity_domain_name>/<dynamic-group-name> to manage orm-family in compartment id  <comp_ocid> 

Allow dynamic-group <identity_domain_name>/<dynamic-group-name> to use repos in compartment id  <comp_ocid>


### Policies to deploy/execute the function from a compute instance using Instance principal  ( if the OCI Config used to call function below policies should be granted to the user's group  inpace of dynamic group )

Allow dynamic-group <identity_domain_name>/<dynamic-group-name> to manage function-family in compartment id <comp_ocid>

Allow dynamic-group <identity_domain_name>/<dynamic-group-name> to manage orm-family in compartment id  <comp_ocid> 

Allow dynamic-group <identity_domain_name>/<dynamic-group-name> to manage compute-container-family in compartment id  <comp_ocid>

Allow dynamic-group <identity_domain_name>/<dynamic-group-name> to manage repos in compartment id  <comp_ocid>

Allow dynamic-group <identity_domain_name>/<dynamic-group-name> to use log-content in compartment id  <comp_ocid>

Allow dynamic-group <identity_domain_name>/<dynamic-group-name> to manage  load-balancers in compartment id <comp_ocid>




############ Deploy  the Function

1. Clone the repo to a local directory
   
    git clone https://github.com/Umashankar-S/ocicontinst-bluegreen-fn 
    
    
2. Follow the Function Quick start Guide :  https://docs.oracle.com/en-us/iaas/Content/Functions/Tasks/functionsquickstartguidestop.htm


3. After following Setup your tenancy  (Section A -  https://docs.oracle.com/en-us/iaas/Content/Functions/Tasks/functionsquickstartocicomputeinstance.htm

 -  B Create you application  (  https://docs.oracle.com/en-us/iaas/Content/Functions/Tasks/functionsquickstartocicomputeinstance.htm#functionsquickstartocicomputeinstance_topic_setup_Create_application )

  - D. Set up your OCI compute instance dev environment 


4.  Next is  Section  E - Create, deploy, and invoke your function [ Reference  https://docs.oracle.com/en-us/iaas/Content/Functions/Tasks/functionsquickstartocicomputeinstance.htm ]

-  fn init --runtime python ci_update 

   Here  ci_update is Application Name and as well function name  

-  Copy the  func.py and requirements.txt from the repo folder to  this function's folder  

   cp <local_repo_folder>/func.py ci_update/


   cp <local_repo_folder>/requirements.txt ci_update/


   Optionally  run compile to catch the errors in python code 

   cd ci_update 


   python -m py_compile func.py


-  fn -v deploy --app ci_update ci_update


- Please do enable logging for the function from OCI Console, helps in debugging invokation logs 

- Please have the Synchronous invocation timeout (in seconds) to 300 sec for the function



5. Functions Invoke 

Please follow one of the below example for either scaling , switching the active environment , updating container image

Here Stack OCID value is the  ORM Stack OCID for Blue Green OCI Container instance deployement as mentioned in NOTE ( in the beginning of this README)

- Example 1  :  Scale Blue Conatiner instance count 

echo -n '{"stack_id":"ocid1.ormstack.oc1......","operation":"scale","env":"blue","ci_count_blue":"3"}' |  fn invoke ci_update ci_update

- Example 2 :  Scale Green Conatiner instance count 

echo -n '{"stack_id":"ocid1.ormstack.oc1......","operation":"scale","env":"green","ci_count_green":"3"}' |  fn invoke ci_update ci_update

- Example 3 :  Switch  to Green as Active Environment

echo -n '{"stack_id":"ocid1.ormstack.oc1....","operation":"switch","env":"green","active_environment":"green"}' |  fn invoke ci_update ci_update

- Example 4 :  Update container images for Green Container Instance  ( Actually you can invoke the function during CI/CD pipeline to update the container instances using  Function Invoke endpoint  )

echo -n '{"stack_id":"ocid1.ormstack.oc1.,,","operation":"update_image","env":"green","ci_1_image_url_green":"iad.ocir.io/.../../app1:v3","ci_2_image_url_green":"iad.ocir.io/.../.../app2:v2"}' |  fn invoke ci_update ci_update



6. Wait for the  ORM job to be completed ( triggered by function ) and review the ORM Job log before actually testing the application URLs. 

   