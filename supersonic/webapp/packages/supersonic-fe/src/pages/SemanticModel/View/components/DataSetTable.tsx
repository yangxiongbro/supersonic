import type { ActionType, ProColumns } from '@ant-design/pro-components';
import { ProTable } from '@ant-design/pro-components';
import { message, Button, Space, Popconfirm, Upload, Modal, Form, Select } from 'antd';
import React, { useRef, useState, useEffect } from 'react';
import { StatusEnum } from '../../enum';
import { useModel } from '@umijs/max';
import { deleteView, updateView, getDataSetList, getAllModelByDomainId, getDatabaseList } from '../../service';
import ViewCreateFormModal from './ViewCreateFormModal';
import moment from 'moment';
import styles from '../../components/style.less';
import { ISemantic } from '../../data';
import { ColumnsConfig } from '../../components/TableColumnRender';
import ViewSearchFormModal from './ViewSearchFormModal';
import { toDatasetEditPage } from '@/pages/SemanticModel/utils';
import { InboxOutlined } from '@ant-design/icons';
import request from 'umi-request';
import { isArrayOfValues } from '@/utils/utils';

const { Dragger } = Upload;

type Props = {
  // dataSetList: ISemantic.IDatasetItem[];
  disabledEdit?: boolean;
};

interface DatabaseItem {
  id: number;
  name: string;
  description: string | null;
  type: string;
  host: string;
  port: string;
  hasEditPermission: boolean;
}

