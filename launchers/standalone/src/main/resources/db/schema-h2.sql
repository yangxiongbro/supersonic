-- chat tables
CREATE TABLE IF NOT EXISTS `s2_chat_context`
(
    `chat_id`        BIGINT NOT NULL , -- context chat id
    `modified_at`    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP , -- row modify time
    `query_user`           varchar(64) DEFAULT NULL , -- row modify user
    `query_text`     LONGVARCHAR DEFAULT NULL , -- query text
    `semantic_parse` LONGVARCHAR DEFAULT NULL , -- parse data
    `ext_data`       LONGVARCHAR DEFAULT NULL , -- extend data
    PRIMARY KEY (`chat_id`)
    );

CREATE TABLE IF NOT EXISTS `s2_chat`
(
    `chat_id`       BIGINT auto_increment ,-- AUTO_INCREMENT,
    `agent_id`       INT DEFAULT NULL,
    `chat_name`     varchar(100) DEFAULT NULL,
    `create_time`   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP ,
    `last_time`     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP ,
    `creator`       varchar(30)  DEFAULT NULL,
    `last_question` varchar(200) DEFAULT NULL,
    `is_delete`     INT DEFAULT '0' COMMENT 'is deleted',
    `is_top`        INT DEFAULT '0' COMMENT 'is top',
    PRIMARY KEY (`chat_id`)
    ) ;


CREATE TABLE IF NOT EXISTS `s2_chat_query`
(
    `question_id`             BIGINT  NOT NULL AUTO_INCREMENT,
    `agent_id`             INT  NULL,
    `create_time`       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `query_text`          mediumtext,
    `user_name`         varchar(150)  DEFAULT NULL COMMENT '',
    `query_state`             int DEFAULT NULL,
    `chat_id`           BIGINT NOT NULL , -- context chat id
    `query_result` mediumtext NOT NULL ,
    `score`             int DEFAULT '0',
    `feedback`          varchar(1024) DEFAULT '',
    `similar_queries`          varchar(1024) DEFAULT '',
    `parse_time_cost` varchar(1024) DEFAULT '',
    PRIMARY KEY (`question_id`)
);

CREATE TABLE IF NOT EXISTS `s2_chat_parse`
(
    `question_id`       BIGINT  NOT NULL,
    `chat_id`           INT NOT NULL ,
    `parse_id`          INT NOT NULL ,
    `create_time`       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `query_text`          varchar(500),
    `user_name`         varchar(150)  DEFAULT NULL COMMENT '',
    `parse_info` mediumtext NOT NULL ,
    `is_candidate` INT DEFAULT 1 COMMENT '1是candidate,0是selected'
);

CREATE TABLE IF NOT EXISTS `s2_chat_statistics`
(
    `question_id`             BIGINT  NOT NULL,
    `chat_id`           BIGINT NOT NULL ,
    `user_name`         varchar(150)  DEFAULT NULL COMMENT '',
    `query_text`          varchar(200),
    `interface_name`         varchar(100)  DEFAULT NULL COMMENT '',
    `cost` INT NOT NULL ,
    `type` INT NOT NULL ,
    `create_time`       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS `s2_chat_config` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `model_id` INT DEFAULT NULL ,
    `chat_detail_config` varchar(655) ,
    `chat_agg_config` varchar(655)    ,
    `recommended_questions`  varchar(1500)    ,
    `created_at` TIMESTAMP  NOT NULL   ,
    `updated_at` TIMESTAMP  NOT NULL   ,
    `created_by` varchar(100) NOT NULL   ,
    `updated_by` varchar(100) NOT NULL   ,
    `status` INT NOT NULL  DEFAULT '0' , -- domain extension information status : 0 is normal, 1 is off the shelf, 2 is deleted
    `llm_examples` TEXT,
    PRIMARY KEY (`id`)
    ) ;
COMMENT ON TABLE s2_chat_config IS 'chat config information table ';


