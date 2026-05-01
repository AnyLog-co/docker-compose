#-----------------------------------------------------------------------------------------------------------------------
# The following file is intended as a placeholder for user implemented code. The file is automatically called by master,
# operator, publisher, query or single_node (operator / publisher) files. If not is written then nothing runs.
#
# Sample commands could include things like;
#   * complicated MQTT calls
#   * Kafka requests
#   * non-standard schedule processes, such as recording disk usage and automated queries
#
# Documentation: https://github.com/AnyLog-co/documentation
#-----------------------------------------------------------------------------------------------------------------------
# process !local_scripts/deployment_scripts/local_script.al

on error ignore

if !company_name == "Bottle Factory" then
do process !anylog_path/deployment-scripts/proveit-scripts/bottle_factory_aggregation.al
do process !anylog_path/deployment-scripts/proveit-scripts/bottle_factory_mqtt.al

if !company_name == "Manufacturing Historian" then
do process !anylog_path/deployment-scripts/proveit-scripts/manufacturing_historian_aggregation.al
do process !anylog_path/deployment-scripts/proveit-scripts/manufacturing_historian_mqtt.al

end script