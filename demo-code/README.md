## Nodes

|                 Node                 | IP | Message Broker | REST  | 
|:------------------------------------:| :---: | :---: |:-----:|
|            Master / Query            | 50.116.13.109 | | 32049 | 
|  Operator I (Enterprise B - Site 1)  | 50.116.13.109 | 32150 | 32149 | 
|      Operator II (Enterprise C)      | 50.116.13.109 | 32160 | 32160 | 32159 |
| Operator III (Enterprise B - Site 2) | 45.33.62.114 | 32150 | 32149 | 
| Operator IV (Enterprise B - Site 3)  | 45.33.62.114 | 32160 | 32159 |


## Setting Up
1. Start Nodes - nodes are already configured 
2. Run mqtt client(s)
   * [Enterprise B](enterpriseb.al) - on Enterprise B nodes
   * [Enterprise C](enterprisec.al) - on Enterprise C node
3. Start MQTT flow(s) via Dynics (using node-RED for demo)
   * [Enterprise B](enterpise_b.json)
   * [Enterprise C](enterpise_c.json)

## Aggregations


## Sample REST calls