CREATE TABLE IF NOT EXISTS `s2_chat_memory` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `question` varchar(655)    ,
    `query_id`  BIGINT    ,
    `agent_id`  INT    ,
    `db_schema`  TEXT    ,
    `s2_sql` TEXT   ,
    `side_info` TEXT    ,
    `status` varchar(10)   ,
    `llm_review` varchar(10)   ,
    `llm_comment`   TEXT,
    `human_review` varchar(10) ,
    `human_comment` TEXT    ,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP  ,
    `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP ,
    `created_by` varchar(100)  ,
    `updated_by` varchar(100)  ,
    PRIMARY KEY (`id`)
    ) ;
COMMENT ON TABLE s2_chat_memory IS 'chat memory table ';

CREATE TABLE IF NOT EXISTS `s2_chat_model`
(
    id          int AUTO_INCREMENT,
    name        varchar(100)  null,
    description varchar(500) null,
   `config` varchar(500) NOT  NULL ,
   `created_at` TIMESTAMP NOT  NULL ,
   `created_by` varchar(100) NOT  NULL ,
   `updated_at` TIMESTAMP NOT  NULL ,
   `updated_by` varchar(100) NOT  NULL,
   `admin` varchar(500) NOT  NULL,
   `viewer` varchar(500) DEFAULT  NULL,
    PRIMARY KEY (`id`)
); COMMENT ON TABLE s2_chat_model IS 'chat model table';

create table IF NOT EXISTS s2_user
(
    id       INT AUTO_INCREMENT,
    name     varchar(100) not null,
    display_name varchar(100) null,
    password varchar(256) null,
    salt varchar(256)  NULL,
    email varchar(100) null,
    is_admin INT null,
    PRIMARY KEY (`id`)
);
COMMENT ON TABLE s2_user IS 'user information table';

-- semantic tables

CREATE TABLE IF NOT EXISTS `s2_domain` (
    `id` INT NOT NULL AUTO_INCREMENT  ,
    `name` varchar(255) DEFAULT NULL  , -- domain name
    `biz_name` varchar(255) DEFAULT NULL  , -- internal name
    `parent_id` INT DEFAULT '0'  , -- parent domain ID
    `status` INT NOT NULL  ,
    `created_at` TIMESTAMP DEFAULT NULL  ,
    `created_by` varchar(100) DEFAULT NULL  ,
    `updated_at` TIMESTAMP DEFAULT NULL  ,
    `updated_by` varchar(100) DEFAULT NULL  ,
    `admin` varchar(3000) DEFAULT NULL  , -- domain administrator
    `admin_org` varchar(3000) DEFAULT NULL  , -- domain administrators organization
    `is_open` TINYINT DEFAULT NULL  , -- whether the domain is public
    `viewer` varchar(3000) DEFAULT NULL  , -- domain available users
    `view_org` varchar(3000) DEFAULT NULL  , -- domain available organization
    PRIMARY KEY (`id`)
    );
COMMENT ON TABLE s2_domain IS 'domain basic information';

CREATE TABLE IF NOT EXISTS `s2_model` (
    `id` INT NOT NULL AUTO_INCREMENT  ,
    `name` varchar(255) DEFAULT NULL  , -- domain name
    `biz_name` varchar(255) DEFAULT NULL  , -- internal name
    `domain_id` INT DEFAULT '0'  , -- parent domain ID
    `tag_object_id` INT DEFAULT '0'  ,
    `alias` varchar(255) DEFAULT NULL  , -- internal name
    `status` INT DEFAULT NULL,
    `description` varchar(500) DEFAULT  NULL ,
    `created_at` TIMESTAMP DEFAULT NULL  ,
    `created_by` varchar(100) DEFAULT NULL  ,
    `updated_at` TIMESTAMP DEFAULT NULL  ,
    `updated_by` varchar(100) DEFAULT NULL  ,
    `admin` varchar(3000) DEFAULT NULL  , -- domain administrator
    `admin_org` varchar(3000) DEFAULT NULL  , -- domain administrators organization
    `is_open` TINYINT DEFAULT NULL  , -- whether the domain is public
    `viewer` varchar(3000) DEFAULT NULL  , -- domain available users
    `view_org` varchar(3000) DEFAULT NULL  , -- domain available organization
    `entity` varchar(500) DEFAULT NULL  , -- domain entity info
    `drill_down_dimensions` TEXT DEFAULT NULL  , -- drill down dimensions info
    `database_id` INT NOT  NULL ,
    `model_detail` LONGVARCHAR NOT  NULL ,
    `depends` varchar(500) DEFAULT NULL ,
    `source_type` varchar(128) DEFAULT NULL ,
    `filter_sql` varchar(1000) DEFAULT NULL ,
    `ext` varchar(1000) DEFAULT NULL,
    PRIMARY KEY (`id`)
    );
COMMENT ON TABLE s2_model IS 'model information';


CREATE TABLE IF NOT EXISTS `s2_database` (
   `id` INT NOT NULL AUTO_INCREMENT,
   `name` varchar(255) NOT  NULL ,
   `description` varchar(500) DEFAULT  NULL ,
   `version` varchar(64) DEFAULT  NULL ,
   `type` varchar(20) NOT  NULL , -- type: mysql,clickhouse,tdw
   `config` varchar(655) NOT  NULL ,
   `created_at` TIMESTAMP NOT  NULL ,
   `created_by` varchar(100) NOT  NULL ,
   `updated_at` TIMESTAMP NOT  NULL ,
   `updated_by` varchar(100) NOT  NULL,
   `admin` varchar(500) NOT  NULL,
   `viewer` varchar(500) DEFAULT  NULL,
   PRIMARY KEY (`id`)
);
COMMENT ON TABLE s2_database IS 'database instance table';

create table IF NOT EXISTS s2_auth_groups
(
    group_id INT,
    config varchar(2048),
    PRIMARY KEY (`group_id`)
);

CREATE TABLE IF NOT EXISTS `s2_metric` (
    `id` INT NOT NULL  AUTO_INCREMENT,
    `model_id` INT  NOT NULL ,
    `name` varchar(255)  NOT NULL ,
    `biz_name` varchar(255)  NOT NULL ,
    `description` varchar(500) DEFAULT NULL ,
    `status` INT  NOT NULL ,
    `sensitive_level` INT NOT NULL ,
    `type` varchar(50)  NOT NULL , -- ATOMIC, DERIVED
    `type_params` LONGVARCHAR DEFAULT NULL  ,
    `created_at` TIMESTAMP NOT NULL ,
    `created_by` varchar(100) NOT NULL ,
    `updated_at` TIMESTAMP NOT NULL ,
    `updated_by` varchar(100) NOT NULL ,
    `data_format_type` varchar(50) DEFAULT NULL ,
    `data_format` varchar(500) DEFAULT NULL,
    `alias` varchar(500) DEFAULT NULL,
    `classifications` varchar(500) DEFAULT NULL,
    `relate_dimensions` varchar(500) DEFAULT NULL,
    `ext` LONGVARCHAR DEFAULT NULL  ,
    `define_type` varchar(50)  NOT NULL, -- MEASURE, FIELD, METRIC
    `is_publish` INT,
    PRIMARY KEY (`id`)
    );
COMMENT ON TABLE s2_metric IS 'metric information table';


CREATE TABLE IF NOT EXISTS `s2_dimension` (
  `id` INT NOT NULL  AUTO_INCREMENT ,
  `model_id` INT NOT NULL ,
  `name` varchar(255) NOT NULL ,
    `biz_name` varchar(255)  NOT NULL ,
    `description` varchar(500) NOT NULL ,
    `status` INT NOT NULL , -- status, 0 is off the shelf, 1 is normal
    `sensitive_level` INT DEFAULT NULL ,
    `data_type` varchar(50)  DEFAULT NULL , -- type date,array,varchar
    `type` varchar(50)  NOT NULL , -- type categorical,time
    `type_params` LONGVARCHAR  DEFAULT NULL ,
    `expr` LONGVARCHAR NOT NULL , -- expression
    `created_at` TIMESTAMP  NOT NULL ,
    `created_by` varchar(100)  NOT NULL ,
    `updated_at` TIMESTAMP  NOT NULL ,
    `updated_by` varchar(100)  NOT NULL ,
    `semantic_type` varchar(20)  NOT NULL,  -- semantic type: DATE, ID, CATEGORY
    `alias` varchar(500) DEFAULT NULL,
    `default_values` varchar(500) DEFAULT NULL,
    `dim_value_maps` varchar(500) DEFAULT NULL,
    `is_tag` INT DEFAULT NULL,
    `ext` varchar(1000) DEFAULT NULL,
    PRIMARY KEY (`id`)
    );
COMMENT ON TABLE s2_dimension IS 'dimension information table';

CREATE TABLE IF NOT EXISTS s2_model_rela
(
    id             BIGINT AUTO_INCREMENT,
    domain_id       BIGINT,
    from_model_id    BIGINT,
    to_model_id      BIGINT,
    join_type       VARCHAR(255),
    join_condition  VARCHAR(255),
    PRIMARY KEY (`id`)
);

create table IF NOT EXISTS `s2_canvas` (
    id         INT auto_increment,
    domain_id  INT       null,
    type       varchar(20)  null comment 'model、dimension、metric',
    config     LONGVARCHAR   null comment 'config detail',
    created_at TIMESTAMP     null,
    created_by varchar(100) null,
    updated_at TIMESTAMP     null,
    updated_by varchar(100) not null,
    PRIMARY KEY (`id`)
);
COMMENT ON TABLE s2_canvas IS 'canvas table';


CREATE TABLE IF NOT EXISTS `s2_query_stat_info` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `trace_id` varchar(200) DEFAULT NULL, -- query unique identifier
  `model_id` INT DEFAULT NULL,
  `data_set_id` INT DEFAULT NULL,
  `query_user`    varchar(200) DEFAULT NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ,
  `query_type` varchar(200) DEFAULT NULL, -- the corresponding scene
  `query_type_back` INT DEFAULT '0' , -- query type, 0-normal query, 1-pre-refresh type
  `query_sql_cmd`LONGVARCHAR , -- sql type request parameter
  `sql_cmd_md5` varchar(200) DEFAULT NULL, -- sql type request parameter md5
  `query_struct_cmd`LONGVARCHAR , -- struct type request parameter
  `struct_cmd_md5` varchar(200) DEFAULT NULL, -- struct type request parameter md5值
  `query_sql` LONGVARCHAR ,
  `sql_md5` varchar(200) DEFAULT NULL, -- sql md5
  `query_engine` varchar(20) DEFAULT NULL,
  `elapsed_ms` bigINT DEFAULT NULL,
  `query_state` varchar(20) DEFAULT NULL,
  `native_query` INT DEFAULT NULL, -- 1-detail query, 0-aggregation query
  `start_date` varchar(50) DEFAULT NULL,
  `end_date` varchar(50) DEFAULT NULL,
  `dimensions`LONGVARCHAR , -- dimensions involved in sql
  `metrics`LONGVARCHAR , -- metric  involved in sql
  `select_cols`LONGVARCHAR ,
  `agg_cols`LONGVARCHAR ,
  `filter_cols`LONGVARCHAR ,
  `group_by_cols`LONGVARCHAR ,
  `order_by_cols`LONGVARCHAR ,
  `use_result_cache` TINYINT DEFAULT '-1' , -- whether to hit the result cache
  `use_sql_cache` TINYINT DEFAULT '-1' , -- whether to hit the sql cache
  `sql_cache_key`LONGVARCHAR , -- sql cache key
  `result_cache_key`LONGVARCHAR , -- result cache key
  `query_opt_mode` varchar(50) DEFAULT NULL ,
  PRIMARY KEY (`id`)
) ;
COMMENT ON TABLE s2_query_stat_info IS 'query statistics table';

CREATE TABLE IF NOT EXISTS `s2_available_date_info` (
    `id` INT NOT NULL  AUTO_INCREMENT ,
    `item_id` INT NOT NULL ,
    `type`    varchar(255) NOT NULL ,
    `date_format` varchar(64)  NOT NULL ,
    `start_date`  varchar(64) ,
    `end_date`  varchar(64) ,
    `unavailable_date` LONGVARCHAR  DEFAULT NULL ,
    `created_at` TIMESTAMP  NOT NULL ,
    `created_by` varchar(100)  NOT NULL ,
    `updated_at` TIMESTAMP  NOT NULL ,
    `updated_by` varchar(100)  NOT NULL ,
    `date_period` varchar(100)  DEFAULT NULL ,
    `status` INT  DEFAULT '0', -- 1-in use  0 is normal, 1 is off the shelf, 2 is deleted
    PRIMARY KEY (`id`)
    );
COMMENT ON TABLE s2_dimension IS 'dimension information table';


CREATE TABLE IF NOT EXISTS `s2_plugin`
(
    `id`         INT AUTO_INCREMENT,
    `type`      varchar(50)   NULL,
    `data_set`     varchar(100)  NULL,
    `pattern`    varchar(500)  NULL,
    `parse_mode` varchar(100)  NULL,
    `parse_mode_config` LONGVARCHAR  NULL,
    `name`       varchar(100)  NULL,
    `created_at` TIMESTAMP   NULL,
    `created_by` varchar(100) null,
    `updated_at` TIMESTAMP    NULL,
    `updated_by` varchar(100) NULL,
    `config`     LONGVARCHAR  NULL,
    `comment`     LONGVARCHAR  NULL,
    PRIMARY KEY (`id`)
); COMMENT ON TABLE s2_plugin IS 'plugin information table';

CREATE TABLE IF NOT EXISTS s2_agent
(
    id          int AUTO_INCREMENT,
    name        varchar(100)  null,
    description varchar(500) null,
    status       int null,
    examples    varchar(500) null,
    tool_config varchar(2000)  null,
    llm_config varchar(2000)  null,
    chat_model_config varchar(6000) null,
    visual_config varchar(2000)  null,
    created_by  varchar(100) null,
    created_at  TIMESTAMP  null,
    updated_by  varchar(100) null,
    updated_at  TIMESTAMP null,
    enable_search int null,
    enable_feedback int null,
    `admin` varchar(3000) DEFAULT NULL  , -- administrator
    `admin_org` varchar(3000) DEFAULT NULL  , -- administrators organization
    `is_open` TINYINT DEFAULT NULL  , -- whether the public
    `viewer` varchar(3000) DEFAULT NULL  , -- available users
    `view_org` varchar(3000) DEFAULT NULL  , -- available organization
    PRIMARY KEY (`id`)
); COMMENT ON TABLE s2_agent IS 'agent information table';

CREATE TABLE IF NOT EXISTS `s2_dictionary_conf` (
   `id` INT NOT NULL AUTO_INCREMENT,
   `description` varchar(255) ,
   `type` varchar(255)  NOT NULL ,
   `item_id` INT  NOT NULL , -- task Request Parameters md5
   `config` LONGVARCHAR  , -- remark related information
   `status` varchar(255) NOT NULL , -- the final status of the task
   `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP  ,
   `created_by` varchar(100) NOT NULL ,
   PRIMARY KEY (`id`)
);
COMMENT ON TABLE s2_dictionary_conf IS 'dictionary conf information table';

