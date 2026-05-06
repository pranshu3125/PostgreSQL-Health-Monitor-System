import { useQuery } from '@tanstack/react-query'
import { metricsApi, alertsApi } from '../services/api'
import { AlertTriangle, Database, Activity } from 'lucide-react'

export default function Dashboard() {
  const { data: metrics } = useQuery({
    queryKey: ['metrics'],
    queryFn: metricsApi.getCurrent,
    refetchInterval: 30000,
  })

  const { data: alertSummary } = useQuery({
    queryKey: ['alertSummary'],
    queryFn: alertsApi.getSummary,
    refetchInterval: 30000,
  })

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Dashboard</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <div className="p-3 bg-blue-100 rounded-lg">
              <Activity className="w-6 h-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-500">System Status</p>
              <p className="text-xl font-semibold text-green-600">Healthy</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <div className="p-3 bg-yellow-100 rounded-lg">
              <AlertTriangle className="w-6 h-6 text-yellow-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-500">Active Alerts</p>
              <p className="text-xl font-semibold">{alertSummary?.active || 0}</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <div className="p-3 bg-green-100 rounded-lg">
              <Database className="w-6 h-6 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-500">Total Alerts</p>
              <p className="text-xl font-semibold">{alertSummary?.total || 0}</p>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-lg font-semibold mb-4">Metrics Overview</h2>
          <div className="space-y-3">
            <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
              <span className="text-sm font-medium">postgres_db_idle_connection</span>
              <span className="text-sm text-gray-500">Idle connections count</span>
            </div>
            <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
              <span className="text-sm font-medium">postgres_db_name_sizes</span>
              <span className="text-sm text-gray-500">Database sizes</span>
            </div>
            <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
              <span className="text-sm font-medium">postgres_connections_per_db</span>
              <span className="text-sm text-gray-500">Connections per database</span>
            </div>
            <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
              <span className="text-sm font-medium">postgres_db_query_latency</span>
              <span className="text-sm text-gray-500">Query latency metrics</span>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-lg font-semibold mb-4">Alert Summary</h2>
          <div className="space-y-3">
            <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
              <span className="text-sm font-medium">Active</span>
              <span className="text-sm text-yellow-600 font-semibold">{alertSummary?.active || 0}</span>
            </div>
            <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
              <span className="text-sm font-medium">Acknowledged</span>
              <span className="text-sm text-blue-600 font-semibold">{alertSummary?.acknowledged || 0}</span>
            </div>
            <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
              <span className="text-sm font-medium">Resolved</span>
              <span className="text-sm text-green-600 font-semibold">{alertSummary?.resolved || 0}</span>
            </div>
          </div>
        </div>
      </div>

      <div className="mt-6 bg-white p-6 rounded-lg shadow">
        <h2 className="text-lg font-semibold mb-4">Raw Metrics Data</h2>
        <pre className="bg-gray-900 text-green-400 p-4 rounded-lg overflow-x-auto text-xs">
          {metrics?.data || 'No metrics available'}
        </pre>
      </div>
    </div>
  )
}
