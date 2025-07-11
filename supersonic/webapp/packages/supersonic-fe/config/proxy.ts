export default {
  dev: {
    '/api/': {
      target: 'http://127.0.0.1:9080',
      // target: 'http://192.168.16.10:32513',//线上地址
      changeOrigin: true,
    },
  },
};