const DataSetTable: React.FC<Props> = ({ disabledEdit = false }) => {
  const domainModel = useModel('SemanticModel.domainData');
  const { selectDomainId } = domainModel;

  const [viewItem, setViewItem] = useState<ISemantic.IDatasetItem>();
  const [saveLoading, setSaveLoading] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(false);
  const [createDataSourceModalOpen, setCreateDataSourceModalOpen] = useState(false);
  const [searchModalOpen, setSearchModalOpen] = useState(false);
  const [modelList, setModelList] = useState<ISemantic.IModelItem[]>([]);
  const actionRef = useRef<ActionType>();
  const [editFormStep, setEditFormStep] = useState<number>(0);
  const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([]);
  const [exportLoading, setExportLoading] = useState<boolean>(false);

  // 导入模态框相关状态
  const [importModalVisible, setImportModalVisible] = useState<boolean>(false);
  const [importForm] = Form.useForm();
  const [databaseList, setDatabaseList] = useState<DatabaseItem[]>([]);
  const [uploading, setUploading] = useState<boolean>(false);
  const [fileList, setFileList] = useState<any[]>([]);
  const [importLoading, setImportLoading] = useState<boolean>(false);

  const updateViewStatus = async (modelData: ISemantic.IDatasetItem) => {
    setSaveLoading(true);
    const { code, msg } = await updateView({
      ...modelData,
    });
    setSaveLoading(false);
    if (code === 200) {
      queryDataSetList();
    } else {
      message.error(msg);
    }
  };

  const [viewList, setViewList] = useState<ISemantic.IDatasetItem[]>();

  useEffect(() => {
    if (!selectDomainId) {
      return;
    }
    queryDataSetList();
    queryDomainAllModel();
    // 当领域切换时，清空已选择的行
    setSelectedRowKeys([]);
  }, [selectDomainId]);

  const queryDataSetList = async () => {
    setLoading(true);
    const { code, data, msg } = await getDataSetList(selectDomainId as number);
    setLoading(false);
    if (code === 200) {
      setViewList(data);
      // 数据重新加载后，清空已选择的行
      setSelectedRowKeys([]);
    } else {
      message.error(msg);
    }
  };

  const queryDomainAllModel = async () => {
    const { code, data, msg } = await getAllModelByDomainId(selectDomainId as number);
    if (code === 200) {
      setModelList(data);
    } else {
      message.error(msg);
    }
  };

  /**
   * 获取数据库列表
   */
  const fetchDatabaseList = async () => {
    try {
      setUploading(true);
      const result = await getDatabaseList();
      setUploading(false);
      if (result.code === 200) {
        setDatabaseList(result.data || []);
      } else {
        message.error('获取数据库列表失败');
      }
    } catch (error) {
      setUploading(false);
      console.error('获取数据库列表失败:', error);
      message.error('获取数据库列表失败');
    }
  };

  /**
   * 处理数据集导出
   */
  const handleExportDataSet = async () => {
    if (!selectDomainId) {
      message.warning('请先选择领域');
      return;
    }

    setExportLoading(true);

    try {
      // 构建请求参数
      let requestUrl = `/api/sync_data/transmission/export/file?domainId=${selectDomainId}`;

      // 如果有选中的数据集，添加到参数中
      if (selectedRowKeys.length > 0) {
        selectedRowKeys.forEach((id) => {
          requestUrl += `&dataSetIdList=${id}`;
        });
      }

      // 发送请求，获取文件流
      const response = await request(requestUrl, {
        method: 'GET',
        responseType: 'blob',
        getResponse: true,
      });

      // 获取文件名
      const contentDisposition = response.response.headers.get('content-disposition');
      let filename = `数据集导出_${selectDomainId}_${moment().format('YYYY-MM-DD')}.json`;
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename=(.*)/);
        if (filenameMatch && filenameMatch[1]) {
          filename = decodeURIComponent(filenameMatch[1].replace(/"/g, ''));
        }
      }

      // 创建Blob对象
      const blob = new Blob([response.data], {
        type: response.response.headers.get('content-type') || 'application/octet-stream'
      });

      // 创建下载链接并触发下载
      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();

      // 清理
      window.URL.revokeObjectURL(downloadUrl);
      document.body.removeChild(link);

      message.success('导出成功');

      // 导出成功后，清空选择
      setSelectedRowKeys([]);
    } catch (error) {
      console.error('导出失败:', error);
      message.error('导出失败');
    } finally {
      setExportLoading(false);
    }
  };

  /**
   * 打开导入弹窗
   */
  const handleShowImportModal = () => {
    setImportModalVisible(true);
    setFileList([]);
    importForm.resetFields();
    fetchDatabaseList();
  };

  /**
   * 处理文件上传变更
   */
  const handleFileChange = (info: any) => {
    // 只保留最后一个文件
    const fileList = info.fileList.slice(-1);

    // 如果用户尝试上传多个文件，提示只能上传一个
    if (info.fileList.length > 1) {
      message.info('只能上传一个文件，系统将保留最新上传的文件');
    }

    setFileList(fileList);

    // 文件状态变化处理
    const file = fileList[0];
    if (file && file.status === 'done') {
      message.success(`${file.name} 上传成功`);
    } else if (file && file.status === 'error') {
      message.error(`${file.name} 上传失败`);
    }

    // 更新表单字段值
    importForm.setFieldsValue({ uploadFile: fileList });
  };

  /**
   * 处理导入表单提交
   */
  const handleImportSubmit = async () => {
    if (!selectDomainId) {
      message.warning('请先选择领域');
      return;
    }

    try {
      await importForm.validateFields();

      if (fileList.length === 0) {
        message.error('请选择上传文件');
        return;
      }

      setImportLoading(true);

      const formData = new FormData();
      formData.append('domainId', String(selectDomainId));
      formData.append('databaseId', importForm.getFieldValue('databaseId'));
      formData.append('data', fileList[0].originFileObj);

      const response = await request.post('/api/sync_data/transmission/import', {
        data: formData,
        requestType: 'form'
      });

      setImportLoading(false);

      if (response.code === 200) {
        message.success('导入成功');
        setImportModalVisible(false);
        queryDataSetList(); // 重新加载数据集列表
        // 导入成功后会重新加载列表，已在queryDataSetList中清空选择
      } else {
        message.error(response.msg || '导入失败');
      }
    } catch (error) {
      setImportLoading(false);
      console.error('导入失败:', error);
      message.error('导入失败');
    }
  };

  const columnsConfig = ColumnsConfig();

  const columns: ProColumns[] = [
    {
      dataIndex: 'id',
      title: 'ID',
      width: 80,
      search: false,
    },
    {
      dataIndex: 'name',
      title: '数据集名称',
      search: false,
      render: (name, record) => {
        return (
          <a
            onClick={() => {
              toDatasetEditPage(record.domainId, record.id, 'relation');
            }}
          >
            {name}
          </a>
        );
      },
    },
    {
      dataIndex: 'bizName',
      title: '英文名称',
      search: false,
    },
    {
      dataIndex: 'status',
      title: '状态',
      search: false,
      render: columnsConfig.state.render,
    },
    {
      dataIndex: 'createdBy',
      title: '创建人',
      search: false,
    },
    {
      dataIndex: 'description',
      title: '描述',
      search: false,
    },
    {
      dataIndex: 'updatedAt',
      title: '更新时间',
      search: false,
      render: (value: any) => {
        return value && value !== '-' ? moment(value).format('YYYY-MM-DD HH:mm:ss') : '-';
      },
    },
  ];

  if (!disabledEdit) {
    columns.push({
      title: '操作',
      dataIndex: 'x',
      valueType: 'option',
      width: 250,
      render: (_, record) => {
        return (
          <Space className={styles.ctrlBtnContainer}>
            <a
              key="metricEditBtn"
              onClick={() => {
                toDatasetEditPage(record.domainId, record.id);
              }}
            >
              编辑
            </a>
            <a
              key="searchEditBtn"
              onClick={() => {
                setViewItem(record);
                setSearchModalOpen(true);
              }}
            >
              查询设置
            </a>
            {record.status === StatusEnum.ONLINE ? (
              <Button
                type="link"
                key="editStatusOfflineBtn"
                onClick={() => {
                  updateViewStatus({
                    ...record,
                    status: StatusEnum.OFFLINE,
                  });
                }}
              >
                停用
              </Button>
            ) : (
              <Button
                type="link"
                key="editStatusOnlineBtn"
                onClick={() => {
                  updateViewStatus({
                    ...record,
                    status: StatusEnum.ONLINE,
                  });
                }}
              >
                启用
              </Button>
            )}
            <Popconfirm
              title="确认删除？"
              okText="是"
              cancelText="否"
              onConfirm={async () => {
                const { code, msg } = await deleteView(record.id);
                if (code === 200) {
                  queryDataSetList();
                } else {
                  message.error(msg);
                }
              }}
            >
              <a key="modelDeleteBtn">删除</a>
            </Popconfirm>
          </Space>
        );
      },
    });
  }

  // 表格行选择配置
  const rowSelection = {
    selectedRowKeys,
    onChange: (selectedRowKeys: React.Key[]) => {
      setSelectedRowKeys(selectedRowKeys);
    },
  };

  return (
    <>
      <ProTable
        className={`${styles.classTable} ${styles.classTableSelectColumnAlignLeft}`}
        actionRef={actionRef}
        rowKey="id"
        search={false}
        columns={columns}
        loading={loading}
        dataSource={viewList}
        tableAlertRender={() => {
          return false;
        }}
        rowSelection={{
          type: 'checkbox',
          ...rowSelection,
        }}
        size="small"
        options={{ reload: false, density: false, fullScreen: false }}
        toolBarRender={() =>
          disabledEdit
            ? [<></>]
            : [
                <Button
                  key="import"
                  type="primary"
                  onClick={handleShowImportModal}
                >
                  导入
                </Button>,
                <Button
                  key="export"
                  type="primary"
                  onClick={handleExportDataSet}
                  loading={exportLoading}
                  disabled={!selectDomainId}
                >
                  {selectedRowKeys.length > 0 ? `导出选中(${selectedRowKeys.length})` : '导出全部'}
                </Button>,
                <Button
                  key="create"
                  type="primary"
                  onClick={() => {
                    setViewItem(undefined);
                    setCreateDataSourceModalOpen(true);
                  }}
                >
                  创建数据集
                </Button>,
              ]
        }
      />

      {/* 导入弹窗 */}
      <Modal
        title="导入数据源"
        open={importModalVisible}
        onOk={handleImportSubmit}
        onCancel={() => setImportModalVisible(false)}
        confirmLoading={importLoading}
        maskClosable={false}
        destroyOnClose
      >
        <Form form={importForm} layout="vertical">
          <Form.Item
            label="选择数据源"
            name="databaseId"
            rules={[{ required: true, message: '请选择数据源' }]}
          >
            <Select
              placeholder="请选择数据源"
              loading={uploading}
              showSearch
              optionFilterProp="children"
            >
              {databaseList.map((db) => (
                <Select.Option key={db.id} value={db.id}>
                  {db.name}
                </Select.Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item
            label="上传文件"
            name="uploadFile"
            rules={[{ required: true, message: '请上传文件' }]}
            valuePropName="fileList"
            getValueFromEvent={(e) => {
              if (Array.isArray(e)) {
                return e;
              }
              return e?.fileList;
            }}
          >
            <Dragger
              name="file"
              accept=".json"
              maxCount={1}
              fileList={fileList}
              onChange={(info) => {
                handleFileChange(info);
                // 更新表单字段值
                importForm.setFieldsValue({ uploadFile: info.fileList.slice(-1) });
              }}
              beforeUpload={(file) => {
                const isJSON = file.type === 'application/json' || file.name.endsWith('.json');
                if (!isJSON) {
                  message.error('只能上传 JSON 文件!');
                }
                return false;
              }}
              onRemove={() => {
                setFileList([]);
                // 清空表单字段值
                importForm.setFieldsValue({ uploadFile: [] });
                return true;
              }}
              multiple={false}
            >
              <p className="ant-upload-drag-icon">
                <InboxOutlined />
              </p>
              <p className="ant-upload-text">点击或拖拽文件到此区域上传</p>
              <p className="ant-upload-hint">
                <strong>仅支持上传单个 .json 格式文件</strong>
                {fileList.length > 0 && <span style={{ color: '#ff4d4f' }}> (最多上传1个文件)</span>}
              </p>
            </Dragger>
          </Form.Item>
        </Form>
      </Modal>

      {createDataSourceModalOpen && (
        <ViewCreateFormModal
          step={editFormStep}
          domainId={selectDomainId as number}
          viewItem={viewItem}
          modelList={modelList}
          onSubmit={() => {
            queryDataSetList();
            setCreateDataSourceModalOpen(false);
          }}
          onCancel={() => {
            setCreateDataSourceModalOpen(false);
          }}
        />
      )}

      {searchModalOpen && (
        <ViewSearchFormModal
          domainId={selectDomainId as number}
          viewItem={viewItem}
          onSubmit={() => {
            queryDataSetList();
            setSearchModalOpen(false);
          }}
          onCancel={() => {
            setSearchModalOpen(false);
          }}
        />
      )}
    </>
  );
};
export default DataSetTable;