CREATE TABLE IF NOT EXISTS `s2_dictionary_task` (
   `id` INT NOT NULL AUTO_INCREMENT,
   `name` varchar(255) NOT NULL , -- task name
   `description` varchar(255) ,
   `type` varchar(255)  NOT NULL ,
   `item_id` INT  NOT NULL , -- task Request Parameters md5
   `config` LONGVARCHAR  , -- remark related information
   `status` varchar(255) NOT NULL , -- the final status of the task
   `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP  ,
   `created_by` varchar(100) NOT NULL ,
   `elapsed_ms` bigINT DEFAULT NULL , -- the task takes time in milliseconds
   PRIMARY KEY (`id`)
);
COMMENT ON TABLE s2_dictionary_task IS 'dictionary task information table';

CREATE TABLE IF NOT EXISTS s2_system_config
(
    id  INT PRIMARY KEY AUTO_INCREMENT,
    admin varchar(500),
    parameters text null
);

CREATE TABLE IF NOT EXISTS `s2_collect` (
    `id` bigint NOT NULL AUTO_INCREMENT,
    `type` varchar(20) NOT NULL,
    `username` varchar(20) NOT NULL,
    `collect_id` bigint NOT NULL,
    `create_time` TIMESTAMP,
    `update_time` TIMESTAMP,
    PRIMARY KEY (`id`)
);

CREATE TABLE IF NOT EXISTS `s2_metric_query_default_config` (
       `id` bigint NOT NULL AUTO_INCREMENT,
       `metric_id` bigint ,
       `user_name` varchar(255) NOT NULL,
       `default_config` varchar(1000) NOT NULL,
       `created_at` TIMESTAMP null,
       `updated_at` TIMESTAMP null,
       `created_by` varchar(100) null,
       `updated_by` varchar(100) not null,
       PRIMARY KEY (`id`)
);

CREATE TABLE IF NOT EXISTS `s2_app` (
    id          bigint AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(255),
    description VARCHAR(255),
    status      INT,
    config      TEXT,
    end_date    TIMESTAMP,
    qps         INT,
    app_secret  VARCHAR(255),
    owner       VARCHAR(255),
    created_at  TIMESTAMP,
    created_by  VARCHAR(255),
    updated_at  TIMESTAMP,
    updated_by  VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS `s2_data_set` (
    id          BIGINT AUTO_INCREMENT PRIMARY KEY,
    domain_id   BIGINT,
    `name`      VARCHAR(255),
    biz_name    VARCHAR(255),
    description VARCHAR(255),
    status      INT,
    alias       VARCHAR(255),
    data_set_detail TEXT,
    created_at  TIMESTAMP,
    created_by  VARCHAR(255),
    updated_at  TIMESTAMP,
    updated_by  VARCHAR(255),
    query_config VARCHAR(3000),
    `admin` varchar(3000) DEFAULT NULL,
    `admin_org` varchar(3000) DEFAULT NULL,
    `query_type` varchar(100) DEFAULT NULL
);

CREATE TABLE IF NOT EXISTS `s2_tag` (
    `id` INT NOT NULL  AUTO_INCREMENT,
    `item_id` INT  NOT NULL ,
    `type` varchar(50)  NOT NULL , -- METRIC DIMENSION
    `created_at` TIMESTAMP NOT NULL ,
    `created_by` varchar(100) NOT NULL ,
    `updated_at` TIMESTAMP DEFAULT NULL ,
    `updated_by` varchar(100) DEFAULT NULL ,
    PRIMARY KEY (`id`)
    );
COMMENT ON TABLE s2_tag IS 'tag information';

CREATE TABLE IF NOT EXISTS `s2_tag_object` (
    `id` INT NOT NULL  AUTO_INCREMENT,
    `domain_id` INT  NOT NULL ,
    `name` varchar(255)  NOT NULL ,
    `biz_name` varchar(255)  NOT NULL ,
    `description` varchar(500) DEFAULT NULL ,
    `status` INT  NOT NULL DEFAULT '1' ,
    `sensitive_level` INT NOT NULL DEFAULT '1' ,
    `created_at` TIMESTAMP NOT NULL ,
    `created_by` varchar(100) NOT NULL ,
    `updated_at` TIMESTAMP DEFAULT NULL ,
    `updated_by` varchar(100) DEFAULT NULL ,
    `ext` LONGVARCHAR DEFAULT NULL  ,
    PRIMARY KEY (`id`)
    );
COMMENT ON TABLE s2_tag IS 'tag object information';

CREATE TABLE IF NOT EXISTS `s2_query_rule` (
    `id` INT NOT NULL  AUTO_INCREMENT,
    `data_set_id` INT ,
    `priority` INT  NOT NULL DEFAULT '1' ,
    `rule_type` varchar(255)  NOT NULL ,
    `name` varchar(255)  NOT NULL ,
    `biz_name` varchar(255)  NOT NULL ,
    `description` varchar(500) DEFAULT NULL ,
    `rule` LONGVARCHAR DEFAULT NULL  ,
    `action` LONGVARCHAR DEFAULT NULL  ,
    `status` INT  NOT NULL DEFAULT '1' ,
    `created_at` TIMESTAMP NOT NULL ,
    `created_by` varchar(100) NOT NULL ,
    `updated_at` TIMESTAMP DEFAULT NULL ,
    `updated_by` varchar(100) DEFAULT NULL ,
    `ext` LONGVARCHAR DEFAULT NULL  ,
    PRIMARY KEY (`id`)
    );
COMMENT ON TABLE s2_query_rule IS 'tag query rule table';

CREATE TABLE IF NOT EXISTS `s2_term` (
    `id` INT NOT NULL  AUTO_INCREMENT,
    `domain_id` INT ,
    `name` varchar(255)  NOT NULL ,
    `description` varchar(500) DEFAULT NULL ,
    `alias` varchar(1000)  NOT NULL ,
    `related_metrics` varchar(1000)  DEFAULT NULL ,
    `related_dimensions` varchar(1000)  DEFAULT NULL,
    `created_at` TIMESTAMP NOT NULL ,
    `created_by` varchar(100) NOT NULL ,
    `updated_at` TIMESTAMP DEFAULT NULL ,
    `updated_by` varchar(100) DEFAULT NULL ,
    PRIMARY KEY (`id`)
    );
COMMENT ON TABLE s2_term IS 'term info';

CREATE TABLE IF NOT EXISTS `s2_user_token` (
   `id` INT NOT NULL AUTO_INCREMENT,
   `name` VARCHAR(255) NOT NULL,
    `user_name` VARCHAR(255)  NOT NULL,
    `expire_time` INT NOT NULL,
    `token` text NOT NULL,
    `salt` VARCHAR(255)  default NULL,
    `create_time` DATETIME NOT NULL,
    `create_by` VARCHAR(255) NOT NULL,
    `update_time` DATETIME default NULL,
    `update_by` VARCHAR(255) NOT NULL,
    `expire_date_time` DATETIME NOT NULL,
    PRIMARY KEY (`id`)
    );
COMMENT ON TABLE s2_user_token IS 'user token info';
