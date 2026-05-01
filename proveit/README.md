# ProveIT 2026 

## ToC
* [docker-makefiles](../docker-makefiles) - directory containing configurations for AnyLog nodes 
* [anylog-scripts](anylog-scripts) - directory containing demo specific scripts used as part of the deployment.
These scripts can also be found under the [deployment-scripts repo](https://github.com/AnyLog-co/deployment-scripts/tree/proveit/proveit-scripts).
* [node-red](node-red) - [node-RED](http://45.33.62.114:1880/#flow) scripts used to demonstrate flow of data
* [blockchain](blockchain) - python3 scripts used to create unified namespace metadata 
* [query](query) - Sample python3 scripts to query the data 
  * [query_blockchain.py](query/query_blockchain.py) - query metadata 
  * [query_data.py](query/query_data.py) - the actual data


## Nodes

| Node           | AnyLog Type        | AnyLog IP      | Dynics IP      | Message Broker | REST  |
|:---------------|:------------------|:---------------|:---------------|:---------------|:------|
| anylog-master  | Master / Query    | 50.116.13.109  | 172.79.89.206  |                | 32049 |
| historian      | Operator          | 50.116.13.109  | 172.79.89.201  | 32160          | 32159 |
| Site1          | Operator          | 50.116.13.109  | 172.79.89.201  | 32150          | 32149 |
| Site2          | Operator          | 45.33.62.114   | 172.79.89.202  | 32150          | 32149 |
| Site3          | Operator          | 45.33.62.114   | 172.79.89.206  | 32160          | 32159 |

* node-RED http://45.33.62.114:1880/#flow/d036c805c711acdc
* Remote-GUI: http://50.116.13.109:3001/


## Sample REST calls

* [query_blockchain.py](query/query_blockchain.py) - query the metadata (blockchain)
* [query_data.py](query/query_data.py) - query the actual data and aggregations


## Deploy Network
1. Update configurations for the nodes
   * LEDGER_CONN 
   * Physical database connection
   * Partitioning - currently set to 1 day / keep 3
2. Deploy nodes
   * Master / Query - `make up ANYLOG_TYPE=anylog-master`
   * Operator: Enterprise C - `make up ANYLOG_TYPE=historian`
   * Operator: Site 1 - `make up ANYLOG_TYPE=site1`
   * Operator: Site 2 - `make up ANYLOG_TYPE=site2`
   * Operator: Site 3 - `make up ANYLOG_TYPE=site3`
3. Declare [unified namespace](#unified-namespace-hierarchy)
```shell
python3 enterprise_b.py [MASTER_CONN] --db-name bottle_factory
python3 enterprise_c.py [MASTER_CONN] --db-name manufacturing_historian
```

4. To publish data into AnyLog
    * **Enterprise B Topic**: _manufacturing_historian_
    * **Enterprise C Topic**: _kpi_ for KPIs and _processing_ for processing data (sensors)

### Background process: 
1. Start node(s) as we know
   * connect tcp, rest, message broker 
   * connect logical databases 
   * Declare blockchain policies
   * For operators: set partitions 
   * For operators: `run operator`
2. For operator node we then automatically run aggregation (keep 10 @ 1 minute intervals) and MQTT client
   * Bottle Factory - stores raw data 
     * [aggregation](anylog-scripts/bottle_factory_aggregation.al)
     * [MQTT client](anylog-scripts/bottle_factory_mqtt.al)
   * Historian - stores aggregation of data 
     * [aggregation](anylog-scripts/manufacturing_historian_aggregation.al) 
     * [MQTT client](anylog-scripts/manufacturing_historian_mqtt.al)
 
  

## Data Breakdown

Data is broken down is broken into 2 groups: 
* Enterprise C - data is stored in a timestamp / value tables, where each sensor is in its own table. 
* Enterprise B - data is stored in 2 tables - either KPI or processing (sensor) with multiple values per row.
In addition, each site is stored on a different operator. 

Having these 2 sets of configuration allows us to demonstrate: 
1. query data across nodes - "compare temperature on site 1 vs site 2 over the last 1 hour"
2. query data across different sensors - "show me the average value per sensor for device SIC-250-003 over the last 1 hour"


### Unified Namespace Hierarchy

**Enterprise B**: 
```tree
Enterprise: B
   -> namespace: Site1
      -> asset: LiquidProcessing (ID: 0ec546a171bd0ef12cfa735e3e4beedb)
         -> tank: Tank 1 (ID: 4e7719075307b52704db2a5218b79d3e) 
            -> lot: L01-0242
               -> kpi: oee
               -> kpi: performance
               -> kpi: quality
               -> kpi: availability
               -> sensor: state
               -> sensor: duration
               -> sensor: flowrate
               -> sensor: temperature
               -> sensor: weight 
   -> namespace: Site2
   -> namespace: Site3
```

**Enterprise C**:
```tree
Enterprise: C
   -> namespace; sub
      -> device: SIC-250-003
         -> sensor: PV_L_per_min
         -> sensor: SP_L_per_min
         -> sensor: STATUS
         -> sensor: START
      -> device: SIC-250-004
      -> device: SIC-250-002
      -> device: TI-250-001
      -> device: AIC-250-001
      ...
```
