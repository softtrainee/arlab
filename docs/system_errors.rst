====================
System Error Codes
====================


=============================  ====== =====================================================================
Name                           Code   Description
=============================  ====== =====================================================================
PychronCommErrorCode           001    could not communicate with pychron through {}. socket.error = {}
InvalidArgumentsErrorCode      002    invalid arguments: {} {}
ManagerUnavaliableErrorCode    003    manager unavaliable: {}
InvalidValveGroupErrorCode     004    Invalid valve group - {}
InvalidValveErrorCode          005    {} is not a registered valve name
DeviceConnectionErrorCode      006    device {} not connected
ValveActuationErrorCode        007    Valve {} failed to actuate {}
FuncCallErrorCode              008    func call problem: err= {} args= {}
InvalidCommandErrorCode        009    invalid command: {}
SecurityErrorCode              010    Not an approved ip address {}
PyScriptErrorCode              011    invalid pyscript {} does not exist
InvalidIPAddressErrorCode      012    {} is not a registered ip address
ValveSoftwareLockErrorCode     013    Valve {} is software locked
NoResponseErrorCode            014    no response from device
SystemLockErrorCode            015    Access restricted to {} ({}). You are {}
=============================  ====== =====================================================================

.. _pychron_comm_err:
.. describe:: PychronCommErrorCode       

.. _invalid_args_err:
.. describe:: InvalidArgumentsErrorCode  

.. _manager_unavailable_err:
.. describe:: ManagerUnavaliableErrorCode

.. _invalid_valve_grp_err:
.. describe:: InvalidValveGroupErrorCode 

.. _invalid_valve_err:
.. describe:: InvalidValveErrorCode    

.. _device_connection_err:
.. describe:: DeviceConnectionErrorCode  

.. _valve_actuation_err:
.. describe:: ValveActuationErrorCode    

.. _func_call_err:
.. describe:: FuncCallErrorCode          

.. _invalid_command_err:
.. describe:: InvalidCommandErrorCode    

.. _security_err:
.. describe:: SecurityErrorCode          

.. _pyscript_err:
.. describe:: PyScriptErrorCode          

.. _invalid_ip_address_err:
.. describe:: InvalidIPAddressErrorCode  

.. _valve_soft_lock_err:
.. describe:: ValveSoftwareLockErrorCode 

.. _no_response_err:
.. describe:: NoResponseErrorCode        

.. _system_lock_err:
.. describe:: SystemLockErrorCode        
