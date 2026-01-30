import oci
import json,io
import logging
import sys
from fdk import response


logging.basicConfig(level=logging.INFO) 
logger = logging.getLogger(__name__)
## Resource Prinicipal

signer = oci.auth.signers.get_resource_principals_signer()
resource_manager_client = oci.resource_manager.ResourceManagerClient(config={},signer=signer)

### OCI Config file - For testing from VM
#config = oci.config.from_file(file_location='~/.oci/config',profile_name='DEFAULT') 
#oci.config.validate_config(config)
#resource_manager_client = oci.resource_manager.ResourceManagerClient(config)

# ### Instance Prinicpal - For testing from VM
# signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()
# resource_manager_client = oci.resource_manager.ResourceManagerClient(config={},signer=signer)

###########
####"Usage of this Script : 
    ####**********************************************************************************************************************
    ####  1st Argument :  stack_id
    ####  2nd Argument :  operation
    ####   operation -> scale , switch or update_image
    ####  3rd Argument :  env
    ####    env  -> green or blue
    ####   Further arguments will based on operation
    ####  operation -> scale 
    ####      ci_count_blue=n  or  ci_count_green=n 
    ####  operation -> switch 
    ####      active_environment=blue or  active_environment=green 
    ####  operation -> update_image 
    ####    ci_1_image_url_blue=image_path:ver ci_2_image_url_blue=image_path:ver 
    #### OR  ci_1_image_url_green=image_path:ver ci_2_image_url_green=image_path:ver  ")
    ####-------------------------------
    ####"Example 1 :
    ####-------------------------------
    #### { "stack_id":"stack_ocid","operation":"scale","env":"blue","ci_count_blue":"4"}  
    ####"Example 2 :
    ####-------------------------------
    ####" { "stack_id":"stack_ocid","operation":"scale","env":"green","active_environment":"green"}
    ####"Example 3 :
    ####-------------------------------
    ####" { "stack_id":"stack_ocid","operation":"update_image","env":"blue","ci_1_image_url_blue":"image_path:ver","ci_2_image_url_blue":"image_path:ver")
    ####**********************************************************************************************************************

def script_usage():
    print("*" * 60)
    print("Usage of this Script : ")
    print("-" * 30)
    print("1st Argument :  stack_id")
    print("2nd Argument :  operation")
    print("    operation:scale , switch or update_image")
    print("3rd Argument :  env")
    print("    env:green or env:blue")
    print("Further arguments will based on operation")
    print(" operation -> scale ")
    print(" ci_count_blue:n  or  ci_count_green:n  ")
    print(" operation -> switch ")
    print(" active_environment:blue or  active_environment:green  ")
    print(" operation -> update_image ")
    print(" ci_1_image_url_blue:\"image_path:ver\",\"ci_2_image_url_blue\":\"image_path:ver\" OR  \"ci_1_image_url_green\":image_path:ver\",\"ci_2_image_url_green\":\"image_path:ver\"  ")
    print("-" * 45)
    print("Example 1 :")
    print("-" * 30)
    print(" {\"stack_id\":\"stack_ocid\",\"operation\":\"scale\",\"env\":\"blue\",\"ci_count_blue\":\"3\" } ")
    print("Example 2 :")
    print("-" * 30)
    print(" {\"stack_id\":\"stack_ocid\",\"operation\":\"switch\",\"env\":\"green\",\"active_environment\":\"green\"} ")
    print("Example 3 :")
    print("-" * 30)
    print(" {\"stack_id\":\"stack_ocid\",\"operation\":\"update_image\",\"env\":\"green\",\"ci_1_image_url_green\":\"image_path:version\",\"ci_2_image_url_green\":\"image_path:version\"} " )
    print("*" * 60)



