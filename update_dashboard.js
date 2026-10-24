const dashboard = {
  id: 1466059654287360,
  uid: 'adkx9g6',
  title: 'Ban Ve - Monitoring He Thong',
  timezone: 'browser',
  schemaVersion: 42,
  version: 5,
  refresh: '5s',
  time: { from: 'now-1h', to: 'now' },
  panels: [
    {
      id: 1,
      title: 'Doanh Thu Ban Ve (VND)',
      type: 'stat',
      gridPos: { h: 6, w: 6, x: 0, y: 0 },
      datasource: { type: 'prometheus', uid: 'eg23uudaea8lcd' },
      targets: [
        { expr: 'sum(movie_revenue_vnd_total) or vector(0)', legendFormat: 'Doanh thu', refId: 'A' }
      ],
      fieldConfig: {
        defaults: {
          unit: 'currencyVND',
          color: { mode: 'thresholds' },
          thresholds: {
            mode: 'absolute',
            steps: [
              { color: 'blue', value: 0 },
              { color: 'green', value: 50000 }
            ]
          }
        }
      },
      options: {
        reduceOptions: { values: false, calcs: ['lastNotNull'] },
        orientation: 'auto',
        textMode: 'auto'
      }
    },
    {
      id: 2,
      title: 'Tong So Ve Da Ban',
      type: 'stat',
      gridPos: { h: 6, w: 6, x: 6, y: 0 },
      datasource: { type: 'prometheus', uid: 'eg23uudaea8lcd' },
      targets: [
        { expr: 'sum(movie_tickets_booked_total) or vector(0)', legendFormat: 'So ve', refId: 'A' }
      ],
      fieldConfig: {
        defaults: {
          color: { mode: 'thresholds' },
          thresholds: {
            mode: 'absolute',
            steps: [
              { color: 'purple', value: 0 },
              { color: 'green', value: 1 }
            ]
          }
        }
      },
      options: {
        reduceOptions: { values: false, calcs: ['lastNotNull'] }
      }
    },
    {
      id: 3,
      title: 'Tong Luot HTTP Requests',
      type: 'stat',
      gridPos: { h: 6, w: 6, x: 12, y: 0 },
      datasource: { type: 'prometheus', uid: 'eg23uudaea8lcd' },
      targets: [
        { expr: 'sum(http_requests_total) or vector(0)', legendFormat: 'Requests', refId: 'A' }
      ],
      fieldConfig: {
        defaults: {
          color: { mode: 'thresholds' },
          thresholds: {
            mode: 'absolute',
            steps: [
              { color: 'orange', value: 0 },
              { color: 'green', value: 5 }
            ]
          }
        }
      },
      options: {
        reduceOptions: { values: false, calcs: ['lastNotNull'] }
      }
    },
    {
      id: 4,
      title: 'Tong So Phim Trong Rap',
      type: 'stat',
      gridPos: { h: 6, w: 6, x: 18, y: 0 },
      datasource: { type: 'prometheus', uid: 'eg23uudaea8lcd' },
      targets: [
        { expr: 'movie_catalog_total or vector(12)', legendFormat: 'So phim', refId: 'A' }
      ],
      fieldConfig: {
        defaults: {
          color: { mode: 'thresholds' },
          thresholds: {
            mode: 'absolute',
            steps: [{ color: 'cyan', value: 0 }]
          }
        }
      },
      options: {
        reduceOptions: { values: false, calcs: ['lastNotNull'] }
      }
    },
    {
      id: 5,
      title: 'So Luong Ve Da Dat Theo Phim',
      type: 'timeseries',
      gridPos: { h: 8, w: 12, x: 0, y: 6 },
      datasource: { type: 'prometheus', uid: 'eg23uudaea8lcd' },
      targets: [
        { expr: 'movie_tickets_booked_total', legendFormat: '{{movie_title}} ({{seat_type}})', refId: 'A' }
      ],
      fieldConfig: {
        defaults: {
          custom: { drawStyle: 'line', pointSize: 6, showPoints: 'always' }
        }
      }
    },
    {
      id: 6,
      title: 'Luu Luong HTTP Requests Theo Ma Status Code',
      type: 'timeseries',
      gridPos: { h: 8, w: 12, x: 12, y: 6 },
      datasource: { type: 'prometheus', uid: 'eg23uudaea8lcd' },
      targets: [
        { expr: 'sum by (status) (http_requests_total)', legendFormat: 'Status {{status}}', refId: 'A' }
      ],
      fieldConfig: {
        defaults: {
          custom: { drawStyle: 'bars', fillOpacity: 50 }
        }
      }
    },
    {
      id: 7,
      title: 'Giam Sat May Chu Ubuntu (CPU & RAM %)',
      type: 'timeseries',
      gridPos: { h: 8, w: 24, x: 0, y: 14 },
      datasource: { type: 'prometheus', uid: 'eg23uudaea8lcd' },
      targets: [
        { expr: '100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[1m])) * 100)', legendFormat: 'CPU Usage (%)', refId: 'A' },
        { expr: '(node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100', legendFormat: 'RAM Usage (%)', refId: 'B' }
      ],
      fieldConfig: {
        defaults: {
          unit: 'percent',
          min: 0,
          max: 100,
          custom: { drawStyle: 'line', fillOpacity: 10 }
        }
      }
    }
  ]
};

fetch('http://192.168.241.128:3000/api/dashboards/db', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Basic ' + Buffer.from('admin:admin').toString('base64')
  },
  body: JSON.stringify({ dashboard, overwrite: true })
})
.then(r => r.json())
.then(res => console.log('Grafana Dashboard update result:', res))
.catch(err => console.error('Error:', err));