#def update_stack_and_apply(stack_id,operation,env,**options):
def update_stack_and_apply(**options):
    stack_id=options['stack_id']
    operation=options['operation']
    env=options['env']
    print(f"stack_id :  {stack_id}")
    print(f"operation : {operation}")
    print(f"env : {env}")
    for key, value in options.items():
        print(f"  {key}: {value}")
    get_stack_response = resource_manager_client.get_stack(
        stack_id=stack_id)
    stack_variables=get_stack_response.data.variables
    logger.info(f"Existing Stack Varables {stack_variables}")
    if not options:
        script_usage()
        logger.info(f"Missing Parameters")
        # sys.exit(1)
        return f"Invalidate Parameters" 
    if operation not in ['scale','switch','update_image']:
        script_usage()
        logger.info(f"Invalid operation parameters, should be scale or switch or update_image")
        return f"Invalid operation parameters, should be scale or switch or update_image"
        # sys.exit(1)


    if operation == "scale":
        ci_count_var=['ci_count_blue','ci_count_green']
        if any(item in ci_count_var for item in options):
         if env == "blue":
           print(f"{options['ci_count_blue']}")
           ci_count=options['ci_count_blue']
           ci_count_string = str(ci_count)   
           new_var={'ci_count_blue': ci_count_string}
         else:
           print(f"{options['ci_count_green']}")
           ci_count=options['ci_count_green']
           ci_count_string = str(ci_count)   
           new_var={'ci_count_green': ci_count_string}
        else:
         print("Invalid scale parameters")
         logger.info(f"Invalid scale parameters")
         script_usage()
         sys.exit(1)
         return f"Invalid scale parameters"

    if operation == "switch":
          if options['active_environment'] in ( 'green','blue'):
            print(f"{options['active_environment']}")
            existing_var=stack_variables['active_environment']
            if existing_var != options['active_environment']:
             active_env=options['active_environment']
             new_var={'active_environment': active_env}
            else:
             print(f"Existing Stack Var active_environment : {existing_var} = {options['active_environment']}")   
             print("No Stack Update required")
             logger.info(f"Existing Stack Var active_environment : {existing_var} = {options['active_environment']} ,No Stack Update required")
             return f"Existing Stack Var active_environment : {existing_var} = {options['active_environment']} ,No Stack Update required"
            #  sys.exit(0)
          else:
            print("Invalid switch parameters")
            script_usage()
            logger.info(f"Invalid switch parameters")
            # sys.exit(1)
            return f"Invalid switch parameters"

    if operation == "update_image":
          if len(options) < 2:
           script_usage()
           sys.exit(1)
           return 
          if env == "blue":
           print(f"{options['ci_1_image_url_blue']} , {options['ci_2_image_url_blue']}")
           ci1_image=options['ci_1_image_url_blue']
           ci2_image=options['ci_2_image_url_blue']
           new_var={'ci_1_image_url_blue': ci1_image,'ci_2_image_url_blue': ci2_image}
          else:
           print(f"{options['ci_1_image_url_green']} , {options['ci_2_image_url_green']}")
           ci1_image=options['ci_1_image_url_green']
           ci2_image=options['ci_2_image_url_green']
           new_var={'ci_1_image_url_green': ci1_image,'ci_2_image_url_green': ci2_image}
    
    # print("--------- get_stack_response ---------")
    # print (get_stack_response.data)
    

    print(f"Update variable of the stack with OCID {stack_id}")
    logger.info(f"Update variable of the stack with OCID {stack_id}")
    #logger.info(f"{new_var}")
    print(new_var)
    stack_variables.update(new_var)
    print("-" * 60)

    try:
         resource_manager_client.update_stack(
                 stack_id=stack_id,
                 update_stack_details=oci.resource_manager.models.UpdateStackDetails(
                     variables=stack_variables))

         resource_manager_client.create_job(
                 create_job_details=oci.resource_manager.models.CreateJobDetails(
                     stack_id=stack_id,
                     job_operation_details=oci.resource_manager.models.CreateApplyJobOperationDetails(
                         operation="APPLY",
                         execution_plan_strategy="AUTO_APPROVED")))
         print("Update Stack End")
         print(f"Updated stack and applied job with updated variable  {new_var}")
         logger.info(f"Updated stack and applied job with updated variable  {new_var}")
         return f"Updated stack and applied job with updated variable  {new_var}"
    except Exception as ex:
             print(f"Update Stack Failed: {ex}") 
             logger.info(f"Update Stack Failed: {ex}")
             return f"Update Stack Failed"         



def handler(ctx, data: io.BytesIO=None):
   
    # logging.basicConfig(level=logging.INFO) 
    # logger = logging.getLogger(__name__)
    body = json.loads(data.getvalue())
    # stack_id = body.get("stack_id")
    # operation = body.get("operation")
    # env = body.get("env")
    options = {} 
    for key, value in body.items():
        options[key] = value

    # logger.info("Stack Id : " + stack_id)
    # logger.info("operation : " + operation)
    # logger.info("env : " + env)

    #func_response = update_stack_and_apply(stack_id,operation,env,**options)
    func_response = update_stack_and_apply(**options)
    print("INFO: ", func_response, flush=True)
    logger.info(f"func_response: {func_response}")
    return response.Response(
        ctx,
        response_data=func_response,
        headers={"Content-Type": "application/json"}
    )

      



# if __name__ == "__main__":
#     if len(sys.argv) < 4:
#         print("Usage: python oci_container_scale.py <ORM_STACK_ID> <no_of_Cont_Inst_to_scale>")
#         sys.exit(1)
#     print(len(sys.argv))
#     print(sys.argv)
#     options = {} 
#     for arg in sys.argv[4:]:
#         if "=" not in arg:
#             print(f"Invalid option: {arg} (expected key=value)")
#             sys.exit(1)
#         k, v = arg.split("=", 1)
#         options[k] = v
#     print(f"update_stack_and_apply({sys.argv[1]}, {sys.argv[2]},{sys.argv[3]},{options}")
#     update_stack_and_apply(sys.argv[1], sys.argv[2],sys.argv[3],**options)
    